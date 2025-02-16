# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines Pydantic models for action requests and responses. They typically map
to conversation messages describing which function is called, with what arguments,
and any returned output.
"""

from typing import Any

from pydantic import Field, field_validator

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_nullable_string_field,
)
from lionagi.operatives.models.field_model import FieldModel
from lionagi.utils import HashableModel, to_dict

from .utils import parse_action_request

__all__ = (
    "ActionRequestModel",
    "ActionResponseModel",
    "ACTION_REQUESTS_FIELD",
    "ACTION_RESPONSES_FIELD",
    "ACTION_REQUIRED_FIELD",
    "FUNCTION_FIELD",
    "ARGUMENTS_FIELD",
)


function_field_description = (
    "Name of the function to call from the provided `tool_schemas`. "
    "If no `tool_schemas` exist, set to None or leave blank. "
    "Never invent new function names outside what's given."
)

arguments_field_description = (
    "Dictionary of arguments for the chosen function. "
    "Use only argument names/types defined in `tool_schemas`. "
    "Never introduce extra argument names."
)

action_required_field_description = (
    "Whether this step strictly requires performing actions. "
    "If true, the requests in `action_requests` must be fulfilled, "
    "assuming `tool_schemas` are available. "
    "If false or no `tool_schemas` exist, actions are optional."
)

action_requests_field_description = (
    "List of actions to be executed when `action_required` is true. "
    "Each action must align with the available `tool_schemas`. "
    "Leave empty if no actions are needed."
)


class ActionRequestModel(HashableModel):
    """
    Captures a single action request, typically from a user or system message.
    Includes the name of the function and the arguments to be passed.
    """

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
        """
        Coerce arguments into a dictionary if possible, recursively.

        Raises:
            ValueError if the data can't be coerced.
        """
        return to_dict(
            value,
            fuzzy_parse=True,
            recursive=True,
            recursive_python_only=False,
        )

    @field_validator("function", mode="before")
    def validate_function(cls, value: str) -> str:
        """
        Ensure the function name is a valid non-empty string (if provided).
        """
        return validate_nullable_string_field(cls, value, "function", False)

    @classmethod
    def create(cls, content: str):
        """
        Attempt to parse a string (usually from a conversation or JSON) into
        one or more ActionRequestModel instances.

        If no valid structure is found, returns an empty list.
        """
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
    """
    Encapsulates a function's output after being called. Typically
    references the original function name, arguments, and the result.
    """

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


def validate_function_name(cls, value: Any) -> str | None:
    return validate_nullable_string_field(cls, value, strict=False)


def validate_arguments(cls, value: Any) -> dict:
    return to_dict(
        value,
        fuzzy_parse=True,
        suppress=True,
        recursive=True,
    )


FUNCTION_FIELD = FieldModel(
    name="function",
    default=None,
    annotation=str | None,
    title="Function",
    description=function_field_description,
    examples=["add", "multiply", "divide"],
    validator=validate_function_name,
)

ARGUMENTS_FIELD = FieldModel(
    name="arguments",
    annotation=dict | None,
    default_factory=dict,
    title="Action Arguments",
    description=arguments_field_description,
    examples=[{"num1": 1, "num2": 2}, {"x": "hello", "y": "world"}],
    validator=validate_arguments,
    validator_kwargs={"mode": "before"},
)

ACTION_REQUIRED_FIELD = FieldModel(
    name="action_required",
    annotation=bool,
    default=False,
    title="Action Required",
    description=action_required_field_description,
    validator=lambda cls, v: validate_boolean_field(cls, v, False),
    validator_kwargs={"mode": "before"},
)


# File: lionagi/operatives/action/request_response_model.py
