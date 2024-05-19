from enum import Enum
from lionagi.libs.ln_convert import to_str
from lionagi.core.collections.abc import Field
from .template.base import BaseUnitForm


class UnitForm(BaseUnitForm):
    """Form for managing unit directives and outputs."""

    actions: dict | None = Field(
        None,
        description=(
            "Actions to take. {action_n: {function: ..., arguments: {'param1':..., 'param2':...}}}"
            "Leave blank if no actions are needed."
            "must use provided functions and parameters, DO NOT MAKE UP NAMES!!!"
            "Flag `action_required` as True if filled."
            "When providing parameters, you must follow the provided type and format, "
            "if the parameter is a number, you should provide a number like 1, 2, or 1.1 if float is allowed."
        )
    )

    action_required: bool | None = Field(
        None,
        description="Set to True if actions are required. Provide actions if True."
    )

    answer: str | None = Field(
        None,
        description=(
            "Provide the answer to the questions asked. If an accurate answer cannot "
            "be provided at this step, set `extend_required` to True and reply with 'PLEASE_EXTEND'."
        )
    )

    extension_required: bool | None = Field(
        None,
        description=(
            "Set to True if more steps are needed to provide an accurate answer. If "
            "True, additional rounds are allowed."
        )
    )

    prediction: None | str = Field(
        None,
        description="Provide the desired prediction based on context and instruction."
    )

    plan: dict | str | None = Field(
        None,
        description=(
            "Provide a step-by-step plan. Format: {step_n: {plan: ..., reason: ...}}. "
            "Achieve the final answer at the last step. Set `extend_required` to True "
            "if providing a plan."
        )
    )

    score: float | None = Field(
        None,
        description=(
            "Provide a numeric score. Higher is better. If not otherwise instructed,"
            " fill this field with your own performance rating."
        )
    )

    selection: Enum | str | list | None = Field(
        None,
        description="Provide a selection from the given choices."
    )

    assignment: str = "task -> answer"

    def __init__(
        self,
        instruction=None,
        *,
        context=None,
        reason: bool = False,
        predict: bool = False,
        score=None,
        select=None,
        plan=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.task = (
            f"Follow the prompt and provide the necessary output.\n"
            f"- Additional instruction: {to_str(instruction or 'N/A')}\n"
            f"- Additional context: {to_str(context or 'N/A')}\n"
        )

        if reason:
            self.append_to_request("reason")

        if allow_action:
            self.append_to_request("actions, action_required, reason")
            
            self.task += (
                "- Perform reasoning and prepare actions with GIVEN TOOLS ONLY.\n"
            )
            
        if plan:
            plan_num_step=plan_num_step or 3
            max_extension = max_extension or plan_num_step
            allow_extension = True
            self.append_to_request("plan")
            self.task += (
                f"- Generate a {plan_num_step}-step plan based on the context.\n"
            )

        if allow_extension:
            self.append_to_request("extension_required")
            self.task += (
                f"- Allow auto-extension for another {max_extension} rounds.\n"
            )

        if predict:
            self.append_to_request("prediction")
            self.task += (
                f"- Predict the next {predict_num_sentences or 1} sentence(s).\n"
            )

        if score:
            self.append_to_request("score")

            if score_num_digits in [0, None]:
                return_precision = "integer"
            else:
                return_precision = f"num:.{score_num_digits}f"

            score_range = score_range or [0, 10]
            score_num_digits = score_num_digits or 0

            self.validation_kwargs["score"] = {
                "upper_bound": score_range[1],
                "lower_bound": score_range[0],
                "num_type": int if score_num_digits == 0 else float,
                "precision": score_num_digits if score_num_digits != 0 else None,
            }

            self.task += (
                f"- Perform scoring according to score range: [{to_str(score_range)}] "
                f"and precision: {return_precision}.\n"
            )

        if select:
            self.append_to_request("selection")
            self.task += (
                f"- Select 1 item from the provided choices: {select_choices}.\n"
            )

        if confidence:
            self.append_to_request("confidence_score")
