# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from lionagi.protocols.types import Log

if TYPE_CHECKING:
    from lionagi.operatives.types import ActionResponseModel
    from lionagi.session.branch import Branch


async def _act(
    branch: "Branch",
    action_request: BaseModel | dict,
    suppress_errors: bool = False,
    verbose_action: bool = False,
) -> "ActionResponseModel":

    _request = {}

    if isinstance(action_request, BaseModel):
        if hasattr(action_request, "function") and hasattr(
            action_request, "arguments"
        ):
            _request["function"] = action_request.function
            _request["arguments"] = action_request.arguments
    elif isinstance(action_request, dict):
        if {"function", "arguments"} <= set(action_request.keys()):
            _request["function"] = action_request["function"]
            _request["arguments"] = action_request["arguments"]

    try:
        if verbose_action:
            args_ = str(_request["arguments"])
            args_ = args_[:50] + "..." if len(args_) > 50 else args_
            print(f"Invoking action {_request['function']} with {args_}.")

        func_call = await branch._action_manager.invoke(_request)
        if verbose_action:
            print(
                f"Action {_request['function']} invoked, status: {func_call.status}."
            )

    except Exception as e:
        content = {
            "error": str(e),
            "function": _request.get("function"),
            "arguments": _request.get("arguments"),
            "branch": str(branch.id),
        }
        branch._log_manager.log(Log(content=content))
        if verbose_action:
            print(f"Action {_request['function']} failed, error: {str(e)}.")
        if suppress_errors:
            logging.error(
                f"Error invoking action '{_request['function']}': {e}"
            )
            return None
        raise e

    branch._log_manager.log(Log.create(func_call))

    from lionagi.protocols.types import ActionRequest

    if not isinstance(action_request, ActionRequest):
        action_request = ActionRequest.create(
            sender=branch.id,
            recipient=func_call.func_tool.id,
            **_request,
        )

    # Add the action request/response to the message manager, if not present
    if action_request not in branch.messages:
        branch.msgs.add_message(action_request=action_request)

    branch.msgs.add_message(
        action_request=action_request,
        action_output=func_call.response,
    )

    # Return an ActionResponse object
    from lionagi.operatives.types import ActionResponseModel

    return ActionResponseModel(
        function=action_request.function,
        arguments=action_request.arguments,
        output=func_call.response,
    )
