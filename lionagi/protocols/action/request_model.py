from typing import Any

from pydantic import BaseModel, field_validator

from lionagi.core.models.types import FieldModel
from lionagi.libs.parse import to_dict

from .base import (
    ARGUMENTS_FIELD,
    FUNCTION_FIELD,
    action_requests_field_description,
)
from .utils import parse_action_request

__all__ = (
    "ActionRequestModel",
    "ACTION_REQUEST_FIELD",
    "ACTION_REQUESTS_FIELD",
)


class ActionRequestModel(BaseModel):

    function: str | None = FUNCTION_FIELD.field_info
    arguments: dict[str, Any] | None = ARGUMENTS_FIELD.field_info

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            recursive=True,
            recursive_python_only=False,
        )

    @classmethod
    def create(cls, content: str):
        try:
            content = parse_action_request(content)
            if content:
                return [cls.model_validate(i) for i in content]
            return []
        except Exception:
            return []


ACTION_REQUEST_FIELD = FieldModel(
    name="action_request",
    annotation=ActionRequestModel | None,
    default=None,
    title="Action",
    description="**do not fill**",
)

ACTION_REQUESTS_FIELD = FieldModel(
    name="action_requests",
    annotation=list[ActionRequestModel],
    default_factory=list,
    title="Actions",
    description=action_requests_field_description,
)
