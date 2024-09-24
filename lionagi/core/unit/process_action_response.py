from typing import Callable
from lion_core.libs import alcall
from lionagi.core.message.action_request import ActionRequest
from lionagi.core.session.branch import Branch


async def process_action_response(
    branch: Branch,
    action_requests: list[ActionRequest],
    responses: list | bool,
    response_parser: Callable = None,
    parser_kwargs: dict = None,
) -> list:
    if responses == False:
        return

    responses = [responses] if not isinstance(responses, list) else responses

    results = []
    if response_parser:
        results = await alcall(
            func=response_parser,
            input_=responses,
            default=None,
            **(parser_kwargs or {}),
        )

    results = results or responses

    for request, result in zip(action_requests, results):
        if result is not None:
            branch.add_message(
                action_request=request,
                func_outputs=result,
                sender=request.recipient,
                recipient=request.sender,
            )
