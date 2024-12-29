# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from typing import Any

from pydantic import Field

from lionagi.utils import DataClass, EventStatus

from .element import Element
from .log import Log

__all__ = (
    "Observer",
    "Event",
    "Condition",
    "Execution",
    "EventStatus",
)


class Observer(ABC):
    """Base class for all observers."""

    pass


class Condition(ABC):
    """Base class for all conditions."""

    async def apply(self, *args, **kwargs) -> bool:
        raise NotImplementedError


class Execution(DataClass):

    def __init__(
        self,
        status: EventStatus,
        duration: float,
        response: Any,
        error: str | None = None,
    ):
        self.status = status
        self.duration = duration
        self.response = response
        self.error = error

    def __str__(self) -> str:
        return f"Execution(status={self.status}, duration={self.duration}, response={self.response}, error={self.error})"

    __repr__ = __str__

    __slots__ = ("status", "duration", "response", "error")


class Event(Element):
    """Base class for all events."""

    execution: Execution | None = Field(None, exclude=True)

    @property
    def status(self) -> EventStatus:
        return self.execution.status

    @status.setter
    def status(self, value: EventStatus) -> None:
        self.execution.status = value

    @property
    def request(self) -> dict:
        return {}

    async def invoke(self) -> None:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "lion_class": self.class_name(),
            "status": self.status.value,
            "duration": self.execution.duration,
            "response": self.execution.response,
            "error": self.execution.error,
        }

    @classmethod
    def from_dict(cls, data, **kwargs):
        raise NotImplementedError(
            "An event cannot be recreated. Once it's done, it's done."
        )

    def to_log(self) -> Log:
        return Log(content=self)
