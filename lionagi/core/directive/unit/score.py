from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from .base import UnitTemplate
from .chat import Chat


class ScoreTemplate(UnitTemplate):

    template_name: str = "score_template"

    score: float = Field(
        None,
        description="a score for the given context and task, numeric",
    )

    signature: str = "task -> score"

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        score_range=(1, 10),
        include_endpoints=True,
        num_digit=0,
        confidence_score=False,
        reason=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        return_precision = ""

        if num_digit == 0:
            return_precision = "integer"
        else:
            return_precision = f"num:{to_str(num_digit)}f"

        self.task = f"""
perform scoring task according to the following constraints:
1. additional objective: {to_str(instruction or "N/A")}.
2. score range: {to_str(score_range)}.
3. include_endpoints: {"yes" if include_endpoints else "no"}.
4. precision, (max number of digits allowed after "."): {return_precision}.
5. additional information: {to_str(context or "N/A")}.
"""
        if reason:
            self.append_to_request("reason")

        if confidence_score:
            self.append_to_request("confidence_score")

        self.validation_kwargs["score"] = {
            "upper_bound": score_range[1],
            "lower_bound": score_range[0],
            "num_type": int if num_digit == 0 else float,
            "precision": num_digit if num_digit != 0 else None,
        }


class Score(Chat):

    defalut_template = ScoreTemplate

    async def score(
        self,
        context=None,
        instruction=None,
        *,
        system=None,
        sender=None,
        recipient=None,
        score_range=(0, 10),
        include_endpoints=True,
        num_digit=0,
        confidence_score=None,
        reason=False,
        requested_fields=None,
        form=None,
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

        return await self._score(
            context=context,
            instruction=instruction,
            system=system,
            sender=sender,
            recipient=recipient,
            score_range=score_range,
            include_endpoints=include_endpoints,
            num_digit=num_digit,
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

    async def _score(
        self,
        form=None,
        score_range=None,
        include_endpoints=None,
        num_digit=None,
        reason=False,
        confidence_score=None,
        **kwargs,
    ):
        if not form:
            form = self.default_template(
                score_range=score_range,
                include_endpoints=include_endpoints,
                num_digit=num_digit,
                reason=reason,
                confidence_score=confidence_score,
            )

        return await self.chat(form=form, **kwargs)
