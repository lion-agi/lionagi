from enum import Enum
import asyncio
from typing import Any

from lionagi.libs import SysUtil
from ..generic.abc import Element


class WorkStatus(str, Enum):
    """Enum to represent different statuses of work."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Work(Element):
    status: WorkStatus = WorkStatus.PENDING
    result: Any = None
    error: Any = None
    async_task: asyncio.Task | None = None
    completion_timestamp: str | None = None

    async def perform(self):
        try:
            result = await self.async_task
            self.result = result
            self.status = WorkStatus.COMPLETED
            self.async_task = None
        except Exception as e:
            self.error = e
            self.status = WorkStatus.FAILED
        finally:
            self.completion_timestamp = SysUtil.get_timestamp()

    def __str__(self):
        return f"Work(id={self.ln_id[:8]}.., status={self.status.value}, created_at={self.timestamp[:-7]}, completed_at={self.completion_timestamp[:-7]})"
