import logging
from typing import Any

from lionfuncs import validate_boolean
from pydantic import Field, field_validator

from .action_model import ActionModel, ReasonActionModel
from .base import DirectiveModel
from .reason_model import ReasonModel


class StepModel(DirectiveModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the step.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the content of the step in detail.",
    )
    action_required: bool = Field(
        False,
        title="Action Required",
        description=(
            "if there are no tool_schema provied, must mark as **False**. "
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

    @field_validator("action_required", mode="before")
    def validate_action_required(cls, value: Any) -> bool:
        try:
            return validate_boolean(value)
        except Exception as e:
            logging.error(
                f"Failed to convert {value} to a boolean. Error: {e}"
            )
            return False


class ReasonStepModel(StepModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the step.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the content of the step in detail.",
    )
    action_required: bool = Field(
        False,
        title="Action Required",
        description=(
            "if there are no tool_schema provied, must mark as **False**. "
            "Indicate whether this step requires an action. Set to **True** if an "
            "action is required; otherwise, set to **False**."
        ),
    )
    actions: list[ReasonActionModel] = Field(
        [],
        title="Actions",
        description=(
            "List of actions to be performed if `action_required` is **True**. Leave "
            "empty if no action is required. **When providing actions, you must "
            "choose from the provided `tool_schema`. Do not invent function or "
            "argument names.**"
        ),
    )
    reason: ReasonModel | None = None
