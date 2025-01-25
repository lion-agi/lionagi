# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any

from pydantic import BaseModel

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_nullable_string_field,
)
from lionagi.utils import to_dict, to_json, to_list

from ..models.field_model import FieldModel

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


__all__ = (
    "FUNCTION_FIELD",
    "ARGUMENTS_FIELD",
    "ACTION_REQUIRED_FIELD",
    "parse_action_request",
)


def parse_action_request(content: str | dict) -> list[dict]:

    json_blocks = []

    if isinstance(content, BaseModel):
        json_blocks = [content.model_dump()]

    elif isinstance(content, str):
        json_blocks = to_json(content, fuzzy_parse=True)
        if not json_blocks:
            pattern2 = r"```python\s*(.*?)\s*```"
            _d = re.findall(pattern2, content, re.DOTALL)
            json_blocks = [to_json(match, fuzzy_parse=True) for match in _d]
            json_blocks = to_list(json_blocks, dropna=True)

        print(json_blocks)

    elif content and isinstance(content, dict):
        json_blocks = [content]

    if json_blocks and not isinstance(json_blocks, list):
        json_blocks = [json_blocks]

    out = []

    for i in json_blocks:
        j = {}
        if isinstance(i, dict):
            if "function" in i and isinstance(i["function"], dict):
                if "name" in i["function"]:
                    i["function"] = i["function"]["name"]
            for k, v in i.items():
                k = (
                    k.replace("action_", "")
                    .replace("recipient_", "")
                    .replace("s", "")
                )
                if k in ["name", "function", "recipient"]:
                    j["function"] = v
                elif k in ["parameter", "argument", "arg", "param"]:
                    j["arguments"] = to_dict(
                        v, str_type="json", fuzzy_parse=True, suppress=True
                    )
            if (
                j
                and all(key in j for key in ["function", "arguments"])
                and j["arguments"]
            ):
                out.append(j)

    return out


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
