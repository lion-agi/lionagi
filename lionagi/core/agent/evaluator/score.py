from lionagi.libs.ln_convert import to_str
from lionagi.core.generic.abc import Field
from ...directive.unit.unit_mixin import Chat
from lionagi.core.report.form import Form


class ScoreTemplate(Form):

    confidence_score: float | None = Field(
        None,
        description="a numeric score between 0 to 1 formatted in num:0.2f, 1 being very confident and 0 being not confident at all, just guessing",
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(
        None,
        description="brief reason for the given output, format: This is my best response because ...",
    )

    template_name: str = "score_template"

    score: float | None = Field(
        None,
        description="a score for the given context and task, numeric",
    )

    assignment: str = "task -> score"

    @property
    def answer(self):
        return getattr(self, "score", None)

    def __init__(
        self,
        *,
        instruction=None,
        context=None,
        score_range=(0, 10),
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

    async def _score(
        self,
        form=None,
        score_range=None,
        include_endpoints=None,
        num_digit=None,
        reason=False,
        confidence_score=None,
        instruction=None,
        context=None,
        branch=None,
        system=None,
        **kwargs,
    ):
        if not form:
            form = self.default_template(
                score_range=score_range,
                include_endpoints=include_endpoints,
                num_digit=num_digit,
                reason=reason,
                confidence_score=confidence_score,
                instruction=instruction,
                context=context,
                system=system,
            )

        directive = Chat(branch)
        return await directive.chat(form=form, return_form=True, **kwargs)

    async def score(self, *args, **kwargs):
        return await self._score(*args, **kwargs)

    async def direct(self, *args, **kwargs):
        return await self._score(*args, **kwargs)
