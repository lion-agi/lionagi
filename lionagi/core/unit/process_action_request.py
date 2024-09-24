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
Module for processing action requests in the Lion framework.

This module provides functionality to handle action requests, including
parsing, validation, and execution of associated functions.
"""

import asyncio
from typing import Any

from lion_core.exceptions import ItemNotFoundError
from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.action_request import ActionRequest
from lion_core.session.msg_handlers.create_request import create_action_request
from lion_core.session.branch import Branch


async def process_action_request(
    branch: Branch,
    response: dict | None = None,
    action_request: list[ActionRequest] | dict | str | None = None,
    invoke_action: bool = True,
) -> list[Any] | dict | bool:
    """
    Process action requests for a given branch.

    Args:
        branch: The Branch object to process action requests for.
        response: Optional message dictionary to parse for action requests.
        action_request: Pre-parsed action requests or raw data to parse.
        invoke_action: Whether to invoke the action or not.

    Returns:
        The results of the action requests, the response, or False if no
        requests were found.

    Raises:
        ItemNotFoundError: If a requested tool is not found in the registry.
    """
    action_requests = action_request or create_action_request(response)
    tasks = []
    for request in action_requests:
        func_name = request.content.get(["action_request", "function"], "")
        if func_name in branch.tool_manager:
            tool = branch.tool_manager.registry[func_name]
            request.recipient = tool.ln_id
        else:
            raise ItemNotFoundError(
                f"Tool {func_name} not found in tool registry",
            )
        branch.add_message(
            action_request=request,
            recipient=request.recipient,
        )

        args = request.content["action_request", "arguments"]

        if invoke_action:
            func_call = FunctionCalling(tool, args)
            tasks.append(asyncio.create_task(func_call.invoke()))

    if tasks:
        return action_requests, await asyncio.gather(*tasks)

    return [], response


__all__ = ["process_action_request"]

# File: lion_core/action/processing.py
