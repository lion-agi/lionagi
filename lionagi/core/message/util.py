import json
import re

from lionfuncs import nget, to_dict

from .action_request import ActionRequest
from .action_response import ActionResponse
from .assistant_response import AssistantResponse
from .instruction import Instruction
from .message import RoledMessage
from .system import System


def create_message(
    *,
    system=None,  # system node - JSON serializable
    instruction=None,  # Instruction node - JSON serializable
    context=None,  # JSON serializable
    assistant_response=None,  # JSON
    function=None,
    arguments=None,
    func_outputs=None,
    action_request=None,  # ActionRequest node
    action_response=None,  # ActionResponse node
    images=None,  # base64 encoded image
    sender=None,  # str
    recipient=None,  # str
    requested_fields=None,  # dict[str, str]
    **kwargs,  # additional context fields
):
    # order of handling
    # action response - action request - other regular messages
    # if the message is output from function calling we will ignore other message types
    """
    Creates a message based on the provided parameters.

    Args:
        system (dict, optional): The system node (JSON serializable).
        instruction (dict, optional): The instruction node (JSON serializable).
        context (dict, optional): Additional context (JSON serializable).
        assistant_response (dict, optional): The assistant response node (JSON serializable).
        function (str, optional): The function name for action requests.
        arguments (dict, optional): The arguments for the function.
        func_outputs (Any, optional): The outputs from the function.
        action_request (ActionRequest, optional): The action request node.
        action_response (ActionResponse, optional): The action response node.
        sender (str, optional): The sender of the message.
        recipient (str, optional): The recipient of the message.
        requested_fields (dict[str, str], optional): The requested fields for the instruction.
        **kwargs: Additional context fields.

    Returns:
        RoledMessage: The constructed message based on the provided parameters.

    Raises:
        ValueError: If the parameters are invalid or missing required values.
    """

    if func_outputs or action_response:
        if not action_request:
            raise ValueError(
                "Error: please provide an corresponding action request for an action response."
            )

        if isinstance(action_response, ActionResponse):
            action_response.update_request(action_request)
            return action_response

        return ActionResponse(
            action_request=action_request,
            sender=sender,
            func_outputs=func_outputs,
        )

    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request

    if function:
        if not arguments:
            raise ValueError(
                "Error: please provide arguments for the function."
            )
        return ActionRequest(
            function=function,
            arguments=arguments,
            sender=sender,
            recipient=recipient,
        )

    a = {
        "system": system,
        "instruction": instruction,
        "assistant_response": assistant_response,
    }

    a = {k: v for k, v in a.items() if v is not None}

    if not len(a) == 1:
        raise ValueError("Error: Message can only have one role")

    if not func_outputs:
        for k, v in a.items():
            if isinstance(v, RoledMessage):
                if isinstance(v, Instruction):
                    if context:
                        v._add_context(context)
                    if requested_fields:
                        v._update_requested_fields(requested_fields)
                return v

    if system:
        return System(system=system, sender=sender, recipient=recipient)

    elif assistant_response:
        return AssistantResponse(
            assistant_response=assistant_response,
            sender=sender,
            recipient=recipient,
        )

    else:
        if images:
            images = images if isinstance(images, list) else [images]

        return Instruction(
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            images=images,
            **kwargs,
        )


def _parse_action_request(response):
    """
    Parses an action request from the response.

    Args:
        response (dict): The response containing the action request.

    Returns:
        list[ActionRequest] or None: A list of action requests or None if invalid.

    Raises:
        ActionError: If the action request is invalid.
    """
    message = to_dict(response) if not isinstance(response, dict) else response
    content_ = None

    if str(nget(message, ["content"])).strip().lower() == "none":
        content_ = _handle_action_request(message)

    elif nget(message, ["content", "tool_uses"], None):
        content_ = message["content"]["tool_uses"]

    else:
        json_block_pattern = re.compile(
            r"```json\n({.*?tool_uses.*?})\n```", re.DOTALL
        )

        # Find the JSON block in the text
        match = json_block_pattern.search(str(message["content"]))
        if match:
            json_block = match.group(1)
            parsed_json = json.loads(json_block)
            if "tool_uses" in parsed_json:
                content_ = parsed_json["tool_uses"]
            elif "actions" in parsed_json:
                content_ = parsed_json["actions"]
            else:
                content_ = []

    if isinstance(content_, dict):
        content_ = [content_]

    if isinstance(content_, list) and not content_ == []:
        outs = []
        for func_calling in content_:
            if "recipient_name" in func_calling:
                func_calling["action"] = func_calling["recipient_name"].split(
                    "."
                )[1]
                func_calling["arguments"] = func_calling["parameters"]
            elif "function" in func_calling:
                func_calling["action"] = func_calling["function"]
                if "parameters" in func_calling:
                    func_calling["arguments"] = func_calling["parameters"]
                elif "arguments" in func_calling:
                    func_calling["arguments"] = func_calling["arguments"]

            msg = ActionRequest(
                function=func_calling["action"]
                .replace("action_", "")
                .replace("recipient_", ""),
                arguments=func_calling["arguments"],
            )
            outs.append(msg)
        return outs

    else:
        try:
            _content = to_dict(message["content"])
            if "action_request" in _content:
                content_ = _content["action_request"]

            if isinstance(content_, dict):
                content_ = [content_]

            if isinstance(content_, list):
                outs = []
                for func_calling in content_:
                    if "function" in func_calling:
                        func_calling["action"] = func_calling["function"]
                        if "parameters" in func_calling:
                            func_calling["arguments"] = func_calling[
                                "parameters"
                            ]
                        elif "arguments" in func_calling:
                            func_calling["arguments"] = func_calling[
                                "arguments"
                            ]
                    msg = ActionRequest(
                        function=func_calling["action"]
                        .replace("action_", "")
                        .replace("recipient_", ""),
                        arguments=func_calling["arguments"],
                    )
                    outs.append(msg)
                return outs
        except:
            return None
    return None


def _handle_action_request(response):
    """
    Handles the action request parsing from the response.

    Args:
        response (dict): The response containing the action request details.

    Returns:
        list[dict]: A list of function call details.

    Raises:
        ValueError: If the response message is invalid.
    """
    try:
        tool_count = 0
        func_list = []
        while tool_count < len(response["tool_calls"]):
            _path = ["tool_calls", tool_count, "type"]

            if nget(response, _path) == "function":
                _path1 = ["tool_calls", tool_count, "function", "name"]
                _path2 = ["tool_calls", tool_count, "function", "arguments"]

                func_content = {
                    "action": f"action_{nget(response, _path1)}",
                    "arguments": nget(response, _path2),
                }
                func_list.append(func_content)
            tool_count += 1
        return func_list
    except:
        raise ValueError(
            "Response message must be one of regular response or function calling"
        )
