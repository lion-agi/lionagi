from lion_core.action.tool import Tool
from lion_core.communication import Instruction, System
from lion_core.operative.step_model import StepModel
from lion_core.session.branch import Branch
from lion_core.types import IDTypes
from lion_service import iModel
from pydantic import BaseModel, Field
from pydantic.types import JsonValue

from ..config import DEFAULT_CHAT_CONFIG
from .fields import IDEAS_FIELD, TOPIC_FIELD
from .prompt import PROMPT

TOPIC_ = TOPIC_FIELD.to_dict()
IDEAS_ = IDEAS_FIELD.to_dict()


class BrainstormModel(BaseModel):

    topic: str = Field(**TOPIC_)
    ideas: list[StepModel] = Field(**IDEAS_)


async def brainstorm(
    num_steps: int = 3,
    instruction: JsonValue | Instruction = None,
    guidance: JsonValue = None,
    context: JsonValue = None,
    system: JsonValue | System = None,
    reason: bool = False,
    actions: bool = False,
    tools: bool | str | list | Tool = None,
    imodel: iModel = None,
    branch: Branch = None,
    sender: IDTypes.SenderRecipient = None,
    recipient: IDTypes.SenderRecipient = None,
    clear_messages: bool = False,
    system_sender: IDTypes.SenderRecipient = None,
    system_datetime: bool | str = None,
    return_branch: bool = False,
    num_parse_retries: int = 0,
    retry_imodel: iModel = None,
    branch_user: IDTypes.SenderRecipient = None,
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
        if isinstance(context, list):
            _context.extend(context)
        else:
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
