import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from lionagi.protocols.types import ActionResponse, Log

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def _act(
    branch: "Branch",
    action_request: BaseModel | dict,
    suppress_errors: bool = False,
) -> ActionResponse:
    """
    Internal function to invoke a tool (action).

    Args:
        branch (Branch):
            The branch context that holds the tool registry and logs.
        action_request (BaseModel|dict):
            Must include `function` and `arguments`.
        suppress_errors (bool):
            If True, errors are logged instead of raised.

    Returns:
        ActionResponse:
            Contains the output of the tool call, or `None` if suppressed/error.
    """
    try:
        func_name = None
        args = None
        if isinstance(action_request, BaseModel):
            if hasattr(action_request, "function") and hasattr(
                action_request, "arguments"
            ):
                func_name = action_request.function
                args = action_request.arguments
        elif isinstance(action_request, dict):
            if {"function", "arguments"} <= set(action_request.keys()):
                func_name = action_request["function"]
                args = action_request["arguments"]

        func_call = await branch._action_manager.invoke(action_request)
        if func_call is None:
            # Possibly no matching function was found or a log entry was returned
            logging.info("No function call result was produced.")
            return None

        branch._log_manager.log(Log.create(func_call))

        from lionagi.protocols.types import ActionRequest

        if not isinstance(action_request, ActionRequest):
            action_request = ActionRequest.create(
                function=func_name,
                arguments=args,
                sender=branch.id,
                recipient=func_call.func_tool.id,
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

    except Exception as e:
        if suppress_errors:
            logging.error(f"Error invoking action '{func_name}': {e}")
            return None
        raise e
