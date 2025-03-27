# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field, field_validator

from lionagi.models import FieldModel
from lionagi.utils import to_num

__all__ = ("Reason",)


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
            "  • 0.5-0.8: Re-check, refine or backtrack\n"
            "  • 0.0-0.5: Off track, stop"
        ),
    )

    @field_validator("confidence_score", mode="before")
    def _validate_confidence(cls, v):
        return validate_confidence_score(cls, v)


def validate_confidence_score(cls, v):
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

# File: lionagi/fields/reason.py
