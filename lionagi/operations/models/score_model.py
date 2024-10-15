from typing import Any

from pydantic import Field, field_validator

from .base import DirectiveModel
from .reason_model import ReasonModel


class ScoreModel(DirectiveModel):

    title: str | None = Field(
        ...,
        title="Title",
        description="Title for the scoring task",
    )
    content: str | None = Field(
        ...,
        title="Content",
        description="Brief description of the scoring task",
    )
    score: list[Any] = Field(
        [],
        title="Score",
        description="The score for the task",
    )

    @field_validator("score", mode="before")
    def _(cls, value):
        return value if isinstance(value, list) else [value]


class ReasonScoreModel(ScoreModel):

    title: str | None = Field(
        ...,
        title="Title",
        description="Title for the scoring task",
    )
    content: str | None = Field(
        ...,
        title="Content",
        description="Brief description of the scoring task",
    )
    score: list[Any] = Field(
        [],
        title="Score",
        description="The score for the task",
    )
    reason: ReasonModel | None = None
