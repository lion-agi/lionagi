from enum import Enum
from lionagi.libs.ln_convert import to_str

from ..generic.abc import Field
from ..report.form import Form
from ..message.action_request import ActionRequest


class ScoreTemplate(Form):

    template_name: str = "default_score"
    sentence: str | list | dict = Field(
        default_factory=str, description="the given context to score"
    )
    answer: float = Field(default_factory=float, description=f"a numeric score")
    signature: str = "sentence -> answer"

    def __init__(
        self,
        sentence=None,
        instruction=None,
        score_range=(1, 10),
        inclusive=True,
        num_digit=0,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence

        return_precision = ""
        if num_digit == 0:
            return_precision = "integer"
        else:
            return_precision = f"num:{to_str(num_digit)}f"

        self.task = f"""
score context according to the following constraints
1. objective, {to_str(instruction)}
2. score range, {to_str(score_range)}
3. include_endpoints, {"yes" if inclusive else "no"}
4. format the score in {return_precision}
"""

        if reason:
            self.requested_fields.append("reason")

        if confidence_score:
            self.requested_fields.append("confidence_score")

        self.out_validation_kwargs["answer"] = {
            "upper_bound": score_range[1],
            "lower_bound": score_range[0],
            "num_type": int if num_digit == 0 else float,
            "precision": num_digit if num_digit != 0 else None,
        }


class PlanTemplate(Form):
    template_name: str = "default_plan"
    sentence: str | list | dict = Field(
        default_factory=str,
        description="the given sentence(s) or context to generate a plan for",
    )
    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )
    signature: str = "sentence -> plan"

    def __init__(
        self,
        sentence=None,
        instruction=None,
        confidence_score=False,
        reason=False,
        num_step=3,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.task = f"Generate a {num_step}_step plan based on the given context. Instruction: {instruction}."

        if reason:
            self.requested_fields.append("reason")

        if confidence_score:
            self.requested_fields.append("confidence_score")


class PredictTemplate(Form):

    template_name: str = "default_predict"
    sentence: str | list | dict = Field(
        default_factory=str, description="the given sentence(s) to predict"
    )
    num_sentences: int = Field(
        default_factory=int, description="the number of sentences to predict"
    )
    answer: str | list = Field(
        default_factory=str, description="the predicted sentence(s) or desired output"
    )
    signature: str = "sentence -> answer"

    def __init__(
        self,
        sentence=None,
        instruction=None,
        num_sentences=1,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.sentence = sentence or ""
        self.num_sentences = num_sentences
        self.task = f"follow instruction to predict the next {self.num_sentences} sentence(s). Instruction: {instruction}."

        if reason:
            self.requested_fields.append("reason")

        if confidence_score:
            self.requested_fields.append("confidence_score")


class ReactTemplate(Form):
    template_name: str = "default_react"
    sentence: str | list | dict | None = Field(
        default_factory=str,
        description="the given sentence(s) to reason and take actions on",
    )

    def __init__(
        self,
        sentence=None,
        instruction=None,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.task = f"Think step by step. Perform reasoning and prepare actions with given tools only.Instruction: {instruction}. Absolutely DO NOT MAKE UP FUNCTIONS !!!"

        if confidence_score:
            self.requested_fields.append("confidence_score")


class ActionForm(Form):

    action_needed: bool | None = Field(
        False, description="true if actions are needed else false"
    )

    actions: list[dict | ActionRequest] | None = Field(
        default_factory=list,
        description="""provide The list of action(s) to take, each action in {"function": function_name, "arguments": {param1:..., param2:..., ...}}. Leave blank if no further actions are needed, you must use provided parameters for each action, DO NOT MAKE UP KWARG NAME!!!""",
    )

    answer: str | dict | None = Field(
        default_factory=str,
        description="output answer to the questions asked if further actions are not needed, leave blank if an accurate answer cannot be provided from context during this step",
    )

    signature: str = "sentence -> reason, action_needed, actions, answer"


class ScoredForm(Form):
    confidence_score: float | None = Field(
        -1,
        description="a numeric score between 0 to 1 formatted in num:0.2f",
    )
    reason: str | None = Field(
        default_factory=str, description="brief reason for the given output"
    )


class SelectTemplate(ScoredForm):

    template_name: str = "default_select"
    sentence: str | list | dict = Field(
        default_factory=str, description="the given context"
    )
    answer: Enum | str = Field(
        default_factory=str, description="selection from given choices"
    )
    choices: list = Field(default_factory=list, description="the given choices")

    signature: str = "sentence -> answer"

    def __init__(
        self,
        sentence=None,
        choices=None,
        instruction=None,
        reason=False,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.sentence = sentence
        self.choices = choices
        self.task = f"select 1 item, from provided choices {choices}."
        if instruction:
            self.task += f"objetive {instruction}."

        if reason:
            self.requested_fields.append("reason")

        if confidence_score:
            self.requested_fields.append("confidence_score")
