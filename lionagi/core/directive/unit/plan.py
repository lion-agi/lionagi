from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from .base import Chat
from lionagi.core.report.form import Form


class PlanTemplate(Form):

    confidence_score: float = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str = Field(
        default_factory=str,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "plan_template"

    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )

    signature: str = "task -> plans"

    @property
    def answer(self):
        return self.plan

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


class Plan(Chat):

    defalut_template = PlanTemplate

    async def direct(
        self,
        form=None,
        num_step=None,
        reason=False,
        confidence_score=None,
        **kwargs,
    ):
        if not form:
            form = self.default_template(
                num_step=num_step,
                reason=reason,
                confidence_score=confidence_score,
            )

        return await self.chat(form=form, **kwargs)

    async def plan(self, *args, **kwargs):
        return await self.direct(*args, **kwargs)
