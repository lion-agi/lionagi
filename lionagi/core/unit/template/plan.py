from lionagi.libs.ln_convert import to_str

from .base import BaseUnitForm, Field


class PlanTemplate(BaseUnitForm):
    """
    A template for generating a step-by-step plan based on given instructions and context.

    Inherits from `BaseUnitForm` and adds fields and methods specific to plan generation.

    Attributes:
        template_name (str): The name of the template.
        plan (dict | str): The generated step-by-step plan in the format {step_n: {plan: ..., reason: ...}}.
        signature (str): A string representing the task signature for the plan.
    """

    template_name: str = "plan_template"

    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )

    assignment: str = "task -> plan"

    @property
    def answer(self):
        """
        Gets the plan attribute.

        Returns:
            dict | str: The generated plan.
        """
        return getattr(self, "plan", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        confidence_score=False,
        reason=False,
        num_step=3,
        **kwargs,
    ):
        """
        Initializes a new instance of the PlanTemplate class.

        Args:
            instruction (str, optional): Additional instructions for the plan.
            context (str, optional): Additional context for the plan.
            confidence_score (bool, optional): Whether to include a confidence score.
            reason (bool, optional): Whether to include a reasoning field.
            num_step (int, optional): The number of steps in the plan. Defaults to 3.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self.task = f"""
Generate a {num_step}_step plan based on the given context
1. additional instruction, {to_str(instruction or "N/A")}
2. additional context, {to_str(context or "N/A")}
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")
