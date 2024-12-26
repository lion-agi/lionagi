from typing import Any

from pydantic import BaseModel, Field

from lionagi.core.models.types import FieldModel

__all__ = (
    "ActionResponseModel",
    "ACTION_RESPONSES_FIELD",
)


class ActionResponseModel(BaseModel):

    function: str = Field(default_factory=str)
    arguments: dict[str, Any] = Field(default_factory=dict)
    output: Any = None


ACTION_RESPONSES_FIELD = FieldModel(
    name="action_responses",
    annotation=list[ActionResponseModel],
    default_factory=list,
    title="Actions",
    description="**do not fill**",
)
