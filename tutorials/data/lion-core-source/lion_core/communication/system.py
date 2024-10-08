from typing import Any

from lionfuncs import time
from typing_extensions import override

from lion_core.communication.message import (
    MessageFlag,
    MessageRole,
    RoledMessage,
)
from lion_core.generic.note import Note

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def format_system_content(
    system_datetime: bool | str | None,
    system_message: str,
) -> Note:
    """Format the system content with optional datetime information."""
    system_message = system_message or DEFAULT_SYSTEM
    if not system_datetime:
        return Note(system_info=str(system_message))
    if isinstance(system_datetime, str):
        return Note(system_info=f"{system_message}. Date: {system_datetime}")
    if system_datetime:
        date = time(type_="iso", timespec="minutes")
        return Note(system_info=f"{system_message}. System Date: {date}")


class System(RoledMessage):
    """Represents a system message in a language model conversation."""

    @override
    def __init__(
        self,
        system: Any | MessageFlag = None,
        sender: str | None | MessageFlag = None,
        recipient: str | None | MessageFlag = None,
        system_datetime: bool | str | None | MessageFlag = None,
        protected_init_params: dict | None = None,
    ):
        """Initialize a System message instance."""
        if all(
            x == MessageFlag.MESSAGE_LOAD
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(**protected_init_params)
            return

        if all(
            x == MessageFlag.MESSAGE_CLONE
            for x in [system, sender, recipient, system_datetime]
        ):
            super().__init__(role=MessageRole.SYSTEM)
            return

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content=format_system_content(
                system_datetime=system_datetime, system_message=system
            ),
            recipient=recipient or "N/A",
        )

    @property
    def system_info(self) -> Any:
        """Retrieve the system information stored in the message content."""
        return self.content.get("system_info", None)


# File: lion_core/communication/system.py
