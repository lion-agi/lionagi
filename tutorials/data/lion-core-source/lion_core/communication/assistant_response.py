from typing import Any

from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)


class AssistantResponse(RoledMessage):
    """Represents a response from an assistant in the system."""

    @override
    def __init__(
        self,
        assistant_response: dict | MessageFlag,
        sender: Any | MessageFlag,
        recipient: Any | MessageFlag,
        protected_init_params: dict | None = None,
    ) -> None:
        """Initialize an AssistantResponse instance.

        Args:
            assistant_response: The content of the assistant's response.
            sender: The sender of the response, typically the assistant.
            recipient: The recipient of the response.
            protected_init_params: Optional parameters for protected init.
        """
        message_flags = [assistant_response, sender, recipient]

        if all(x == MessageFlag.MESSAGE_LOAD for x in message_flags):
            super().__init__(**protected_init_params)
            return

        if all(x == MessageFlag.MESSAGE_CLONE for x in message_flags):
            super().__init__(role=MessageRole.ASSISTANT)
            return

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender or "N/A",
            recipient=recipient,
        )
        if assistant_response:
            if isinstance(assistant_response, str):
                assistant_response = {"content": assistant_response}
            elif isinstance(assistant_response, dict):
                if "content" not in assistant_response:
                    assistant_response = {"content": assistant_response}
        else:
            assistant_response = {"content": ""}

        res = assistant_response.get("content", "")
        self.content["assistant_response"] = res

    @property
    def response(self) -> Any:
        """Return the assistant response content."""
        return self.content.get("assistant_response")


# File: lion_core/communication/assistant_response.py
