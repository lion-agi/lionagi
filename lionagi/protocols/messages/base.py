# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

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

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSET = "unset"
    ACTION = "action"


class MessageFlag(str, Enum):

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


SenderRecipient: TypeAlias = IDType | MessageRole | str


class MessageField(str, Enum):

    CREATED_AT = "created_at"
    ROLE = "role"
    CONTENT = "content"
    ID = "id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"


MESSAGE_FIELDS = [i.value for i in MessageField.__members__.values()]


def validate_sender_recipient(value: Any, /) -> SenderRecipient:
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
