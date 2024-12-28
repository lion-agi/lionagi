# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, TypeAlias

from pydantic import BaseModel, Field, field_serializer

from ..generic._id import ID, IDError
from ..generic.element import IDType, Observable

__all__ = (
    "Communicatable",
    "Sendable",
    "MessageRole",
    "MessageFlag",
    "MessageField",
    "MESSAGE_FIELDS",
    "validate_sender_recipient",
)


class MessageRole(str, Enum):
    """
    Enum for possible roles a message can assume in a conversation.

    These roles define the nature and purpose of messages in the system:
    - SYSTEM: System-level messages providing context or instructions
    - USER: Messages from users making requests or providing input
    - ASSISTANT: Messages from AI assistants providing responses
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSET = "unset"
    ACTION = "action"


class MessageFlag(str, Enum):
    """
    Enum to signal special message construction modes.

    These flags are used internally to control message instantiation:
    - MESSAGE_CLONE: Signal to create a clone of an existing message
    - MESSAGE_LOAD: Signal to load a message from stored data
    """

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class Communicatable(ABC):

    @abstractmethod
    def send(self, *args, **kwargs):
        pass

    @abstractmethod
    def receive(self, *args, **kwargs):
        pass


SenderRecipient: TypeAlias = ID.Ref | MessageRole | str


class Sendable(BaseModel):

    sender: SenderRecipient = Field(
        default=MessageRole.UNSET,
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: SenderRecipient = Field(
        default=MessageRole.UNSET,
        title="Recipient",
        description="The ID of the recipient node or a role.",
    )

    @field_serializer("sender", "recipient")
    def _serialize_sender_recipient(cls, value: SenderRecipient) -> str:
        return str(value)


class MessageField(str, Enum):

    TIMESTAMP = "timestamp"
    LION_CLASS = "lion_class"
    ROLE = "role"
    CONTENT = "content"
    ID = "id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"


MESSAGE_FIELDS = [i.value for i in MessageField.__members__.values()]


def validate_sender_recipient(value: Any, /) -> SenderRecipient:
    """
    Validate sender and recipient fields for mail-like communication.

    Args:
        value: The value to validate

    Returns:
        Union[IDType, Literal]: Valid sender/recipient value

    Raises:
        ValueError: If value is not a valid sender or recipient
    """
    if isinstance(value, MessageRole | MessageFlag):
        return value

    if isinstance(value, IDType):
        return value

    if isinstance(value, Observable):
        return value.id

    if value is None:
        return MessageRole.UNSET

    if value in ["system", "user", "unset", "assistant"]:
        return MessageRole(value)

    if value in ["MESSAGE_CLONE", "MESSAGE_LOAD"]:
        return MessageFlag(value)

    try:
        return ID.get_id(value)
    except IDError as e:
        raise ValueError("Invalid sender or recipient") from e
