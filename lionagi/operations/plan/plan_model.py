from pydantic import BaseModel, Field


class PlanStepModel(BaseModel):
    title: str | None = Field(
        None,
        title="Title",
        description="**Provide a concise title summarizing the step.**",
    )

    description: str = Field(
        ...,
        description="**Describe a specific action step required to achieve the plan's objective.**",
    )


class PlanningModel(BaseModel):
    title: str | None = Field(
        None,
        title="Title",
        description="**Provide a concise title summarizing the plan.**",
    )

    objective: str = Field(
        ...,
        description="**State the goal or purpose of the plan in a clear and concise manner.**",
    )
    steps: list[PlanStepModel] = Field(
        default_factory=list,
        description="**Outline the sequence of steps needed to accomplish the objective. Each step should be a specific action described in a `PlanStepModel`.**",
    )
