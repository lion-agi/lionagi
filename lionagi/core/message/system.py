from typing import Any

from ..collections.abc import Field
from .message import MessageRole, RoledMessage


class System(RoledMessage):
    """
    Represents a system message with system-related information.

    Inherits from `RoledMessage` and provides methods to manage system-specific content.

    Attributes:
        system (str | Any | None): The system information.
    """

    system: str | Any | None = Field(None)

    def __init__(self, system=None, sender=None, recipient=None, **kwargs):
        """
        Initializes the System message.

        Args:
            system (str or Any, optional): The system information.
            sender (str, optional): The sender of the message.
            recipient (str, optional): The recipient of the message.
            **kwargs: Additional fields to be added to the message content, must be JSON serializable.
        """
        if not system:
            if "metadata" in kwargs and "system" in kwargs["metadata"]:
                system = kwargs["metadata"].pop("system")

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content={"system_info": system},
            recipient=recipient or "N/A",
            system=system,
            **kwargs,
        )

    @property
    def system_info(self):
        """
        Retrieves the system information stored in the message content.

        Returns:
            Any: The system information.
        """
        return self.content["system_info"]

    def clone(self, **kwargs):
        """
        Creates a copy of the current System object with optional additional arguments.

        This method clones the current object, preserving its content.
        It also retains the original metadata, while allowing
        for the addition of new attributes through keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned object.

        Returns:
            System: A new instance of the object with the same content and additional keyword arguments.
        """
        import json

        system = json.dumps(self.system_info)
        system_copy = System(system=json.loads(system), **kwargs)
        system_copy.metadata["origin_ln_id"] = self.ln_id
        return system_copy
