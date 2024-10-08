from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse


def handle_action_request(
    *,
    sender,
    recipient,
    action_request,
    func,
    arguments,
) -> ActionRequest | None:
    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request

    if func:
        if callable(func):
            func = func.__name__
        if not arguments:
            raise ValueError(
                "Error: please provide arguments for the function."
            )
        return ActionRequest(
            func=func,
            arguments=arguments,
            sender=sender,
            recipient=recipient,
        )


def handle_action_response(
    *,
    sender,
    action_request,
    action_response,
    func_output,
) -> ActionResponse | ActionRequest | None:
    if func_output or action_response:
        if not action_request or not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: please provide a corresponding action request for an "
                "action response."
            )

        # if action response is provided, we update the request with the
        # response and return the response
        if isinstance(action_response, ActionResponse):
            action_response.update_request(
                action_request=action_request,
                func_output=func_output,
            )
            return action_response

        # if only function output is provided, we create a new action response
        return ActionResponse(
            action_request=action_request,
            sender=sender,
            func_outputs=func_output,
        )

    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise ValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request


def handle_action(
    *,
    sender,
    recipient,
    action_request,
    action_response,
    func,
    arguments,
    func_output,
) -> ActionRequest | ActionResponse | None:
    a = handle_action_response(
        sender=sender,
        action_request=action_request,
        action_response=action_response,
        func_output=func_output,
    )
    if isinstance(a, ActionResponse):
        return a

    return handle_action_request(
        sender=sender,
        recipient=recipient,
        action_request=action_request,
        func=func,
        arguments=arguments,
    )
