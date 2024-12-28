# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, field_validator

from lionagi.core.models import FieldModel
from lionagi.libs.parse import to_num

from ..operatives.prompts import confidence_description


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
    default=None,
    title="Reason",
    description="**Provide a concise reason for the decision made.**",
)


__all__ = ["Reason"]
