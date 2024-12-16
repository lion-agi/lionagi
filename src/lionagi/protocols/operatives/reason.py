from pydantic import BaseModel, field_validator

from lionagi.core.models import FieldModel
from lionagi.libs.parse import to_num

from .prompts import confidence_description


def validate_confidence_score(cls, value) -> float:
    try:
        return to_num(
            value,
            upper_bound=1,
            lower_bound=0,
            num_type=float,
            precision=3,
        )
    except Exception:
        return -1


CONFIDENCE_SCORE_FIELD = FieldModel(
    name="confidence_score",
    annotation=float | None,
    default=None,
    title="Confidence Score",
    description=confidence_description,
    examples=[0.821, 0.257, 0.923, 0.439],
    validator=validate_confidence_score,
    validator_kwargs={"mode": "before"},
)


class ReasonModel(BaseModel):

    title: str | None = None
    content: str | None = None
    confidence_score: float | None = CONFIDENCE_SCORE_FIELD.field_info

    @field_validator(
        "confidence_score", **CONFIDENCE_SCORE_FIELD.validator_kwargs
    )
    def _validate_confidence(cls, v):
        return CONFIDENCE_SCORE_FIELD.validator(cls, v)


REASON_FIELD = FieldModel(
    name="reason",
    annotation=ReasonModel | None,
    default=None,
    title="Reason",
    description="**Provide a concise reason for the decision made.**",
)


__all__ = ["ReasonModel"]
