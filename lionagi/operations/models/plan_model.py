from pydantic import Field

from .base import DirectiveModel
from .reason_model import ReasonModel
from .step_model import ReasonStepModel, StepModel


class PlanModel(DirectiveModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the plan.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Provide a detailed description of the plan.",
    )
    steps: list[StepModel] = Field(
        [],
        title="Steps",
        description="A list of steps to execute the plan.",
    )


class ReasonPlanModel(PlanModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the plan.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Provide a detailed description of the plan.",
    )
    steps: list[ReasonStepModel] = Field(
        [],
        title="Steps",
        description="A list of steps to execute the plan.",
    )
    reason: ReasonModel | None = None
