from lionagi.libs.ln_func_call import lcall

from .message import RoledMessage
from .system import System
from .instruction import Instruction
from .assistant_response import AssistantResponse
from .action_request import ActionRequest
from .action_response import ActionResponse

def create_message(
    system=None,            # system node - JSON serializable
    instruction=None,       # Instruction node - JSON serializable
    context=None,           # JSON serializable
    assistant_response=None,    # JSON
    function = None,
    arguments = None,
    func_outputs = None,
    action_request=None,        # ActionRequest node
    action_response=None,       # ActionResponse node
    sender=None,                # str
    recipient=None,             # str
    requested_fields=None,      # dict[str, str]
):
    if func_outputs:
        if not action_request:
            raise ValueError("Error: please provide an corresponding action request for an action response.")
        return ActionResponse(
            action_request=action_request,
            sender=sender,
            func_outputs=func_outputs
            



    if not sum(
        lcall([system, instruction, assistant_response, func_outputs,])
    )








    if not func_outputs:
        for v in _dict.values:
            if v is not None and isinstance(v, RoledMessage):
                return v
    
    if system:
        return System(system=system, sender=sender, recipient=recipient)
    
    elif instruction:
        return Instruction(
            instruction=instruction, 
            context=context, 
            sender=sender, 
            recipient=recipient, 
            requested_fields=requested_fields
        )
        
    elif assistant_response:
        return AssistantResponse(assistant_response=assistant_response, sender=sender, recipient=recipient)

    elif not all([function, arguments]):
        raise ValueError("Error: Both function and arguments are required.")
    
    if func_outputs:
        return ActionResponse(
            function=function, 
            arguments=arguments, 
            func_outputs=func_outputs, 
            sender=sender, 
            recipient=recipient
        )
        
    return ActionRequest(
        function=function, 
        arguments=arguments, 
        sender=sender, 
        recipient=recipient
    )
















def create_message(
    system=None, 
    instruction=None, 
    context=None, 
    assistant_response=None,
    action_re
):
    ...

        if isinstance(system, System):
            return system
        elif isinstance(instruction, Instruction):
            return instruction
        elif isinstance(response, Response):
            return response

        msg = 0
        if response:
            msg = Response(response=response, **kwargs)
        elif instruction:
            msg = Instruction(
                instruction=instruction,
                context=context,
                output_fields=output_fields,
                **kwargs,
            )
        elif system:
            msg = System(system=system, **kwargs)
        return msg
