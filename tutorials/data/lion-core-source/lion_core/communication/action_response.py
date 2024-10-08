from typing import Any

from lionabc.exceptions import LionValueError
from typing_extensions import override

from lion_core.communication.action_request import ActionRequest
from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.generic.note import Note


def prepare_action_response_content(
    action_request: ActionRequest,
    func_output: Any,
) -> Note:
    """Prepare the content for an action response."""
    if action_request.is_responded:
        raise LionValueError("Action request already responded to")

    dict_ = action_request.request_dict
    dict_["output"] = func_output
    content = Note(action_request_id=action_request.ln_id)
    content["action_response"] = dict_
    return content


class ActionResponse(RoledMessage):
    """Represents a response to an action request in the system."""

    @override
    def __init__(
        self,
        action_request: ActionRequest | MessageFlag,
        sender: Any | MessageFlag,
        func_output: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ) -> None:
        """Initialize an ActionResponse instance.

        Args:
            action_request: The original action request to respond to.
            sender: The sender of the action response.
            func_output: The output from the function in the request.
            protected_init_params: Protected initialization parameters.
        """
        message_flags = [
            action_request,
            sender,
            func_output,
        ]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",  # sender is the actionable component
            recipient=action_request.sender,
            content=prepare_action_response_content(
                action_request=action_request,
                func_output=func_output,
            ),
        )
        self.update_request(
            action_request=action_request,
            func_output=func_output,
        )

    @property
    def func_output(self) -> Any:
        """Get the function output from the action response."""
        return self.content.get(["action_response", "output"])

    @property
    def response_dict(self) -> dict[str, Any]:
        """Get the action response as a dictionary."""
        return self.content.get("action_response", {})

    @property
    def action_request_id(self) -> str | None:
        """Get the ID of the corresponding action request."""
        return self.content.get("action_request_id", None)

    def update_request(
        self,
        action_request: ActionRequest,
        func_output: Any,
    ) -> None:
        """Update the action response with new request and output.

        Args:
            action_request: The original action request being responded to.
            func_output: The output from the function in the request.
        """
        self.content = prepare_action_response_content(
            action_request=action_request,
            func_output=func_output,
        )
        action_request.content.set(
            ["action_response_id"],
            self.ln_id,
        )


# File: lion_core/communication/action_response.py
