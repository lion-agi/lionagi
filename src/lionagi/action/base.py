# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, NoReturn

from pydantic import Field

from ..protocols.types import BaseAutoModel, Event, EventStatus, Log

__all__ = ("Action",)


class Action(BaseAutoModel, Event, ABC):
    """
    Base class for executable actions with status tracking and result management.

    An Action represents a discrete unit of work that can be executed asynchronously.
    It tracks its execution state, timing, results, and any errors that occur during
    execution.

    Attributes:
        status (EventStatus): Current execution status. Defaults to PENDING.
        execution_time (Optional[float]): Time taken for execution in seconds.
        execution_result (Optional[Any]): Result produced by the action execution.
        error (Optional[str]): Error message if execution failed.

    Properties:
        request (dict[str, Any]): Request parameters for permission checking.
    """

    status: EventStatus = Field(
        default=EventStatus.PENDING,
        description="Current status of the action execution",
    )
    execution_time: float | None = Field(
        default=None, description="Time taken to execute the action in seconds"
    )
    execution_result: Any | None = Field(
        default=None, description="Result produced by the action execution"
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True,
        "use_enum_values": False,
    }

    def from_dict(self, *args: Any, **kwargs: Any) -> NoReturn:
        """
        Explicitly prevents recreation from dictionary.

        Actions are meant to be created and executed once, not recreated from
        serialized state.

        Raises:
            NotImplementedError: Always, as Actions cannot be recreated.
        """
        raise NotImplementedError(
            "Actions cannot be re-created from dictionaries. Create a new Action instance instead."
        )

    def to_log(self) -> Log:
        """
        Converts the action instance to a Log entry.

        Creates a log entry capturing the current state of the action for
        tracking and auditing purposes.

        Returns:
            Log: A log entry representing the current action state.
        """
        return Log(
            content={
                "id": str(self.id),
                "created_timestamp": self.created_timestamp,
                "status": self.status,
                "execution_time": self.execution_time,
                "execution_result": self.execution_result,
                "error": self.error,
            }
        )

    @property
    def request(self) -> dict[str, Any]:
        """
        Gets request parameters for permission checking.

        Override this in subclasses to provide custom permission parameters.

        Returns:
            Empty dict by default. Subclasses should override to provide
            relevant permission parameters.
        """
        return {}

    def __repr__(self) -> str:
        """
        Returns a string representation of the Action instance.

        Returns:
            String containing key action state (status and execution time).
        """
        return (
            f"Action(status={self.status.name}, "
            f"execution_time={self.execution_time})"
        )

    @abstractmethod
    async def invoke(self) -> None:
        """Execute the action.

        This method must be implemented by subclasses to define the actual
        execution behavior of the action.
        """
        pass
