# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

E = TypeVar("E")


class Observer(ABC):
    """Base class for all observers.

    This abstract class should be inherited by any observer-like objects.
    """


class Manager(Observer):
    """Base class for all managers.

    This class extends the Observer base class and can be used to manage
    or oversee other objects or processes.
    """


class Relational(ABC):
    """Base class for objects that can be connected on a graph.

    This abstract class indicates that subclasses may form links or
    relationships in a graph structure.
    """


class Sendable(ABC):
    """Base class for sendable entities.

    Subclasses must define 'sender' and 'recipient' attributes.
    """

    sender = None
    recipient = None


class Observable(ABC):
    """Base class for observable entities.

    Subclasses must define an 'id' attribute.
    """

    id = None


class Communicatable(Observable):
    """Base class for communicatable objects.

    This class extends Observable and requires subclasses to define a
    'mailbox' attribute. Subclasses must implement the abstract methods
    for sending and receiving (both synchronous and asynchronous).
    """

    mailbox = None

    @abstractmethod
    def send(self, *args, **kwargs):
        """Send a message synchronously.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass

    @abstractmethod
    def receive(self, *args, **kwargs):
        """Receive a message synchronously.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass

    @abstractmethod
    def asend(self, *args, **kwargs):
        """Send a message asynchronously.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass

    @abstractmethod
    def areceive(self, *args, **kwargs):
        """Receive a message asynchronously.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass


class Collective(ABC, Generic[E]):
    """Abstract base class for collections of elements.

    Subclasses must implement methods for including and excluding elements.
    """

    @abstractmethod
    def include(self, *args, **kwargs):
        """Include elements into the collection.

        Args:
            *args: Positional arguments for inclusion logic.
            **kwargs: Keyword arguments for inclusion logic.
        """
        pass

    @abstractmethod
    def exclude(self, *args, **kwargs):
        """Exclude elements from the collection.

        Args:
            *args: Positional arguments for exclusion logic.
            **kwargs: Keyword arguments for exclusion logic.
        """
        pass


class Ordering(ABC, Generic[E]):
    """Abstract base class for defining element orderings.

    Subclasses must implement methods for including and excluding elements
    in an ordered sequence.
    """

    @abstractmethod
    def include(self, *args, **kwargs):
        """Include elements into the ordering.

        Args:
            *args: Positional arguments for inclusion logic.
            **kwargs: Keyword arguments for inclusion logic.
        """
        pass

    @abstractmethod
    def exclude(self, *args, **kwargs):
        """Exclude elements from the ordering.

        Args:
            *args: Positional arguments for exclusion logic.
            **kwargs: Keyword arguments for exclusion logic.
        """
        pass


# File: lionagi/protocols/generic/concepts.py
