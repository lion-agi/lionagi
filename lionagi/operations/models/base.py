from typing import Any

from lionfuncs import validate_str
from pydantic import BaseModel, field_validator


class DirectiveModel(BaseModel):

    title: str | None = None
    content: str | None = None

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")
