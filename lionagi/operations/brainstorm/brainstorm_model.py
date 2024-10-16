from pydantic import Field

from ..plan.base import DirectiveModel
from ..react.reason_model import ReasonModel
from ..step_model import ReasonStepModel, StepModel


class BrainstormModel(DirectiveModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the brainstorming session.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the context or focus of the brainstorming session.",
    )
    ideas: list[StepModel] = Field(
        [],
        title="Ideas",
        description="A list of ideas for the next step, generated during brainstorming.",
    )


class ReasonBrainstormModel(BrainstormModel):

    title: str | None = Field(
        None,
        title="Title",
        description="Provide a concise title summarizing the brainstorming session.",
    )
    content: str | None = Field(
        None,
        title="Content",
        description="Describe the context or focus of the brainstorming session.",
    )
    ideas: list[ReasonStepModel] = Field(
        [],
        title="Ideas",
        description="A list of ideas for the next step, generated during brainstorming.",
    )
    reason: ReasonModel | None = None
