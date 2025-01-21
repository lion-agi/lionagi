# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""Foundational types and enums for the message system.

This module provides the core types and enumerations that define message roles,
flags, and field names in LionAGI's message system. It includes:

- MessageRole: Enum for system, user, and assistant roles
- MessageFlag: Internal flags for message states
- MessageField: Standard field names used in messages
- SenderRecipient: Type alias for message endpoints
- Helper functions for validating sender/recipient fields

These components form the foundation for all message-based communication
in the system, whether between users and AI, or between different AI agents.
"""

from enum import Enum
from typing import Any, TypeAlias

from ..generic.element import ID, IDError, IDType, Observable

__all__ = (
    "MessageRole",
    "MessageFlag",
    "MessageField",
    "MESSAGE_FIELDS",
    "validate_sender_recipient",
)


class MessageRole(str, Enum):
    """Predefined roles for conversation participants.

    These roles define the different actors in a conversation:
    - SYSTEM: System-level messages that set context or constraints
    - USER: Messages from human users or external agents
    - ASSISTANT: Responses from AI models or assistants
    - UNSET: Default/unspecified role
    - ACTION: Messages related to tool/function execution

    Example:
        >>> role = MessageRole.USER
        >>> print(role)  # "user"
        >>> role == "user"  # True
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSET = "unset"
    ACTION = "action"


class MessageFlag(str, Enum):
    """Internal flags for message state tracking.

    These flags help track special states of messages:
    - MESSAGE_CLONE: Indicates this message is a copy of another
    - MESSAGE_LOAD: Indicates this message was loaded from storage

    These are primarily used internally by the message system to
    maintain proper state and relationships between messages.
    """

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


SenderRecipient: TypeAlias = IDType | MessageRole | str
"""
A union type indicating that a sender or recipient could be:
- A lionagi IDType,
- A string-based role or ID,
- A specific enum role from `MessageRole`.
"""


class MessageField(str, Enum):
    """Standard field names used across message objects.

    These field names are used consistently throughout the message system:
    - CREATED_AT: Message creation timestamp
    - ROLE: The message's role (system/user/assistant)
    - CONTENT: The actual message content
    - ID: Unique message identifier
    - SENDER: Who sent the message
    - RECIPIENT: Who should receive the message
    - METADATA: Additional message data

    This enum ensures consistent field naming across the codebase.
    """

    CREATED_AT = "created_at"
    ROLE = "role"
    CONTENT = "content"
    ID = "id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"


MESSAGE_FIELDS = [i.value for i in MessageField.__members__.values()]


def validate_sender_recipient(value: Any, /) -> SenderRecipient:
    """
    Normalize a sender/recipient value into a recognized type.

    Args:
        value (Any): Input to interpret as a role or ID.

    Returns:
        SenderRecipient: A validated and normalized entity.

    Raises:
        ValueError: If the input cannot be recognized as a role or ID.
    """
    if isinstance(value, MessageRole | MessageFlag):
        return value

    if isinstance(value, IDType):
        return value

    if isinstance(value, Observable):
        return value.id

    if value is None:
        return MessageRole.UNSET

    if value in ["system", "user", "unset", "assistant", "action"]:
        return MessageRole(value)

    if value in ["MESSAGE_CLONE", "MESSAGE_LOAD"]:
        return MessageFlag(value)

    try:
        return ID.get_id(value)
    except IDError as e:
        raise ValueError("Invalid sender or recipient") from e


# File: lionagi/protocols/messages/base.py
