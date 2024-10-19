from typing import Any

from lion_core.generic import Progression
from lion_core.session.branch import Branch

from .plan_model import PlanningModel

PROMPT = (
    "Please follow prompt and provide step-by-step plan of {num_steps} steps"
)


async def plan(
    num_steps: int = 3,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    sender=None,
    recipient=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    branch: Branch = None,
    return_branch=False,
    clear_messages: bool = False,
    **kwargs,  # additional operate arguments
):
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
        **kwargs,
    )
    return response, branch
