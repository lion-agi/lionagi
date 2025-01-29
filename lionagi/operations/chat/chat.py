# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lionagi.protocols.types import (
    ActionResponse,
    AssistantResponse,
    Instruction,
    Log,
    RoledMessage,
)
from lionagi.service.imodel import iModel
from lionagi.utils import copy

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def chat(
    branch: "Branch",
    instruction=None,
    guidance=None,
    context=None,
    sender=None,
    recipient=None,
    request_fields=None,
    response_format: type[BaseModel] = None,
    progression=None,
    imodel: iModel = None,
    tool_schemas=None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    plain_content: str = None,
    return_ins_res_message: bool = False,
    include_token_usage_to_model: bool = False,
    **kwargs,
) -> tuple[Instruction, AssistantResponse]:
    ins: Instruction = branch.msgs.create_instruction(
        instruction=instruction,
        guidance=guidance,
        context=context,
        sender=sender or branch.user or "user",
        recipient=recipient or branch.id,
        response_format=response_format,
        request_fields=request_fields,
        images=images,
        image_detail=image_detail,
        tool_schemas=tool_schemas,
        plain_content=plain_content,
    )

    progression = progression or branch.msgs.progression
    messages: list[RoledMessage] = [
        branch.msgs.messages[i] for i in progression
    ]

    use_ins = None
    _to_use = []
    _action_responses: set[ActionResponse] = set()

    for i in messages:
        if isinstance(i, ActionResponse):
            _action_responses.add(i)
        if isinstance(i, AssistantResponse):
            j = AssistantResponse(
                role=i.role,
                content=copy(i.content),
                sender=i.sender,
                recipient=i.recipient,
                template=i.template,
            )
            _to_use.append(j)
        if isinstance(i, Instruction):
            j = Instruction(
                role=i.role,
                content=copy(i.content),
                sender=i.sender,
                recipient=i.recipient,
                template=i.template,
            )
            j.tool_schemas = None
            j.respond_schema_info = None
            j.request_response_format = None

            if _action_responses:
                d_ = [k.content for k in _action_responses]
                for z in d_:
                    if z not in j.context:
                        j.context.append(z)

                _to_use.append(j)
                _action_responses = set()
            else:
                _to_use.append(j)

    messages = _to_use
    if _action_responses:
        j = ins.model_copy()
        d_ = [k.content for k in _action_responses]
        for z in d_:
            if z not in j.context:
                j.context.append(z)
        use_ins = j

    if messages and len(messages) > 1:
        _msgs = [messages[0]]

        for i in messages[1:]:
            if isinstance(i, AssistantResponse):
                if isinstance(_msgs[-1], AssistantResponse):
                    _msgs[-1].response = (
                        f"{_msgs[-1].response}\n\n{i.response}"
                    )
                else:
                    _msgs.append(i)
            else:
                if isinstance(_msgs[-1], AssistantResponse):
                    _msgs.append(i)
        messages = _msgs

    imodel = imodel or branch.chat_model
    if branch.msgs.system and imodel.sequential_exchange:
        messages = [msg for msg in messages if msg.role != "system"]
        first_instruction = None

        if len(messages) == 0:
            first_instruction = ins.model_copy()
            first_instruction.guidance = branch.msgs.system.rendered + (
                first_instruction.guidance or ""
            )
            messages.append(first_instruction)
        elif len(messages) >= 1:
            first_instruction = messages[0]
            if not isinstance(first_instruction, Instruction):
                raise ValueError(
                    "First message in progression must be an Instruction or System"
                )
            first_instruction = first_instruction.model_copy()
            first_instruction.guidance = branch.msgs.system.rendered + (
                first_instruction.guidance or ""
            )
            messages[0] = first_instruction
            messages.append(use_ins or ins)

    else:
        messages.append(use_ins or ins)

    kwargs["messages"] = [i.chat_msg for i in messages]
    imodel = imodel or branch.chat_model

    meth = imodel.invoke
    if "stream" not in kwargs or not kwargs["stream"]:
        kwargs["include_token_usage_to_model"] = include_token_usage_to_model
    else:
        meth = imodel.stream

    api_call = await meth(**kwargs)
    branch._log_manager.log(Log.create(api_call))

    if return_ins_res_message:
        # Wrap result in `AssistantResponse` and return
        return ins, AssistantResponse.create(
            assistant_response=api_call.response,
            sender=branch.id,
            recipient=branch.user,
        )
    return AssistantResponse.create(
        assistant_response=api_call.response,
        sender=branch.id,
        recipient=branch.user,
    ).response
