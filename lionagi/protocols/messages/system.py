# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `System` class, representing system-level instructions or
settings that guide the AI's behavior from a privileged role.
"""

from datetime import datetime
from typing import Any, NoReturn

from pydantic import JsonValue
from typing_extensions import Self, override

from .base import SenderRecipient
from .message import MessageRole, RoledMessage, Template, jinja_env

__all__ = ("System",)


def format_system_content(
    system_datetime: bool | str | None,
    system_message: str,
) -> dict:
    """
    Insert optional datetime string into the system message content.

    Args:
        system_datetime (bool|str|None):
            If True, embed current time. If str, use as time. If None, omit.
        system_message (str):
            The main system message text.

    Returns:
        dict: The combined system content.
    """
    content: dict = {"system_message": system_message}
    if system_datetime:
        if isinstance(system_datetime, str):
            content["system_datetime"] = system_datetime
        else:
            content["system_datetime"] = datetime.now().isoformat(
                timespec="minutes"
            )
    return content


class System(RoledMessage):
    """
    A specialized message that sets a *system-level* context or policy.
    Usually the first in a conversation, instructing the AI about general
    constraints or identity.
    """

    template: str | Template | None = jinja_env.get_template(
        "system_message.jinja2"
    )

    @override
    @classmethod
    def create(
        cls,
        system_message="You are a helpful AI assistant. Let's think step by step.",
        system_datetime=None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        template=None,
        system: Any = None,
        **kwargs,
    ) -> Self:
        """
        Construct a system message with optional datetime annotation.

        Args:
            system_message (str):
                The main text instructing the AI about behavior/identity.
            system_datetime (bool|str, optional):
                If True or str, embed a time reference. If str, it is used directly.
            sender (SenderRecipient, optional):
                Typically `MessageRole.SYSTEM`.
            recipient (SenderRecipient, optional):
                Typically `MessageRole.ASSISTANT`.
            template (Template|str|None):
                An optional custom template for rendering.
            system (Any):
                Alias for `system_message` (deprecated).
            **kwargs:
                Additional content merged into the final dict.

        Returns:
            System: A newly created system-level message.
        """
        if system and system_message:
            raise ValueError(
                "Cannot provide both system and system_message arguments."
                "as they are alias, and `system` is deprecated"
            )
        system_message = system_message or system

        content = format_system_content(
            system_datetime=system_datetime, system_message=system_message
        )
        content.update(kwargs)
        params = {
            "role": MessageRole.SYSTEM,
            "content": content,
            "sender": sender or MessageRole.SYSTEM,
            "recipient": recipient or MessageRole.ASSISTANT,
        }
        if template:
            params["template"] = template
        return cls(**params)

    def update(
        self,
        system_message: JsonValue = None,
        sender: SenderRecipient = None,
        recipient: SenderRecipient = None,
        system_datetime: bool | str = None,
        template: Template | str | None = None,
        **kwargs,
    ) -> NoReturn:
        """
        Adjust fields of this system message.

        Args:
            system_message (JsonValue):
                New system message text.
            sender (SenderRecipient):
                Updated sender or role.
            recipient (SenderRecipient):
                Updated recipient or role.
            system_datetime (bool|str):
                If set, embed new datetime info.
            template (Template|str|None):
                New template override.
            **kwargs:
                Additional fields for self.content.
        """
        if any([system_message, system_message]):
            self.content = format_system_content(
                system_datetime=system_datetime, system_message=system_message
            )
        super().update(
            sender=sender, recipient=recipient, template=template, **kwargs
        )


# File: lionagi/protocols/messages/system.py
