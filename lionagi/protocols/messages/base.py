# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Holds foundational enumerations and types for messages, including
roles like `SYSTEM`, `USER`, and helper functions for validating
sender/recipient fields.
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
    """
    Predefined roles for conversation participants or message semantics.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSET = "unset"
    ACTION = "action"


class MessageFlag(str, Enum):
    """
    Internal flags for certain message states, e.g., clones or loads.
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
    """
    Common field names used in message objects.
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
