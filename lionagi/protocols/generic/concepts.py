from abc import ABC, abstractmethod
from typing import Generic, TypeVar

E = TypeVar("E")


class Observer(ABC):
    """Base class for all observers."""

    pass


class Manager(Observer):
    """Base class for all managers."""

    pass


class Relational(ABC):
    """Base class for all relational elements."""

    pass


class Sendable(ABC):
    pass


class Observable(ABC):
    pass


class Communicatable(ABC):

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


class Collective(ABC, Generic[E]):
    """Abstract base class for collections of elements."""

    pass


class Ordering(ABC, Generic[E]):
    """Abstract base class for defining element orderings."""

    pass
