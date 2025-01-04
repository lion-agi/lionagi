# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, field_validator

from lionagi.utils import to_num

from ..models.field_model import FieldModel


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


confidence_description = (
    "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating "
    "how well you've met user expectations. Use this guide:\n"
    "  • 1.0: Highly confident\n"
    "  • 0.8-1.0: Reasonably sure\n"
    "  • 0.5-0.8: Re-check or refine\n"
    "  • 0.0-0.5: Off track"
)

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
    confidence_score: float | None = CONFIDENCE_SCORE_FIELD.field_info

    @field_validator(
        "confidence_score", **CONFIDENCE_SCORE_FIELD.validator_kwargs
    )
    def _validate_confidence(cls, v):
        return CONFIDENCE_SCORE_FIELD.validator(cls, v)


REASON_FIELD = FieldModel(
    name="reason",
    annotation=Reason | None,
    title="Reason",
    description="**Provide a concise reason for the decision made.**",
)


__all__ = ["Reason"]
