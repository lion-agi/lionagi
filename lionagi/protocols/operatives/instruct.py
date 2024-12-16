"""Field definitions and validation for InstructModel components."""

from typing import Any, ClassVar

from pydantic import JsonValue, field_validator

from lionagi.core.models import FieldModel, SchemaModel
from lionagi.core.models.base import BaseAutoModel
from lionagi.libs.parse import validate_boolean

from .prompts import (
    actions_field_description,
    context_examples,
    context_field_description,
    guidance_examples,
    guidance_field_description,
    instruction_examples,
    instruction_field_description,
    reason_field_description,
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
    examples=instruction_examples,
    validator=validate_instruction,
    validator_kwargs={"mode": "before"},
)

GUIDANCE_FIELD = FieldModel(
    name="guidance",
    annotation=JsonValue | None,
    default=None,
    title="Execution Guidance",
    description=guidance_field_description,
    examples=guidance_examples,
)

CONTEXT_FIELD = FieldModel(
    name="context",
    annotation=JsonValue | None,
    default=None,
    title="Task Context",
    description=context_field_description,
    examples=context_examples,
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


class Instruct(SchemaModel):
    """Model for defining instruction parameters and execution requirements.

    Attributes:
        instruction (JsonValue | None): The primary instruction.
        guidance (JsonValue | None): Execution guidance.
        context (JsonValue | None): Task context.
        reason (bool): Whether to include reasoning.
        actions (bool): Whether specific actions are required.
    """

    instruction: JsonValue | None = INSTRUCTION_FIELD.field_info
    guidance: JsonValue | None = GUIDANCE_FIELD.field_info
    context: JsonValue | None = CONTEXT_FIELD.field_info

    @field_validator("instruction", **INSTRUCTION_FIELD.validator_kwargs)
    def _validate_instruction(cls, v):
        """Field validator for the 'instruction' field.

        Args:
            v: The value to validate.

        Returns:
            JsonValue | None: The validated instruction value.
        """
        return INSTRUCTION_FIELD.validator(cls, v)


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
    reason: bool = REASON_FIELD.field_info
    actions: bool = ACTIONS_FIELD.field_info

    @field_validator("reason", **REASON_FIELD.validator_kwargs)
    def _validate_reason(cls, v):
        """Field validator for the 'reason' field.

        Args:
            v: The value to validate.

        Returns:
            bool | None: The validated boolean value.
        """
        return REASON_FIELD.validator(cls, v)

    @field_validator("actions", **ACTIONS_FIELD.validator_kwargs)
    def _validate_actions(cls, v):
        """Field validator for the 'actions' field.

        Args:
            v: The value to validate.

        Returns:
            bool | None: The validated boolean value.
        """
        return ACTIONS_FIELD.validator(cls, v)


INSTRUCT_MODEL_FIELD = FieldModel(
    name="instruct_models",
    annotation=list[Instruct],
    default_factory=list,
    title="Instruction Model",
    description="Model for defining instruction parameters and execution requirements.",
)


class InstructResponse(BaseAutoModel):
    instruct: Instruct
    response: Any | None = None


# Export all components
__all__ = [
    "INSTRUCTION_FIELD",
    "GUIDANCE_FIELD",
    "CONTEXT_FIELD",
    "REASON_FIELD",
    "ACTIONS_FIELD",
    "Instruct",
    "INSTRUCT_MODEL_FIELD",
    "InstructResponse",
]
