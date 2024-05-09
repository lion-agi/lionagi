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
            action_request=action_request, sender=sender, func_outputs=func_outputs
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
            function=function, arguments=arguments, sender=sender, recipient=recipient
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
        )

    elif assistant_response:
        return AssistantResponse(
            assistant_response=assistant_response, sender=sender, recipient=recipient
        )
