from enum import Enum
from lionagi.core.generic.abc import Field
from .base import UnitTemplate, Chat


class SelectTemplate(UnitTemplate):

    template_name: str = "default_select"

    selection: Enum | str | list = Field(
        default_factory=str, description="selection from given choices"
    )
    choices: list = Field(default_factory=list, description="the given choices")

    signature: str = "task -> selection"

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        choices=None,
        reason=False,
        confidence_score=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.choices = choices
        self.task = f"""
select 1 item from the provided choices {choices}.        
1. additional objective: {instruction or "N/A"}.
2. additional information: {context or "N/A"}.     
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")


class Select(Chat):

    defalut_template = SelectTemplate

    async def select(
        self,
        context=None,
        instruction=None,
        *,
        system=None,
        sender=None,
        recipient=None,
        choices=None,
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
        **kwargs,
    ):

        return await self._select(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            choices=choices,
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
            **kwargs,
        )

    async def _select(
        self,
        form=None,
        choices=None,
        reason=False,
        confidence_score=None,
        **kwargs,
    ):
        if not form:
            form = self.default_template(
                choices=choices,
                reason=reason,
                confidence_score=confidence_score,
            )

        return await self.chat(form=form, **kwargs)
