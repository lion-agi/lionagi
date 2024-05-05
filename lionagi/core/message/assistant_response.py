from typing import Any
from .message import RoledMessage, MessageRole


class AssistantResponse(RoledMessage):

    def __init__(
        self,
        response: Any = None,
        sender: str | None = None,
        recipient: str | None = None,
    ):

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            content={"assistant_response": response},
            recipient=recipient,
        )
