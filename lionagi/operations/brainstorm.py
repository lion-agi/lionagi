from typing import Any

from lion_core.generic import Progression
from lion_core.operative.step_model import StepModel
from lion_core.session.branch import Branch
from pydantic import BaseModel, Field


class BrainstormModel(BaseModel):

    topic: str = Field(
        default_factory=str,
        description="**Specify the topic or theme for the brainstorming session.**",
    )
    ideas: list[StepModel] = Field(
        default_factory=list,
        description="**Provide a list of ideas needed to accomplish the objective. Each step should be as described in a `PlanStepModel`.**",
    )


PROMPT = "Please follow prompt and provide {num_ideas} different ideas for the next step"


# the inner steps are not immidiately executed
async def brainstorm(
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
    **kwargs,  # additional operate arguments
):
    response, branch = await _brainstorm(
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
        system_datetime=system_datetime**kwargs,
    )
    if return_branch:
        return response, branch
    return response


async def _brainstorm(
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
        operative_model=BrainstormModel,
        **kwargs,
    )
    return response, branch
