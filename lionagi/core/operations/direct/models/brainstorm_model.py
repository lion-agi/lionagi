from typing import Any

from lionfuncs import validate_str
from pydantic import BaseModel, Field, field_validator

from .reason_model import ReasonModel
from .step_model import StepModel


class BrainstormModel(BaseModel):

    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the brainstorming session.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="Describe the context or focus of the brainstorming session.",
    )
    ideas: list[StepModel] = Field(
        ...,
        title="Ideas",
        description="A list of ideas for the next step, generated during brainstorming.",
    )
    reason: ReasonModel = Field(
        ...,
        title="Reason",
        description="Provide the high level reasoning behind the brainstorming session.",
    )

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")


__all__ = ["BrainstormModel"]
