from typing import Any

from lion_core.operative.step_model import StepModel
from lion_core.session.branch import Branch
from lion_service import iModel
from pydantic import BaseModel, Field

from .config import DEFAULT_CHAT_CONFIG


class BrainstormModel(BaseModel):

    topic: str = Field(
        default_factory=str,
        description="**Specify the topic or theme for the brainstorming session.**",
    )
    ideas: list[StepModel] = Field(
        default_factory=list,
        description="**Provide a list of ideas needed to accomplish the objective. Each step should be as described in a `PlanStepModel`.**",
    )


PROMPT = "Please follow prompt and provide {num_steps} different ideas for the next step"


async def brainstorm(
    num_steps: int = 3,
    instruction=None,
    guidance=None,
    context=None,
    system=None,
    reason: bool = False,
    actions: bool = False,
    tools: Any = None,
    imodel: iModel = None,
    branch: Branch = None,
    sender=None,
    recipient=None,
    clear_messages: bool = False,
    system_sender=None,
    system_datetime=None,
    return_branch=False,
    num_parse_retries: int = 3,
    retry_imodel: iModel = None,
    branch_user=None,
    **kwargs,  # additional operate arguments
):
    if branch and branch.imodel:
        imodel = imodel or branch.imodel
    else:
        imodel = imodel or iModel(**DEFAULT_CHAT_CONFIG)

    prompt = PROMPT.format(num_steps=num_steps)

    branch = branch or Branch(imodel=imodel)
    if branch_user:
        branch.user = branch_user

    if system:
        branch.add_message(
            system=system,
            system_datetime=system_datetime,
            sender=system_sender,
        )
    _context = [{"operation": prompt}]
    if context:
        _context.append(context)

    response = await branch.operate(
        instruction=instruction,
        guidance=guidance,
        context=_context,
        sender=sender,
        recipient=recipient,
        reason=reason,
        actions=actions,
        tools=tools,
        clear_messages=clear_messages,
        operative_model=BrainstormModel,
        retry_imodel=retry_imodel,
        num_parse_retries=num_parse_retries,
        imodel=imodel,
        **kwargs,
    )
    if return_branch:
        return response, branch
    return response
