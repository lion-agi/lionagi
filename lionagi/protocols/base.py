# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Generator, Mapping, Sequence
from enum import Enum
from typing import Any, Generic, NoReturn, TypeAlias, TypeVar
from uuid import uuid4

# A generic type var bound to Observable
T = TypeVar("T", bound="Observable")


__all__ = (
    "Observable",
    "Ordering",
    "Container",
    "IDType",
    "ID",
    "MessageRole",
    "EventStatus",
    "MessageFlag",
    "MessageField",
    "MESSAGE_FIELDS",
    "DEFAULT_SYSTEM",
    "Event",
    "Condition",
    "Observer",
    "Manager",
    "T",
)


class EventStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, Enum):
    """Defines possible roles a message can have in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSPECIFIED = "unspecified"


class MessageFlag(str, Enum):
    """
    Enum to signal special message construction modes.

    These flags are used internally to control message instantiation:
    - MESSAGE_CLONE: Signal to create a clone of an existing message
    - MESSAGE_LOAD: Signal to load a message from stored data
    """

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class MessageField(str, Enum):
    """
    Enum for standard message fields.

    Defines the standard fields that can be present in a message:
    - TIMESTAMP: Message creation timestamp
    - LION_CLASS: Class identifier for LION system
    - ROLE: Message role (system/user/assistant)
    - CONTENT: Message content
    - id: Unique message identifier
    - SENDER: Message sender
    - RECIPIENT: Message recipient
    - METADATA: Additional message metadata
    """

    TIMESTAMP = "timestamp"
    LION_CLASS = "lion_class"
    ROLE = "role"
    CONTENT = "content"
    id = "id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"


MESSAGE_FIELDS = [i.value for i in MessageField.__members__.values()]

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


class Observable(ABC):
    """An interface indicating an object can be identified by a stable ID."""

    id: IDType

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Convert the object to a dictionary."""
        return {}


class Ordering(ABC, Generic[T]):
    """Base for objects maintaining ordered collections."""

    pass


class Container(ABC, Generic[T]):
    """Base for objects that can contain Observable items."""

    pass


class Communicatable(ABC):
    """An interface indicating an object can be communicated with."""

    pass


class Event(ABC):
    """Base for events in the system."""

    @abstractmethod
    async def invoke(self) -> NoReturn:
        raise NotImplementedError("Action must be subclassed to invoke.")


class Condition(Event):
    """Base for conditions in the system."""

    @abstractmethod
    async def apply(self) -> NoReturn:
        raise NotImplementedError("Action must be subclassed to invoke.")


class Observer(ABC):
    pass


class Manager(Observable):
    pass


class IDType:
    """
    A validated ID string.

    A simplified ID type: a 32-char hex string. This provides stable,
    unique references. If needed, can be extended, but we keep it simple here.
    """

    PATTERN = re.compile(r"^[0-9a-f]{32}$")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("IDType value must be a string.")
        if not self.PATTERN.match(value):
            raise ValueError(
                "Invalid ID format. Must be a 32-char hex string."
            )
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"IDType('{self._value}')"

    __slots__ = ("_value", "PATTERN")


class ID(Generic[T]):
    """
    Utilities for ID generation and handling.

    Provides:
    - A stable generate() method for new IDs.
    - is_id() to check if a string is a valid ID.
    - get_id() to extract the ID from an Observable or a string.

    This is enough to handle stable references in a concurrency-friendly environment.
    """

    # For functions that accept either ID or item
    Ref: TypeAlias = IDType | T  # type: ignore
    ID: TypeAlias = IDType  # type: ignore

    Item: TypeAlias = T  # type: ignore
    # For collections
    IDSeq: TypeAlias = Sequence[IDType] | Ordering[IDType]
    ItemSeq: TypeAlias = (  # type: ignore
        Sequence[T] | Mapping[IDType, T] | Container[T]
    )
    RefSeq: TypeAlias = IDSeq | ItemSeq
    SenderRecipient: TypeAlias = MessageRole | IDType | MessageFlag

    @staticmethod
    def generate() -> IDType:
        # Generate a 32-char hex string (128 bits of randomness)
        return IDType(uuid4().hex[:32])

    @staticmethod
    def is_id(item: Any) -> bool:
        if isinstance(item, IDType):
            return True
        if isinstance(item, str):
            return bool(IDType.PATTERN.match(item))
        return False

    @staticmethod
    def get_id(item: T | IDType | str) -> IDType:
        # If Observable, return item.id
        if isinstance(item, Observable):
            return item.id

        # If IDType, return it
        if isinstance(item, IDType):
            return item

        # If str, validate and convert
        if isinstance(item, str):
            return IDType(item)

        raise TypeError("Item does not contain or represent a valid ID.")


def to_list_type(value: Any, /) -> list[Any]:
    """Convert input to a list format"""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if ID.is_id(value) else []
    if isinstance(value, Observable):
        return [value]
    if hasattr(value, "values") and callable(value.values):
        return list(value.values())
    if isinstance(value, list | tuple | set | deque | Generator):
        return list(value)
    return [value]


def validate_order(value: Any, /) -> list[str]:
    """Validate and standardize order representation"""

    try:
        return [ID.get_id(item) for item in to_list_type(value)]
    except Exception as e:
        raise ValueError("Must only contain valid Lion IDs.") from e


def validate_sender_recipient(value) -> MessageRole | IDType | MessageFlag:
    if isinstance(value, MessageRole | MessageFlag):
        return value
    if isinstance(value, IDType):
        return value
    try:
        return ID.get_id(value)
    except Exception as e:
        raise ValueError(f"Invalid sender or recipient: {value}") from e
