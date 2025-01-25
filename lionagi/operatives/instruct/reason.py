# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field, field_validator

from lionagi.utils import to_num

from ..models.field_model import FieldModel

__all__ = (
    "Reason",
    "REASON_FIELD",
)


# deprecated
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


# deprecated
confidence_description = (
    "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating "
    "how well you've met user expectations. Use this guide:\n"
    "  • 1.0: Highly confident\n"
    "  • 0.8-1.0: Reasonably sure\n"
    "  • 0.5-0.8: Re-check or refine\n"
    "  • 0.0-0.5: Off track"
)

# deprecated
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


class Reason(BaseModel):

    title: str | None = None
    content: str | None = None
    confidence_score: float | None = Field(
        None,
        title="Confidence Score",
        description=(
            "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating "
            "how well you've met user expectations. Use this guide:\n"
            "  • 1.0: Highly confident\n"
            "  • 0.8-1.0: Reasonably sure\n"
            "  • 0.5-0.8: Re-check or refine\n"
            "  • 0.0-0.5: Off track"
        ),
        examples=[0.821, 0.257, 0.923, 0.439],
    )

    @field_validator("confidence_score", mode="before")
    def _validate_confidence(cls, v):
        try:
            return to_num(
                v,
                upper_bound=1,
                lower_bound=0,
                num_type=float,
                precision=3,
            )
        except Exception:
            return -1


REASON_FIELD = FieldModel(
    name="reason",
    annotation=Reason | None,
    title="Reason",
    description="**Provide a concise reason for the decision made.**",
)
