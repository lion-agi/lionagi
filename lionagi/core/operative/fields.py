from typing import Any

from pydantic import Field

from .models import ActionRequestModel, ActionResponseModel, ReasonModel

REASON_FIELD: ReasonModel | None = Field(None)

ACTION_REQUESTS_FIELD: list[ActionRequestModel] = Field(
    [],
    title="Actions",
    description=(
        "List of actions to be performed if `action_required` is **True**. Leave "
        "empty if no action is required. **When providing actions, you must "
        "choose from the provided `tool_schemas`. Do not invent function or "
        "argument names.**"
    ),
)

ACTION_RESPONSES_FIELD: list[ActionResponseModel] = []

ACTION_REQUIRED_FIELD: bool = Field(
    False,
    title="Action Required",
    description=(
        "if there are no tool_schemas provied, must mark as **False**. "
        "Indicate whether this step requires an action. Set to **True** if an "
        "action is required; otherwise, set to **False**."
    ),
)

RESPONSE_FIELD: Any = Field(None)
