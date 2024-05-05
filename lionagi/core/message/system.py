from .message import RoledMessage, MessageRole


class System(RoledMessage):

    def __init__(self, system_info: any, sender=None, recipient=None):

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={"system_info": system_info},
            recipient=recipient or "N/A",
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.
        """
        return self.content["system_info"]
