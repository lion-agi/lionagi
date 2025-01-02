# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import JsonValue

from lionagi.libs.validate.validate_boolean import validate_boolean

from ..models.field_model import FieldModel
from .prompts import (
    actions_field_description,
    context_field_description,
    guidance_field_description,
    instruction_field_description,
    reason_field_description,
)

__all__ = (
    "INSTRUCTION_FIELD",
    "GUIDANCE_FIELD",
    "CONTEXT_FIELD",
    "REASON_FIELD",
    "ACTIONS_FIELD",
)


def validate_instruction(cls, value) -> JsonValue | None:
    """Validates that the instruction is not empty or None and is in the correct format.

    Args:
        cls: The validator class method.
        value (JsonValue | None): The instruction value to validate.

    Returns:
        JsonValue | None: The validated instruction or None if invalid.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return value


def validate_boolean_field(cls, value) -> bool | None:
    """Validates boolean fields, allowing for flexible input formats.

    Args:
        cls: The validator class method.
        value: The value to validate as boolean.

    Returns:
        bool | None: The validated boolean value or None if invalid.
    """
    try:
        return validate_boolean(value)
    except Exception:
        return None


# Field Models
INSTRUCTION_FIELD = FieldModel(
    name="instruction",
    annotation=JsonValue | None,
    default=None,
    title="Primary Instruction",
    description=instruction_field_description,
    validator=validate_instruction,
    validator_kwargs={"mode": "before"},
)

GUIDANCE_FIELD = FieldModel(
    name="guidance",
    annotation=JsonValue | None,
    default=None,
    title="Execution Guidance",
    description=guidance_field_description,
)

CONTEXT_FIELD = FieldModel(
    name="context",
    annotation=JsonValue | None,
    default=None,
    title="Task Context",
    description=context_field_description,
)

REASON_FIELD = FieldModel(
    name="reason",
    annotation=bool,
    default=False,
    title="Include Reasoning",
    description=reason_field_description,
    validator=validate_boolean_field,
    validator_kwargs={"mode": "before"},
)

ACTIONS_FIELD = FieldModel(
    name="actions",
    annotation=bool,
    default=False,
    title="Require Actions",
    description=actions_field_description,
    validator=validate_boolean_field,
    validator_kwargs={"mode": "before"},
)
