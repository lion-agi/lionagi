# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


class Observable(ABC):
    """
    Abstract base class for objects that can be uniquely identified and tracked.

    All Observable objects must have a unique identifier (ln_id) that allows them
    to be tracked and referenced within the Lion system.
    """

    ln_id: str


T = TypeVar("T", bound=Observable)


class Container(ABC, Generic[T]):
    """
    Abstract base class for objects that can contain Observable items.

    Generic type T must be a subclass of Observable.
    """

    pass


class Ordering(ABC, Generic[T]):
    """
    Abstract base class for objects that maintain an ordered collection of items.

    Generic type T must be a subclass of Observable.
    """

    pass


class Communicatable(ABC):
    """
    Abstract base class for objects that can participate in communication.

    Defines the interface for objects that can send and receive messages within
    the Lion system.
    """

    pass


class Relational(Observable):

    pass


class Event(ABC):

    @abstractmethod
    async def invoke(self, *args, **kwargs) -> Any:
        pass


class Condition(ABC):

    @abstractmethod
    async def apply(self, *args, **kwargs) -> bool:
        pass


class Structure(ABC):
    pass


class ItemError(Exception):
    """Base exception for errors related to framework items."""

    def __init__(
        self,
        message: str = "Item error.",
        item_id: str | None = None,
    ):
        self.item_id = item_id
        item_info = f" Item ID: {item_id}" if item_id else ""
        super().__init__(f"{message}{item_info}")


class ItemNotFoundError(ItemError):
    """Exception raised when an item is not found."""

    def __init__(
        self,
        message: str = "Item not found.",
        item_id: str | None = None,
    ):
        super().__init__(message, item_id)


class ItemExistsError(ItemError):
    """Exception raised when an item already exists."""

    def __init__(
        self,
        message: str = "Item already exists.",
        item_id: str | None = None,
    ):
        super().__init__(message, item_id)


class RelationError(Exception):
    """Base exception for errors related to framework relations."""

    def __init__(self, message: str = "Relation error."):
        super().__init__(message)


__all__ = [
    "Observable",
    "Container",
    "Ordering",
    "Communicatable",
    "ItemError",
    "ItemNotFoundError",
    "ItemExistsError",
    "Relational",
    "Event",
    "Condition",
    "Structure",
    "RelationError",
]
