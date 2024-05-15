from lionagi.core.generic.abc import Field
from .base import UnitTemplate
from .chat import Chat


class PredictTemplate(UnitTemplate):

    template_name: str = "predict_template"

    num_sentences: int = Field(1, description="the number of sentences to predict")

    prediction: str | list = Field(
        default_factory=str, description="the predicted sentence(s) or desired output"
    )

    signature: str = "task -> prediction"

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        num_sentences=1,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.num_sentences = num_sentences

        self.task = f"""
predict the next sentence(s) according to the following constraints
1. number of sentences: {self.num_sentences}
2. additional objective , {instruction or "N/A"}
3. additional information, {context or "N/A"}
"""

        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")


class Predict(Chat):

    default_template = PredictTemplate

    async def predict(
        self,
        context=None,  # context to perform the instruction on
        instruction=None,  # additional instruction
        *,
        system=None,  # optionally swap system message
        sender=None,  # sender of the instruction, default "user"
        recipient=None,  # recipient of the instruction, default "branch.ln_id"
        num_sentences=3,  # number of sentences to generate, default 3
        confidence_score=None,
        reason=False,
        requested_fields=None,  # fields to request from the context, default None
        form=None,  # form to create instruction from, default None,
        return_form=True,  # whether to return the form if a form is passed in, otherwise return a dict/str
        strict=False,  # whether to strictly enforce the rule validation, default False
        rulebook=None,  # the rulebook to use for validation, default None, use default rulebook
        imodel=None,  # the optinally swappable iModel for the commands, otherwise self.branch.imodel
        template_name=None,
        use_annotation=True,  # whether to use annotation as rule qualifier, default True, (need rulebook if False)
        retries: int = 3,  # kwargs for rcall, number of retries if failed
        delay: float = 0,  # number of seconds to delay before retrying
        backoff_factor: float = 1,  # exponential backoff factor, default 1 (no backoff)
        default=None,  # default value to return if all retries failed
        timeout: (
            float | None
        ) = None,  # timeout for the rcall, default None (no timeout)
        timing: bool = False,  # if timing will return a tuple (output, duration)
        max_concurrency: int = 10_000,  # max concurrency for the chat, default 10_000 (global max concurrency)
        throttle_period: int = None,
        **kwargs,
    ):

        return await self._predict(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            num_sentences=num_sentences,
            confidence_score=confidence_score,
            reason=reason,
            requested_fields=requested_fields,
            form=form,
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

    async def _predict(
        self,
        form=None,
        num_sentences=None,
        reason=False,
        confidence_score=None,
        **kwargs,
    ):
        if not form:
            form = self.default_template(
                num_sentences=num_sentences,
                confidence_score=confidence_score,
                reason=reason,
            )

        form = await self.chat(form=form, return_form=True, **kwargs)

    async def direct(self, *args, **kwargs):
        return await self.predict(*args, **kwargs)
