import re
import contextlib
import asyncio
from typing import Any, Optional, Callable
from lion_core.action.tool import Tool
from lion_core.action.tool_manager import func_to_tool
from lion_core.exceptions import ItemNotFoundError
from lion_core.libs import validate_mapping, fuzzy_parse_json, extract_json_block
from lion_core.communication.utils import parse_action_request


retry_kwargs = {
    "retries": 0,  # kwargs for rcall, number of retries if failed
    "delay": 0,  # number of seconds to delay before retrying
    "backoff_factor": 1,  # exponential backoff factor, default 1 (no backoff)
    "default": None,  # default value to return if all retries failed
    "timeout": None,  # timeout for the rcall, default None (no timeout)
    "timing": False,  # if timing will return a tuple (output, duration)
}

ai_fields = [
    "id",
    "object",
    "created",
    "model",
    "choices",
    "usage",
    "system_fingerprint",
]

choices_fields = ["index", "message", "logprobs", "finish_reason"]

usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]


async def process_action_request(
    _msg: Optional[dict] = None,
    branch: Optional[Any] = None,
    invoke_tool: bool = True,
    action_request: Optional[Any] = None,
) -> Any:
    """
    Processes an action request from the assistant response.

    Args:
        _msg: The message data.
        branch: The branch instance.
        invoke_tool: Flag indicating if tools should be invoked.
        action_request: The action request instance.

    Returns:
        Any: The processed result.
    """
    action_request = action_request or parse_action_request(_msg)
    if action_request is None:
        return _msg if _msg else False

    if action_request:
        for i in action_request:
            if i.function in branch.tool_manager.registry:
                i.recipient = branch.tool_manager.registry[i.function].ln_id
            else:
                raise ItemNotFoundError(f"Tool {i.function} not found in registry")
            branch.add_message(action_request=i, recipient=i.recipient)

    if invoke_tool:
        tasks = []
        for i in action_request:
            tool = branch.tool_manager.registry[i.function]
            tasks.append(asyncio.create_task(tool.invoke(i.arguments)))
        results = await asyncio.gather(*tasks)

        for idx, item in enumerate(results):
            if item is not None:
                branch.add_message(
                    action_request=action_request[idx],
                    func_outputs=item,
                    sender=action_request[idx].recipient,
                    recipient=action_request[idx].sender,
                )

    return None


def process_model_response(content_, requested_fields):
    """
    Processes the model response content.

    Args:
        content_: The content data.
        requested_fields: Fields requested in the response.

    Returns:
        Any: The processed response.
    """
    out_ = content_.get("content", "")
    if out_ == "":
        out_ = content_

    if requested_fields:
        with contextlib.suppress(Exception):
            return validate_mapping(out_, requested_fields, handle_unmatched="force")

    if isinstance(out_, str):
        with contextlib.suppress(Exception):
            return fuzzy_parse_json(out_)

        with contextlib.suppress(Exception):
            return extract_json_block(out_)

        with contextlib.suppress(Exception):
            match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
            if match:
                return fuzzy_parse_json(match.group(1))

    return out_


def process_tools(tool_obj, branch):
    if isinstance(tool_obj, Callable):
        _process_tool(tool_obj, branch)
    else:
        if isinstance(tool_obj, bool):
            return
        for i in tool_obj:
            _process_tool(i, branch)


def _process_tool(tool_obj, branch):
    if (
        isinstance(tool_obj, Tool)
        and tool_obj.schema_["function"]["name"] not in branch.tool_manager.registry
    ):
        branch.register_tools(tool_obj)
    if isinstance(tool_obj, Callable):
        tool = func_to_tool(tool_obj)[0]
        if tool.schema_["function"]["name"] not in branch.tool_manager.registry:
            branch.register_tools(tool)
