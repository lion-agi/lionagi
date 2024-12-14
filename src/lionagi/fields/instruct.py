# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, ClassVar

from pydantic import JsonValue, field_validator

from lionagi.libs.parse import validate_boolean
from lionagi.protocols.models import BaseAutoModel, FieldModel

from .prompts import (
    actions_field_description,
    context_examples,
    context_field_description,
    guidance_examples,
    guidance_field_description,
    instruct_model_examples,
    instruction_examples,
    instruction_field_description,
    operation_instruct_model_examples,
    reason_field_description,
)

__all__ = (
    "Instruct",
    "OperationInstruct",
    "InstructResponse",
    "INSTRUCT_FIELD_MODEL",
    "INSTRUCTION_FIELD_MODEL",
    "GUIDANCE_FIELD_MODEL",
    "CONTEXT_FIELD_MODEL",
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
    if value is None:
        return None
    try:
        return validate_boolean(value)
    except Exception:
        return None


# Field Models
INSTRUCTION_FIELD_MODEL = FieldModel(
    name="instruction",
    annotation=JsonValue | None,
    default=None,
    title="Primary Instruction",
    description=instruction_field_description,
    examples=instruction_examples,
    validator=validate_instruction,
    validator_kwargs={"mode": "before"},
)

GUIDANCE_FIELD_MODEL = FieldModel(
    name="guidance",
    annotation=JsonValue | None,
    default=None,
    title="Execution Guidance",
    description=guidance_field_description,
    examples=guidance_examples,
)

CONTEXT_FIELD_MODEL = FieldModel(
    name="context",
    annotation=JsonValue | None,
    default=None,
    title="Task Context",
    description=context_field_description,
    examples=context_examples,
)

REASON_FIELD_MODEL = FieldModel(
    name="reason",
    annotation=bool,
    default=False,
    title="Include Reasoning",
    description=reason_field_description,
    validator=validate_boolean_field,
    validator_kwargs={"mode": "before"},
)

ACTIONS_FIELD_MODEL = FieldModel(
    name="actions",
    annotation=bool,
    default=False,
    title="Require Actions",
    description=actions_field_description,
    validator=validate_boolean_field,
    validator_kwargs={"mode": "before"},
)


class Instruct(BaseAutoModel):
    """Model for defining instruction parameters and execution requirements.

    Attributes:
        instruction (JsonValue | None): The primary instruction.
        guidance (JsonValue | None): Execution guidance.
        context (JsonValue | None): Task context.
        reason (bool): Whether to include reasoning.
        actions (bool): Whether specific actions are required.
    """

    instruction: JsonValue | None = INSTRUCTION_FIELD_MODEL.field_info
    guidance: JsonValue | None = GUIDANCE_FIELD_MODEL.field_info
    context: JsonValue | None = CONTEXT_FIELD_MODEL.field_info
    extension_required: bool = False

    @field_validator("instruction", **INSTRUCTION_FIELD_MODEL.validator_kwargs)
    def _validate_instruction(cls, v):
        """Field validator for the 'instruction' field.

        Args:
            v: The value to validate.

        Returns:
            JsonValue | None: The validated instruction value.
        """
        return INSTRUCTION_FIELD_MODEL.validator(cls, v)

    @field_validator("extension_required", mode="before")
    def _validate_extension_required(cls, v):
        """Field validator for the 'extension_required' field.

        Args:
            v: The value to validate.

        Returns:
            bool: The validated boolean value.
        """
        try:
            return validate_boolean_field(cls, v)
        except Exception:
            return False


class OperationInstruct(Instruct):

    reserved_kwargs: ClassVar[list[str]] = [
        "operative_model",
        "field_models",
        "operative",
        "reason",
        "actions",
        "request_params",
        "response_params",
    ]
    reason: bool = REASON_FIELD_MODEL.field_info
    actions: bool = ACTIONS_FIELD_MODEL.field_info

    @field_validator("reason", **REASON_FIELD_MODEL.validator_kwargs)
    def _validate_reason(cls, v):
        """Field validator for the 'reason' field.

        Args:
            v: The value to validate.

        Returns:
            bool | None: The validated boolean value.
        """
        return REASON_FIELD_MODEL.validator(cls, v)

    @field_validator("actions", **ACTIONS_FIELD_MODEL.validator_kwargs)
    def _validate_actions(cls, v):
        """Field validator for the 'actions' field.

        Args:
            v: The value to validate.

        Returns:
            bool | None: The validated boolean value.
        """
        return ACTIONS_FIELD_MODEL.validator(cls, v)


INSTRUCT_FIELD_MODEL = FieldModel(
    name="instruct_models",
    annotation=list[Instruct],
    default_factory=list,
    title="Instruction Model",
    description="Model for defining instruction parameters and execution requirements.",
    examples=instruct_model_examples,
)


OPERATION_INSTRUCT_FIELD_MODEL = FieldModel(
    name="operation_instruct_models",
    annotation=list[OperationInstruct],
    default_factory=list,
    title="Operation Instruction Model",
    description="Model for defining operation instruction parameters and execution requirements.",
    examples=operation_instruct_model_examples,
)


class InstructResponse(Instruct):
    response: Any | None = None


class OperationInstructResponse(OperationInstruct):
    response: Any | None = None
