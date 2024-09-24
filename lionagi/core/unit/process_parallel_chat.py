"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Module for parallel processing of chat interactions in the Lion framework.

This module provides functionality to handle multiple chat processes
concurrently across different branches of a session.
"""

import asyncio
from functools import partial
from typing import Any, Literal

from lion_core.abc import BaseProcessor
from lion_core.libs import to_list
from lion_core.generic.pile import pile, Pile
from lion_core.communication.action_request import ActionRequest
from lion_core.session.branch import Branch
from lionagi.core.unit.unit import Unit

from lion_core.session.session import Session

as_nice_list = partial(to_list, flatten=True, dropna=True)


async def process_parallel_chat(
    session: "Session",
    *,
    branches: Pile[Branch] | None = None,
    form=None,
    sender=None,
    recipient=None,
    instruction: Any = None,  # single | list
    context: Any = None,  # single | list
    request_fields=None,
    action_request: ActionRequest | None = None,
    imodel=None,
    images=None,
    image_path=None,
    image_detail: Literal["low", "high", "auto"] = None,
    tools: bool | None = None,
    validator: BaseProcessor | None = None,
    rulebook=None,
    strict_validation: bool = False,
    use_annotation: bool = True,
    branch_system: Any = None,
    branch_system_datetime: Any = None,
    branch_messages=None,
    clear_branch_messages: bool = False,
    tool_manager=None,
    num_instances: int = 1,
    explode: bool = False,
    **kwargs
) -> list[Any]:
    """
    Process chat interactions in parallel across multiple branches.

    Args:
        session: The Session object to process chats for.
        branches: Existing branches to use for processing.
        form: The form associated with the chat.
        sender: Sender of the message.
        recipient: Recipient of the message.
        instruction: Instruction(s) for the chat (single or list).
        context: Context(s) for the chat (single or list).
        request_fields: Fields requested in the response.
        action_request: Action request for the chat.
        imodel: The iModel to use for chat completion.
        images: Image data for the chat.
        image_path: Path to an image file.
        image_detail: Detail level for image processing.
        tools: Whether to include tools in the configuration.
        validator: The validator to use for form validation.
        rulebook: Optional rulebook for validation.
        strict_validation: Whether to use strict validation.
        use_annotation: Whether to use annotation for validation.
        branch_system: System message for new branches.
        branch_system_datetime: Datetime for system messages in new branches.
        branch_messages: Initial messages for new branches.
        clear_branch_messages: Whether to clear existing branch messages.
        tool_manager: Tool manager for new branches.
        num_instances: Number of instances to create for each combination.
        explode: Whether to create all possible instruction-context pairs.
        **kwargs: Additional keyword arguments for chat processing.

    Returns:
        A list of results from parallel chat processing.
    """
    branches = branches or pile()

    async def process_single_chat(branch_, instruct_, context_):
        if not branch_:
            branch_ = await session.new_branch(
                system=branch_system,
                system_sender=session.ln_id,
                system_datetime=branch_system_datetime,
                user=session.user,
                imodel=imodel or session.imodel,
                messages=branch_messages,
                tool_manager=tool_manager,
                tools=tools,
            )

        unit_ = Unit(branch=branch_)
        resp_ = await unit_.process_chat(
            form=form,
            sender=sender,
            recipient=recipient,
            instruction=instruct_,
            context=context_,
            request_fields=request_fields,
            images=images,
            image_path=image_path,
            image_detail=image_detail,
            action_request=action_request,
            system_datetime=branch_system_datetime,
            tools=tools,
            clear_messages=clear_branch_messages,
            validator=validator,
            rulebook=rulebook,
            strict_validation=strict_validation,
            use_annotation=use_annotation,
            return_branch=True,
            **kwargs
        )
        branches.include(branch_)
        return resp_

    async def process_multiple_instances(branch, instruct_=None, context_=None):
        tasks = [
            process_single_chat(branch, instruct_, context_)
            for _ in range(num_instances)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_instruction(branch):
        tasks = [
            process_multiple_instances(branch, instruct_=ins_)
            for ins_ in as_nice_list(instruction)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_context(branch):
        tasks = [
            process_multiple_instances(branch, context_=ctx_)
            for ctx_ in as_nice_list(context)
        ]
        return as_nice_list(await asyncio.gather(*tasks))

    async def process_multi_instruction_context(branch):
        if explode:
            tasks = [
                process_multiple_instances(branch, instruct_=ins_, context_=ctx_)
                for ins_ in as_nice_list(instruction)
                for ctx_ in as_nice_list(context)
            ]
        else:
            tasks = [
                process_multiple_instances(branch, instruct_=ins_, context_=ctx_)
                for ins_, ctx_ in zip(as_nice_list(instruction), as_nice_list(context))
            ]
        return as_nice_list(await asyncio.gather(*tasks))

    instr_list = as_nice_list(instruction)
    ctx_list = as_nice_list(context)

    if len(instr_list) == 1:
        if len(ctx_list) == 1:
            out_ = await process_multiple_instances(0)
        else:
            out_ = await process_multi_context(0)
    elif len(ctx_list) == 1:
        out_ = await process_multi_instruction(0)
    else:
        out_ = await process_multi_instruction_context(0)

    session.branches.include(list(branches))
    return out_


__all__ = ["process_parallel_chat"]

# File: lion_core/chat/process_parallel_chat.py
