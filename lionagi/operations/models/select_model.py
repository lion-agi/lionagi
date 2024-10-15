from typing import Any

from pydantic import Field, field_validator

from .base import DirectiveModel
from .reason_model import ReasonModel


class SelectionModel(DirectiveModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the selection process.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the context or focus of the selection process.",
    )
    selected: list[Any] = []

    @field_validator("selected", mode="before")
    def _(cls, value: Any) -> Any:
        return value if isinstance(value, list) else [value]


class ReasonSelectionModel(SelectionModel):
    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the selection process.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the context or focus of the selection process.",
    )
    selected: list[Any] = []
    reason: ReasonModel | None = None
