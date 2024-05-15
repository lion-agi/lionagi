from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from .base import DirectiveTemplate


class PlanTemplate(DirectiveTemplate):

    template_name: str = "plan_template"

    plan: dict | str = Field(
        default_factory=dict,
        description="the generated step by step plan, return as a dictionary following {step_n: {plan: ..., reason: ...}} format",
    )

    signature: str = "task -> plans"

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


from .chat import Chat


class Plan(Chat):

    defalut_template = PlanTemplate

    async def plan(
        self,
        context=None,
        instruction=None,
        *,
        system=None,
        sender=None,
        recipient=None,
        num_step=3,
        confidence_score=None,
        reason=False,
        requested_fields=None,
        form=None,
        tools=False,
        invoke_tool=True,
        return_form=True,
        strict=False,
        rulebook=None,
        imodel=None,
        template_name=None,
        use_annotation=True,
        retries: int = 3,
        delay: float = 0,
        backoff_factor: float = 1,
        default=None,
        timeout: float | None = None,
        timing: bool = False,
        max_concurrency: int = 10_000,
        throttle_period: int = None,
        branch=None,
        **kwargs,
    ):

        return await self._plan(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            num_step=num_step,
            confidence_score=confidence_score,
            reason=reason,
            requested_fields=requested_fields,
            form=form,
            tools=tools,
            invoke_tool=invoke_tool,
            return_form=return_form,
            strict=strict,
            rulebook=rulebook,
            imodel=imodel,
            template_name=template_name,
            use_annotation=use_annotation,
            retries=retries,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            timing=timing,
            max_concurrency=max_concurrency,
            throttle_period=throttle_period,
            branch=branch,
            **kwargs,
        )

    async def _plan(
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

    async def direct(self, *args, **kwargs):
        return await self.plan(*args, **kwargs)
