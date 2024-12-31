# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

E = TypeVar("E")


__all__ = (
    "Observer",
    "Manager",
    "Relational",
    "Sendable",
    "Observable",
    "Communicatable",
    "Condition",
    "Collective",
    "Ordering",
)


class Observer(ABC):
    """Base for all observers."""

    pass


class Manager(Observer):
    """Base for all managers."""

    pass


class Relational(ABC):
    """Base for graph-connectable objects."""

    pass


class Sendable(ABC):
    """Sendable entities must define 'sender' and 'recipient'."""

    sender = None
    recipient = None


class Observable(ABC):
    """Observable entities must define 'id'."""

    id = None


class Communicatable(Observable):
    """Communicatable must define 'mailbox' and send/receive methods."""

    mailbox = None

    @abstractmethod
    def send(self, *args, **kwargs):
        pass

    @abstractmethod
    def receive(self, *args, **kwargs):
        pass

    @abstractmethod
    def asend(self, *args, **kwargs):
        pass

    @abstractmethod
    def areceive(self, *args, **kwargs):
        pass


class Condition(ABC):
    """Base for conditions."""

    @abstractmethod
    async def apply(self, *args, **kwargs) -> bool:
        pass


class Collective(ABC, Generic[E]):
    """Base for collections of elements."""

    @abstractmethod
    def include(self, *args, **kwargs):
        pass

    @abstractmethod
    def exclude(self, *args, **kwargs):
        pass


class Ordering(ABC, Generic[E]):
    """Base for element orderings."""

    @abstractmethod
    def include(self, *args, **kwargs):
        pass

    @abstractmethod
    def exclude(self, *args, **kwargs):
        pass


# File: protocols/generic/concepts.py
