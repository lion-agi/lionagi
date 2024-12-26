from abc import ABC

from lionagi.utils import EventStatus

from .element import Element

__all__ = (
    "Observer",
    "Event",
    "Condition",
)


class Observer(ABC):
    """Base class for all observers."""

    pass


class Condition(ABC):
    """Base class for all conditions."""

    async def apply(self, *args, **kwargs) -> bool:
        raise NotImplementedError


class Event(Element):
    """Base class for all events."""

    status: EventStatus = EventStatus.PENDING

    @property
    def request(self) -> dict:
        return {}

    async def invoke(self) -> None:
        raise NotImplementedError
