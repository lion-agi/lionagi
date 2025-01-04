# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import Field, field_validator

from lionagi.libs.validate.common_field_validators import (
    validate_nullable_string_field,
)
from lionagi.utils import HashableModel, to_dict

from ..models.field_model import FieldModel
from .utils import (
    action_requests_field_description,
    arguments_field_description,
    function_field_description,
    parse_action_request,
)

__all__ = (
    "ActionRequestModel",
    "ACTION_REQUESTS_FIELD",
    "ActionResponseModel",
    "ACTION_RESPONSES_FIELD",
)


class ActionRequestModel(HashableModel):

    function: str | None = Field(
        None,
        title="Function",
        description=function_field_description,
        examples=["multiply", "create_user"],
    )
    arguments: dict[str, Any] | None = Field(
        None,
        title="Arguments",
        description=arguments_field_description,
    )

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            recursive=True,
            recursive_python_only=False,
        )

    @field_validator("function", mode="before")
    def validate_function(cls, value: str) -> str:
        return validate_nullable_string_field(cls, value, "function", False)

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


class ActionResponseModel(HashableModel):

    function: str = Field(default_factory=str, title="Function")
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: Any = None


ACTION_RESPONSES_FIELD = FieldModel(
    name="action_responses",
    annotation=list[ActionResponseModel],
    default_factory=list,
    title="Actions",
    description="**do not fill**",
)
