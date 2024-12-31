# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Any

from .element import Element

__all__ = (
    "EventStatus",
    "Execution",
    "Event",
)


class EventStatus(str, Enum):
    """Status states for tracking action execution progress.

    Attributes:
        PENDING: Initial state before execution starts
        PROCESSING: Action is currently being executed
        COMPLETED: Action completed successfully
        FAILED: Action failed during execution
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Execution:
    """Execution state of an event."""

    __slots__ = ("status", "duration", "response", "error")

    def __init__(
        self,
        duration: float | None = None,
        response: Any = None,
        status: EventStatus = EventStatus.PENDING,
        error: str | None = None,
    ):
        self.status = status
        self.duration = duration
        self.response = response
        self.error = error

    def __str__(self) -> str:
        return (
            f"Execution(status={self.status}, duration={self.duration}, "
            f"response={self.response}, error={self.error})"
        )


class Event(Element):
    """Event extends Element with an execution state."""

    def __init__(self, execution: Execution | None = None, **kwargs):
        super().__init__(**kwargs)
        self.execution = execution if execution else Execution()

    @property
    def response(self) -> Any:
        return self.execution.response

    @response.setter
    def response(self, val: Any) -> None:
        self.execution.response = val

    @property
    def status(self) -> EventStatus:
        return self.execution.status

    @status.setter
    def status(self, val: EventStatus) -> None:
        self.execution.status = val

    @property
    def request(self) -> dict:
        return {}

    async def invoke(self) -> None:
        raise NotImplementedError("Override in subclass.")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "status": self.status.value,
                "duration": self.execution.duration,
                "response": self.execution.response,
                "error": self.execution.error,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        raise NotImplementedError("Cannot recreate an event once it's done.")


# File: protocols/generic/event.py
