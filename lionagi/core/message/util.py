from lionagi.libs.ln_convert import strip_lower, to_dict
from lionagi.libs.ln_nested import nget

from lionagi.libs.ln_func_call import lcall

from .message import RoledMessage
from .system import System
from .instruction import Instruction
from .assistant_response import AssistantResponse
from .action_request import ActionRequest
from .action_response import ActionResponse


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
    sender=None,  # str
    recipient=None,  # str
    requested_fields=None,  # dict[str, str]
    **kwargs,  # additional context fields
):
    # order of handling
    # action response - action request - other regular messages
    # if the message is output from function calling we will ignore other message types

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
            raise ValueError("Error: please provide arguments for the function.")
        return ActionRequest(
            function=function,
            arguments=arguments,
            sender=sender,
            recipient=recipient,
        )

    if not sum(lcall([system, instruction, assistant_response], bool)) == 1:
        raise ValueError("Error: Message can only have one role")

    if not func_outputs:
        for v in [system, instruction, assistant_response]:
            if v is not None and isinstance(v, RoledMessage):
                if isinstance(v, Instruction):
                    if context:
                        v._add_context(context)
                    if requested_fields:
                        v._update_requested_fields(requested_fields)
                return v

    if system:
        return System(system=system, sender=sender, recipient=recipient)

    elif instruction:
        return Instruction(
            instruction=instruction,
            context=context,
            sender=sender,
            recipient=recipient,
            requested_fields=requested_fields,
            **kwargs,
        )

    elif assistant_response:
        return AssistantResponse(
            assistant_response=assistant_response,
            sender=sender,
            recipient=recipient,
        )


def _parse_action_request(response):

    message = to_dict(response) if not isinstance(response, dict) else response
    content_ = None

    if strip_lower(nget(message, ["content"])) == "none":
        content_ = _handle_action_request(message)

    elif nget(message, ["content", "tool_uses"], None):
        content_ = message["content"]["tool_uses"]

    if isinstance(content_, dict):
        content_ = [content_]

    if isinstance(content_, list):
        outs = []
        for func_calling in content_:
            msg = ActionRequest(
                function=func_calling["action"].replace("action_", ""),
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
                    msg = ActionRequest(
                        function=func_calling["action"].replace("action_", ""),
                        arguments=func_calling["arguments"],
                    )
                    outs.append(msg)
                return outs
        except:
            return None
    return None


def _handle_action_request(response):
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
