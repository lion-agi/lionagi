from pydantic import Field

from lionagi.libs import func_call, convert
from ..prompt.prompt_template import ScoredTemplate
from ..branch import Branch


class ScoreTemplate(ScoredTemplate):
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
            return_precision = f"num:{convert.to_str(num_digit)}f"

        self.task = f"""
score context according to the following constraints
1. objective, {convert.to_str(instruction)}
2. score range, {convert.to_str(score_range)}
3. include_endpoints, {"yes" if inclusive else "no"}
4. format the score in {return_precision}
"""

        if reason:
            self.output_fields.append("reason")

        if confidence_score:
            self.output_fields.append("confidence_score")

        self.out_validation_kwargs['answer'] = {
            "upper_bound": score_range[1],
            "lower_bound": score_range[0],
            "num_type": int if num_digit == 0 else float,
            "precision": num_digit if num_digit != 0 else None,
        }

async def score(
    sentence,
    instruction=None,
    score_range=(1, 10),
    inclusive=True,
    num_digit=0,
    confidence_score=False,
    reason=False,
    retries=2,
    delay=0.5,
    backoff_factor=2,
    default_value=None,
    timeout=None,
    branch_name=None,
    system=None,
    messages=None,
    service=None,
    sender=None,
    llmconfig=None,
    tools=None,
    datalogger=None,
    persist_path=None,
    tool_manager=None,
    **kwargs,
):

    branch = Branch(
        name=branch_name,
        system=system,
        messages=messages,
        service=service,
        sender=sender,
        llmconfig=llmconfig,
        tools=tools,
        datalogger=datalogger,
        persist_path=persist_path,
        tool_manager=tool_manager,
    )

    _template = ScoreTemplate(
        sentence=sentence,
        instruction=instruction,
        score_range=score_range,
        inclusive=inclusive,
        num_digit=num_digit,
        confidence_score=confidence_score,
        reason=reason,
    )

    await func_call.rcall(
        branch.chat,
        prompt_template=_template,
        retries=retries,
        delay=delay,
        backoff_factor=backoff_factor,
        default=default_value,
        timeout=timeout,
        **kwargs,
    )

    return _template
