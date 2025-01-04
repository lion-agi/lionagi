# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, ClassVar

from pydantic import JsonValue, field_validator

from lionagi.utils import HashableModel

from ..models.field_model import FieldModel
from .base import (
    ACTIONS_FIELD,
    CONTEXT_FIELD,
    GUIDANCE_FIELD,
    INSTRUCTION_FIELD,
    REASON_FIELD,
)

__all__ = (
    "Instruct",
    "InstructResponse",
    "INSTRUCT_FIELD",
    "LIST_INSTRUCT_FIELD_MODEL",
)


class Instruct(HashableModel):
    """Model for defining instruction parameters and execution requirements.

    Attributes:
        instruction (JsonValue | None): The primary instruction.
        guidance (JsonValue | None): Execution guidance.
        context (JsonValue | None): Task context.
    """

    reserved_kwargs: ClassVar[list[str]] = [
        "operative_model",
        "field_models",
        "operative",
        "reason",
        "actions",
        "request_params",
        "response_params",
    ]
    instruction: JsonValue | None = INSTRUCTION_FIELD.field_info
    guidance: JsonValue | None = GUIDANCE_FIELD.field_info
    context: JsonValue | None = CONTEXT_FIELD.field_info
    reason: bool = REASON_FIELD.field_info
    actions: bool = ACTIONS_FIELD.field_info

    @field_validator("instruction", **INSTRUCTION_FIELD.validator_kwargs)
    def _validate_instruction(cls, v):
        """Field validator for the 'instruction' field.

        Args:
            v: The value to validate.

        Returns:
            JsonValue | None: The validated instruction value.
        """
        return INSTRUCTION_FIELD.validator(cls, v)

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


INSTRUCT_FIELD = FieldModel(
    name="instruct_model",
    annotation=Instruct | None,
    default=None,
)


class InstructResponse(HashableModel):
    instruct: Instruct
    response: Any | None = None


LIST_INSTRUCT_FIELD_MODEL = FieldModel(
    name="instruct_models",
    annotation=list[Instruct] | None,
    default=None,
)
