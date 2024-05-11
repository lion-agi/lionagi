from typing import Any
from .message import RoledMessage, MessageRole


class AssistantResponse(RoledMessage):

    def __init__(
        self,
        assistant_response: Any = None,
        sender: str | None = None,
        recipient: str | None = None,
    ):

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            content={"assistant_response": assistant_response["content"]},
            recipient=recipient,
        )
