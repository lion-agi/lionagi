from typing import Any, List

from lionfuncs import validate_str
from pydantic import BaseModel, Field, field_validator

from .reason_model import ReasonModel
from .step_model import StepModel


class PlanModel(BaseModel):
    """
    Represents a plan consisting of multiple steps, with an overall reason.

    Attributes:
        title (str): A concise title summarizing the plan.
        content (str): A detailed description of the plan.
        reason (ReasonModel): The overall reasoning behind the plan.
        steps (List[StepModel]): A list of steps to execute the plan.
    """

    title: str = Field(
        ...,
        title="Title",
        description="Provide a concise title summarizing the plan.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="Provide a detailed description of the plan.",
    )
    reason: ReasonModel = Field(
        ...,
        title="Reason",
        description="Provide the reasoning behind the entire plan.",
    )
    steps: list[StepModel] = Field(
        ...,
        title="Steps",
        description="A list of steps to execute the plan.",
    )

    @field_validator("title", mode="before")
    def validate_title(cls, value: Any) -> str:
        return validate_str(value, "title")

    @field_validator("content", mode="before")
    def validate_content(cls, value: Any) -> str:
        return validate_str(value, "content")


__all__ = ["PlanModel"]
