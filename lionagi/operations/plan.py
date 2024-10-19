from typing import Any

from lion_core.generic import Progression
from lion_core.operative.operative import StepModel
from lion_core.session.branch import Branch
from pydantic import BaseModel, Field


class PlanningModel(BaseModel):

    title: str | None = Field(
        None,
        title="Title",
        description="**Provide a concise title summarizing the plan.**",
    )
    objective: str = Field(
        default_factory=str,
        description="**State the goal or purpose of the plan in a clear and concise manner.**",
    )
    steps: list[StepModel] = Field(
        default_factory=list,
        description="**Outline the sequence of steps needed to accomplish the objective. Each step should be as described in a `PlanStepModel`.**",
    )


PROMPT = (
    "Please follow prompt and provide step-by-step plan of {num_steps} steps"
)


# the inner steps are not immidiately executed, but are planned
async def plan(
    num_steps: int = 3,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    progress: Progression = None,
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    return_branch=False,
    invoke_action: bool = True,
    **kwargs,  # additional operate arguments
) -> PlanningModel:
    branch = branch or Branch()
    response, branch = await _plan(
        num_steps=num_steps,
        instruction=instruction,
        guidance=guidance,
        context=context,
        system=system,
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        branch=branch,
        clear_messages=clear_messages,
        progress=progress,
        system_sender=system_sender,
        system_datetime=system_datetime,
        invoke_action=invoke_action,
        **kwargs,
    )
    if return_branch:
        return response, branch
    return response


async def _plan(
    num_steps: int = 3,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    progress: Progression = None,
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    invoke_action: bool = True,
    **kwargs,  # additional operate arguments
):
    prompt = PROMPT.format(num_steps=num_steps)

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            sender=system_sender,
        )

    response = await branch.operate(
        instruction=instruction,
        guidance=guidance,
        context=(
            [{"operation": prompt}, context]
            if context
            else {"operation": prompt}
        ),
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        progress=progress,
        clear_messages=clear_messages,
        operative_model=PlanningModel,
        invoke_action=invoke_action,
        **kwargs,
    )
    return response, branch
