import logging
from typing import Any

from lionfuncs import validate_boolean, validate_str
from pydantic import BaseModel, Field, field_validator

from .action_model import ActionModel
from .reason_model import ReasonModel


class StepModel(BaseModel):
    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the step.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="Describe the content of the step in detail.",
    )
    reason: ReasonModel = Field(
        ...,
        title="Reason",
        description="Provide the reasoning behind this step, including supporting details.",
    )
    action_required: bool = Field(
        False,
        title="Action Required",
        description=(
            "Indicate whether this step requires an action. Set to **True** if an "
            "action is required; otherwise, set to **False**."
        ),
    )
    actions: list[ActionModel] = Field(
        [],
        title="Actions",
        description=(
            "List of actions to be performed if `action_required` is **True**. Leave "
            "empty if no action is required. **When providing actions, you must "
            "choose from the provided `tool_schema`. Do not invent function or "
            "argument names.**"
        ),
    )

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")

    @field_validator("action_required", mode="before")
    def validate_action_required(cls, value: Any) -> bool:
        try:
            return validate_boolean(value)
        except Exception as e:
            logging.error(
                f"Failed to convert {value} to a boolean. Error: {e}"
            )
            return False


__all__ = ["StepModel"]
