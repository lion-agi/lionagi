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
    "Event",
    "Condition",
    "Execution",
    "EventStatus",
)


class Condition(ABC):
    """Base class for all conditions."""

    async def apply(self, *args, **kwargs) -> bool:
        """Apply the condition asynchronously.

        This method must be implemented by subclasses. It should evaluate a
        certain condition and return a boolean indicating whether the condition
        is met.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if the condition is satisfied, False otherwise.

        Raises:
            NotImplementedError: If not overridden by subclasses.
        """
        raise NotImplementedError


class Execution(DataClass):
    """Represents the execution state of an event.

    This class holds details about the status, duration, response, and any
    errors encountered during the event execution.
    """

    __slots__ = ("status", "duration", "response", "error")

    def __init__(
        self,
        duration: float = None,
        response: Any = None,
        status: EventStatus = EventStatus.PENDING,
        error: str | None = None,
    ):
        """Initialize the Execution instance.

        Args:
            duration (float | None, optional):
                The time duration of the event's execution.
            response (Any, optional):
                The response data associated with the event's execution.
            status (EventStatus, optional):
                The status of the execution. Defaults to EventStatus.PENDING.
            error (str | None, optional):
                Any error message or details if the execution fails or
                encounters issues.
        """
        self.status = status
        self.duration = duration
        self.response = response
        self.error = error

    def __str__(self) -> str:
        """Return a user-friendly string representation of the execution.

        Returns:
            str: A summary of execution status, duration, response, and error.
        """
        return (
            f"Execution(status={self.status}, duration={self.duration}, "
            f"response={self.response}, error={self.error})"
        )

    __repr__ = __str__


class Event(Element):
    """Base class for all events.

    An event extends the basic `Element` with execution details and provides
    properties to manage the event's status, response, and invocation logic.
    """

    execution: Execution = Field(default_factory=Execution)

    @property
    def response(self) -> Any:
        """Any: Get or set the response associated with the event."""
        return self.execution.response

    @response.setter
    def response(self, value: Any) -> None:
        self.execution.response = value

    @property
    def status(self) -> EventStatus:
        """EventStatus: Get or set the current status of the event."""
        return self.execution.status

    @status.setter
    def status(self, value: EventStatus) -> None:
        self.execution.status = value

    @property
    def request(self) -> dict:
        """dict: Return the request data associated with the event.

        Subclasses can override this property to provide more specific
        request data.
        """
        return {}

    async def invoke(self) -> None:
        """Invoke the event asynchronously.

        Subclasses should implement the logic for how the event is triggered
        or executed. By default, this raises a NotImplementedError.

        Raises:
            NotImplementedError: Always, unless overridden by subclasses.
        """
        raise NotImplementedError

    def to_dict(self) -> dict:
        """Convert the event into a dictionary.

        The returned dictionary contains the ID, class name (for
        round-trip deserialization), status, duration, response, and
        any error message.

        Returns:
            dict: A dictionary representation of the event.
        """
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
        """Restore an event from a dictionary.

        Events are not intended to be restored once completed, so this
        method raises a NotImplementedError by default.

        Args:
            data (dict): The dictionary from which to reconstruct the event.
            **kwargs: Additional keyword arguments.

        Raises:
            NotImplementedError:
                Indicates that events cannot be recreated.
        """
        raise NotImplementedError(
            "An event cannot be recreated. Once it's done, it's done."
        )

    def to_log(self) -> Log:
        """Convert the event into a Log object.

        Returns:
            Log: A Log object containing the event as its content.
        """
        return Log(content=self)


# File: lionagi/protocols/generic/event.py
