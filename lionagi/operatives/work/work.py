"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from collections.abc import Coroutine
from datetime import datetime
from typing import Any

from pydantic import Field

from lionagi.protocols.generic.event import Event, EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.utils import to_dict


class Work(Event):
    """
    A class representing a unit of work.

    This class extends Event to provide execution state tracking and event handling,
    while adding work-specific attributes for execution details.

    Attributes:
        async_task (Coroutine | None): The asynchronous task associated with the work.
        async_task_name (str | None): The name of the asynchronous task.
        completion_timestamp (str | None): The timestamp when the work was completed.
        duration (float | None): The duration of the work in seconds.
    """

    async_task: Coroutine | None = Field(
        default=None,
        description="The asynchronous task associated with the work",
        exclude=True,  # Exclude from serialization since coroutines can't be serialized
    )

    async_task_name: str | None = Field(
        default=None, description="The name of the asynchronous task"
    )

    completion_timestamp: str | None = Field(
        default=None, description="The timestamp when the work was completed"
    )

    duration: float | None = Field(
        default=None, description="The duration of the work in seconds"
    )

    async def invoke(self) -> None:
        """Perform the work and update execution state."""
        self.status = EventStatus.PROCESSING
        try:
            result, duration = await self.async_task
            self.execution.response = result
            self.status = EventStatus.COMPLETED
            self.duration = duration
            del self.async_task
        except Exception as e:
            self.execution.error = str(e)
            self.status = EventStatus.FAILED
        finally:
            from lionagi.utils import time

            self.completion_timestamp = time(
                type_="custom", custom_format="%Y%m%d%H%M%S"
            )

    async def stream(self) -> None:
        """
        Performs the work with streaming results.
        For now, we just call invoke since we don't need streaming.
        """
        await self.invoke()

    def to_log(self) -> Log:
        """Create a Log object summarizing this event."""
        return Log(
            content={
                "type": "Work",
                "id": str(self.id),
                "task_name": self.async_task_name,
                "status": str(self.status),
                "created_at": datetime.fromtimestamp(self.created_at).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "completed_at": self.completion_timestamp,
                "duration": float(self.duration) if self.duration else 0,
                "response": to_dict(self.execution.response),
                "error": self.execution.error,
            }
        )

    def __str__(self):
        return (
            f"Work(id={str(self.id)[:8]}.., status={self.status.value}, "
            f"created_at={datetime.fromtimestamp(self.created_at).strftime('%Y-%m-%d %H:%M:%S')}, "
            f"completed_at={self.completion_timestamp}, "
            f"duration={float(self.duration) if self.duration else 0:.04f} sec(s))"
        )
