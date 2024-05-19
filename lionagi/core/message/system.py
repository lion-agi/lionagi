from typing import Any
from ..collections.abc import Field
from .message import RoledMessage, MessageRole


class System(RoledMessage):

    system: str | Any | None = Field(None)

    def __init__(self, system, sender=None, recipient=None, **kwargs):

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={"system_info": system},
            recipient=recipient or "N/A",
            **kwargs,
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.
        """
        return self.content["system_info"]
