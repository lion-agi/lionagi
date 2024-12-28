# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import NoReturn, Self

from pydantic import JsonValue
from typing_extensions import override

from .base import SenderRecipient, validate_sender_recipient
from .message import MessageRole, RoledMessage, Template, jinja_env

__all__ = ("System",)


def format_system_content(
    system_datetime: bool | str | None,
    system_message: str,
) -> dict:
    """
    Format system message content with optional datetime information.

    Args:
        system_datetime: Flag or string for datetime inclusion
        system_message: The system message content

    Returns:
        Note: Formatted system content
    """
    content: dict = {"system": system_message}
    if system_datetime:
        if isinstance(system_datetime, str):
            content["system_datetime"] = system_datetime
        else:
            content["system_datetime"] = datetime.now().isoformat(
                timespec="minutes"
            )
    return content


class System(RoledMessage):

    template: str | Template | None = jinja_env.get_template("system.jinja")

    @override
    @classmethod
    def create(
        cls,
        system_message="You are a helpful AI assistant. Let's think step by step.",
        system_datetime=None,
        **kwargs,
    ) -> Self:
        """
        Create a new system message.

        Args:
            system_message: The system message content
            system_datetime: Optional datetime flag or string

        Returns:
            System: The new system message
        """
        content = format_system_content(
            system_datetime=system_datetime, system_message=system_message
        )
        content.update(kwargs)
        return cls(role=MessageRole.SYSTEM, content=content)

    def update(
        self,
        system_message: JsonValue = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        system_datetime: bool | str = None,
        **kwargs,
    ) -> NoReturn:
        """
        Update the system message components.

        Args:
            system: New system message content
            sender: New sender
            recipient: New recipient
            system_datetime: New datetime flag or string
        """
        if any([system_message, system_message]):
            self.content = format_system_content(
                system_datetime=system_datetime, system_message=system_message
            )
        super().update(sender=sender, recipient=recipient, **kwargs)
