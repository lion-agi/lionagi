from typing import Any

from pydantic import BaseModel, Field, field_validator

from lionagi.libs.parse import to_dict

from ...event.prompts import (
    arguments_field_description,
    function_field_description,
)
from .utils import parse_action_request_model


class ActionRequestModel(BaseModel):

    function: str | None = Field(None, description=function_field_description)

    arguments: dict | None = Field(
        default_factory=dict,
        description=arguments_field_description,
    )

    @field_validator("arguments", mode="before")
    def validate_arguments(cls, value: Any) -> dict[str, Any]:
        return to_dict(
            value,
            fuzzy_parse=True,
            suppress=True,
            recursive=True,
            recursive_python_only=False,
        )

    @classmethod
    def create(cls, content: str) -> list[BaseModel]:
        """Create request models from content string."""
        try:
            requests = parse_action_request_model(content)
            return (
                [cls.model_validate(req) for req in requests]
                if requests
                else []
            )
        except Exception:
            return []
