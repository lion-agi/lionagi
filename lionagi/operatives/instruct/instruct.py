# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, ClassVar, Literal

from pydantic import ConfigDict, Field, JsonValue, field_validator

from lionagi.libs.validate.common_field_validators import (
    validate_boolean_field,
    validate_nullable_jsonvalue_field,
)
from lionagi.utils import HashableModel, to_num

from ..models.field_model import FieldModel

__all__ = (
    "Instruct",
    "InstructResponse",
    "INSTRUCT_FIELD",
    "LIST_INSTRUCT_FIELD",
    "CHAT_FIELD",
    "OPERATE_FIELD",
)


class Instruct(HashableModel):

    reserved_kwargs: ClassVar[set[str]] = {
        "reason",
        "actions",
        "action_strategy",
        "action_batch_size",
        "extension_allowed",
        "max_extensions",
    }

    model_config = ConfigDict(
        json_schema_extra={
            "description": """
Request options for a Branch to perform an instruction
- instruction is typically required
- if extension is needed, the Branch will execute a ReAct
- if reason/action is needed, the Branch will execute an operate
- else, the Branch will perform a communicate operation
"""
        }
    )

    instruction: JsonValue | None = Field(
        None,
        title="Primary Instruction",
        description=(
            "A clear, actionable task definition. Specify:\n"
            "1) The primary goal or objective\n"
            "2) Key success criteria or constraints\n"
            "\n"
            "Guidelines:\n"
            "- Start with a direct action verb (e.g., 'Analyze', 'Generate', 'Create')\n"
            "- Include scope, boundaries, or constraints\n"
            "- Provide success criteria if relevant\n"
            "- For complex tasks, break them into logical steps"
        ),
    )
    guidance: JsonValue | None = Field(
        None,
        title="Guidance",
        description=(
            "Strategic direction and constraints for executing the task. "
            "Include:\n"
            "1) Preferred methods or frameworks\n"
            "2) Quality benchmarks (e.g., speed, clarity)\n"
            "3) Resource or environmental constraints\n"
            "4) Relevant compliance or standards\n"
            "Use None if no special guidance."
        ),
    )
    context: JsonValue | None = Field(
        None,
        description=(
            "Background information and current-state data needed for the task. "
            "Should be:\n"
            "1) Directly relevant\n"
            "2) Sufficient to perform the task\n"
            "3) Free of extraneous detail\n"
            "Include environment, prior outcomes, system states, or dependencies. "
            "Use None if no additional context is needed."
        ),
    )

    reason: bool | None = Field(
        None,
        description=(
            "Include a thoughtful explanation of decisions, trade-offs, "
            "and insights. Encourage deeper introspection on why certain "
            "choices were made, potential alternatives, and how confidence "
            "was shaped. If not needed, set to None."
        ),
    )
    actions: bool | None = Field(
        None,
        description=(
            "Controls execution mode. "
            "True: Execute specified actions. "
            "False: Analysis/recommendations only. "
            "None: Contextual execution."
        ),
    )
    action_strategy: Literal["batch", "sequential", "concurrent"] | None = (
        Field(
            None,
            description="Action strategy to use for executing actions. Default "
            "is 'concurrent'. Only provide for if actions are enabled.",
        )
    )
    action_batch_size: int | None = Field(
        None,
        description="Batch size for executing actions. Only provide for 'batch' strategy.",
    )
    extension_allowed: bool | None = Field(
        None,
        description="Whether to allow extensions for additional analysis or actions.",
    )
    max_extensions: int | None = Field(
        None,
        description=(
            "Maximum number of extensions allowed. If None, no extension will be performed "
            "Only provide if extension_allowed is True. Should be appropriate for the task."
            "max is 100."
        ),
    )

    @field_validator("instruction", "guidance", "context", mode="before")
    def _validate_instruction(cls, v):
        return validate_nullable_jsonvalue_field(cls, v)

    @field_validator("action_batch_size", "max_extensions", mode="before")
    def _validate_batch_size(cls, v):
        if v is None:
            return None
        try:
            return to_num(v, num_type=int)
        except Exception:
            return None

    @field_validator("reason", "actions", mode="before")
    def _validate_reason(cls, v):
        return validate_boolean_field(cls, v)

    @field_validator("action_strategy", mode="before")
    def _validate_action_strategy(cls, v):
        if v not in ["batch", "sequential", "concurrent"]:
            return "concurrent"
        return v


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
