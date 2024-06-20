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

from enum import Enum
import asyncio
from typing import Any

from lionagi.os.lib.sys_util import get_timestamp
from lionagi.os.collections.abc import Component


class WorkStatus(str, Enum):
    """Enum to represent different statuses of work."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Work(Component):
    """
    A class representing a unit of work.

    Attributes:
        status (WorkStatus): The current status of the work.
        result (Any): The result of the work, if completed.
        error (Any): Any error encountered during the work.
        async_task (asyncio.Task | None): The asynchronous task associated with the work.
        completion_timestamp (str | None): The timestamp when the work was completed.
        duration (float | None): The duration of the work.
    """

    status: WorkStatus = WorkStatus.PENDING
    result: Any = None
    error: Any = None
    async_task: asyncio.Task | None = None
    completion_timestamp: str | None = None
    duration: float | None = None

    async def perform(self):
        """Perform the work and update the status, result, and duration."""
        try:
            result, duration = await self.async_task
            self.result = result
            self.status = WorkStatus.COMPLETED
            self.duration = duration
            del self.async_task
        except Exception as e:
            self.error = e
            self.status = WorkStatus.FAILED
        finally:
            self.completion_timestamp = get_timestamp(sep=None)[:-6]

    def __str__(self):
        return (
            f"Work(id={self.ln_id[:8]}.., status={self.status.value}, "
            f"created_at={self.timestamp[:-7]}, "
            f"completed_at={self.completion_timestamp[:-7]}, "
            f"duration={float(self.duration) if self.duration else 0:.04f} sec(s))"
        )
