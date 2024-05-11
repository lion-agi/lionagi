from enum import Enum
import asyncio
from typing import Any

from lionagi.libs import SysUtil
from ..generic.abc import Component


class WorkStatus(str, Enum):
    """Enum to represent different statuses of work."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Work(Component):
    status: WorkStatus = WorkStatus.PENDING
    result: Any = None
    error: Any = None
    async_task: asyncio.Task | None = None
    completion_timestamp: str | None = None
    duration: float | None = None

    async def perform(self):
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
            self.completion_timestamp = SysUtil.get_timestamp(sep=None)[:-6]

    def __str__(self):
        return f"Work(id={self.ln_id[:8]}.., status={self.status.value}, created_at={self.timestamp[:-7]}, completed_at={self.completion_timestamp[:-7]}, duration={float(self.duration) if self.duration else 0:.04f} sec(s)"
