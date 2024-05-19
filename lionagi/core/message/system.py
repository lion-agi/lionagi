from typing import Any
from ..collections.abc import Field
from .message import RoledMessage, MessageRole


class System(RoledMessage):

    system: str | Any | None = Field(None)

    def __init__(self, system=None, sender=None, recipient=None, **kwargs):
        if not system:
            if 'metadata' in kwargs and 'system' in kwargs['metadata']:
                system = kwargs['metadata'].pop('system')

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={"system_info": system},
            recipient=recipient or "N/A",
            system = system,
            **kwargs,
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.
        """
        return self.content["system_info"]
