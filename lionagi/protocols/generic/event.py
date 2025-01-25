# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Any

from pydantic import Field, field_serializer

from .element import Element

__all__ = (
    "EventStatus",
    "Execution",
    "Event",
)


class EventStatus(str, Enum):
    """Status states for tracking action execution progress.

    Attributes:
        PENDING: Initial state before execution starts.
        PROCESSING: Action is currently being executed.
        COMPLETED: Action completed successfully.
        FAILED: Action failed during execution.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Execution:
    """Represents the execution state of an event.

    Attributes:
        status (`EventStatus`): The current status of the event execution.
        duration (float | None): Time (in seconds) the execution took,
            if known.
        response (Any): The result or output of the execution, if any.
        error (str | None): An error message if the execution failed.
    """

    __slots__ = ("status", "duration", "response", "error")

    def __init__(
        self,
        duration: float | None = None,
        response: Any = None,
        status: EventStatus = EventStatus.PENDING,
        error: str | None = None,
    ) -> None:
        """Initializes an execution instance.

        Args:
            duration (float | None): The duration of the execution.
            response (Any): The result or output of the execution.
            status (EventStatus): The current status (default is PENDING).
            error (str | None): An optional error message.
        """
        self.status = status
        self.duration = duration
        self.response = response
        self.error = error

    def __str__(self) -> str:
        """Returns a string representation of the execution state.

        Returns:
            str: A descriptive string indicating status, duration, response,
            and error.
        """
        return (
            f"Execution(status={self.status.value}, duration={self.duration}, "
            f"response={self.response}, error={self.error})"
        )


class Event(Element):
    """Extends Element with an execution state.

    Attributes:
        execution (Execution): The execution state of this event.
    """

    execution: Execution = Field(default_factory=Execution)
    streaming: bool = False

    @field_serializer("execution")
    def _serialize_execution(self, val: Execution) -> dict:
        """Serializes the Execution object into a dictionary.

        Args:
            val (Execution): The Execution object to serialize.

        Returns:
            dict: The serialized data containing status, duration, response,
            and error fields.
        """
        return {
            "status": val.status.value,
            "duration": val.duration,
            "response": val.response,
            "error": val.error,
        }

    @property
    def response(self) -> Any:
        """Gets or sets the execution response.

        Returns:
            Any: The current response for this event.
        """
        return self.execution.response

    @response.setter
    def response(self, val: Any) -> None:
        """Sets the execution response.

        Args:
            val (Any): The new response value for this event.
        """
        self.execution.response = val

    @property
    def status(self) -> EventStatus:
        """Gets or sets the event status.

        Returns:
            EventStatus: The current status of this event.
        """
        return self.execution.status

    @status.setter
    def status(self, val: EventStatus) -> None:
        """Sets the event status.

        Args:
            val (EventStatus): The new status for the event.
        """
        self.execution.status = val

    @property
    def request(self) -> dict:
        """Gets the request for this event.

        Returns:
            dict: An empty dictionary by default. Override in subclasses
            if needed.
        """
        return {}

    async def invoke(self) -> None:
        """Performs the event action asynchronously.

        Raises:
            NotImplementedError: This base method must be overridden by
            subclasses.
        """
        raise NotImplementedError("Override in subclass.")

    async def stream(self) -> None:
        """Performs the event action asynchronously, streaming results.

        Raises:
            NotImplementedError: This base method must be overridden by
            subclasses.
        """
        raise NotImplementedError("Override in subclass.")

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Not implemented. Events cannot be fully recreated once done.

        Args:
            data (dict): Event data (unused).

        Raises:
            NotImplementedError: Always, because recreating an event is
            disallowed.
        """
        raise NotImplementedError("Cannot recreate an event once it's done.")


# File: lionagi/protocols/generic/event.py
