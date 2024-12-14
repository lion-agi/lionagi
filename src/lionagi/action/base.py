# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any, NoReturn

from pydantic import Field, field_serializer

from ..protocols.base import Event, EventStatus
from ..protocols.log import Log
from ..protocols.models import BaseAutoModel

__all__ = ("Action",)


class Action(BaseAutoModel, Event):
    """
    Represents an executable action with status tracking and result management.

    Inherits from BaseAutoModel for data validation and Event for event protocol
    compatibility. Tracks execution status, timing, results, and potential errors.

    Attributes:
        status (EventStatus): Current status of the action. Defaults to PENDING.
        execution_time (float | None): Time taken for execution in seconds.
        execution_result (Any | None): Result of the action execution.
        error (str | None): Error message if execution failed.

    Methods:
        to_log(): Converts the action to a Log entry.

    Raises:
        NotImplementedError: When attempting to recreate from dictionary.
    """

    status: EventStatus = Field(
        default=EventStatus.PENDING, description="Current status of the action"
    )
    execution_time: float | None = Field(
        default=None, description="Execution duration in seconds"
    )
    execution_result: Any | None = Field(
        default=None, description="Result of the action execution"
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of action creation",
    )

    @field_serializer("status")
    def _serialize_status(self, value: EventStatus) -> str:
        """Serializes the EventStatus enum to string format."""
        return value.value

    def from_dict(self, *args: Any, **kwargs: Any) -> NoReturn:
        """
        Explicitly prevents recreation from dictionary.

        Raises:
            NotImplementedError: Always, as Actions cannot be recreated.
        """
        raise NotImplementedError(
            "An Action cannot be re-created from a dictionary."
        )

    def to_log(self) -> Log:
        """
        Converts the action instance to a Log entry.

        Returns:
            Log: A log entry representing the current action state.
        """
        return Log(self)

    @property
    def request(self) -> dict[str, Any]:
        return {}

    def __repr__(self) -> str:
        """Returns a string representation of the Action instance."""
        return (
            f"Action(status={self.status.value}, "
            f"execution_time={self.execution_time})"
        )


# File: lionagi/action/base.py
