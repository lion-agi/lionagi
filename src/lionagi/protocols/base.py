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
    """Event execution status states."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, Enum):
    """Message participant roles in conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    UNSPECIFIED = "unspecified"


class MessageFlag(str, Enum):
    """Internal flags for message construction control."""

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class MessageField(str, Enum):
    """Standard message field identifiers."""

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
    """Interface for objects with stable ID identification."""

    id: IDType

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Convert the object to a dictionary format."""
        return {}


class Ordering(ABC, Generic[T]):
    """Base for ordered collection management."""

    pass


class Container(ABC, Generic[T]):
    """Base for Observable item containers."""

    pass


class Communicatable(ABC):
    """Interface for communication-capable objects."""

    pass


class Event(ABC):
    """Base for system events."""

    @abstractmethod
    async def invoke(self) -> NoReturn:
        raise NotImplementedError("Action must be subclassed to invoke.")


class Condition(Event):
    """Base for system conditions."""

    @abstractmethod
    async def apply(self) -> NoReturn:
        raise NotImplementedError("Action must be subclassed to invoke.")


class Observer(ABC):
    """Base for system observers."""

    pass


class Manager(Observer):
    """Base for system managers."""

    pass


class IDType:
    """32-character hexadecimal ID validation and handling."""

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

    __slots__ = "_value"


class ID(Generic[T]):
    """ID generation and reference handling utilities."""

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
        """Generate new unique ID."""
        return IDType(uuid4().hex[:32])

    @staticmethod
    def is_id(item: Any) -> bool:
        """Check if item is valid ID."""
        if isinstance(item, IDType):
            return True
        if isinstance(item, str):
            return bool(IDType.PATTERN.match(item))
        return False

    @staticmethod
    def get_id(item: T | IDType | str) -> IDType:
        """Extract ID from item or validate ID string."""
        if isinstance(item, Observable):
            return item.id
        if isinstance(item, IDType):
            return item
        if isinstance(item, str):
            return IDType(item)
        raise TypeError("Item does not contain or represent a valid ID.")


def to_list_type(value: Any, /) -> list[Any]:
    """Convert input to list format, handling various input types."""
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


def validate_order(value: Any, /) -> list[IDType]:
    """Validate and standardize order representation"""
    try:
        return [ID.get_id(item) for item in to_list_type(value)]
    except Exception as e:
        raise ValueError("Must only contain valid Lion IDs.") from e


def validate_sender_recipient(value) -> ID.SenderRecipient:
    """Validate and standardize sender/recipient identifiers."""
    if isinstance(value, ID.SenderRecipient):
        return value
    try:
        return ID.get_id(value)
    except Exception as e:
        raise ValueError(f"Invalid sender or recipient: {value}") from e


# File: lionagi/protocols/base.py
