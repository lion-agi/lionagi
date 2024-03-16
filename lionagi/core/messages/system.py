from lionagi.core.messages.base.base_message import BaseMessage


class System(BaseMessage):
    """
    Represents a system-related message, a specialized subclass of Message.

    Designed for messages containing system information, this class sets the message role to 'system'.
    """

    def __init__(
        self, system: dict | list | str, sender: str | None = None, name=None
    ) -> None:
        super().__init__(
            role="system", sender=sender or "system", content={"system_info": system}
        )
        self.name = name

    @property
    def system(self):
        return self.content["system_info"]

    @system.setter
    def system(self, value):
        self.content["system_info"] = value
