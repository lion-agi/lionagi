# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""deprecated"""

from pydantic import JsonValue

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_nullable_jsonvalue_field,
)

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


# Field Models
INSTRUCTION_FIELD = FieldModel(
    name="instruction",
    annotation=JsonValue | None,
    default=None,
    title="Primary Instruction",
    description=instruction_field_description,
    validator=validate_nullable_jsonvalue_field,
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
    validator=lambda cls, value: validate_boolean_field(
        cls, value, default=False
    ),
    validator_kwargs={"mode": "before"},
)

ACTIONS_FIELD = FieldModel(
    name="actions",
    annotation=bool,
    default=False,
    title="Require Actions",
    description=actions_field_description,
    validator=lambda cls, value: validate_boolean_field(
        cls, value, default=False
    ),
    validator_kwargs={"mode": "before"},
)
