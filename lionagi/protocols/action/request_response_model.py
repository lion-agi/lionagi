# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import Field
from typing import Any

from pydantic import BaseModel, field_validator

from lionagi.utils import to_dict

from ..models.field_model import FieldModel
from .utils import (
    ARGUMENTS_FIELD,
    FUNCTION_FIELD,
    action_requests_field_description,
    parse_action_request,
)

__all__ = (
    "ActionRequestModel",
    "ACTION_REQUESTS_FIELD",
    "ActionResponseModel",
    "ACTION_RESPONSES_FIELD",
)


class ActionRequestModel(BaseModel):

    function: str | None = FUNCTION_FIELD.field_info
    arguments: dict[str, Any] | None = ARGUMENTS_FIELD.field_info

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            recursive=True,
            recursive_python_only=False,
        )

    @classmethod
    def create(cls, content: str):
        try:
            content = parse_action_request(content)
            if content:
                return [cls.model_validate(i) for i in content]
            return []
        except Exception:
            return []


ACTION_REQUESTS_FIELD = FieldModel(
    name="action_requests",
    annotation=list[ActionRequestModel],
    default_factory=list,
    title="Actions",
    description=action_requests_field_description,
)


class ActionResponseModel(BaseModel):

    function: str = Field(default_factory=str)
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: Any = None


ACTION_RESPONSES_FIELD = FieldModel(
    name="action_responses",
    annotation=list[ActionResponseModel],
    default_factory=list,
    title="Actions",
    description="**do not fill**",
)
