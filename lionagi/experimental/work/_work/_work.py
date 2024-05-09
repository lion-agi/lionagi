import asyncio
from typing import Any, Optional

from lionagi.core.generic.component import BaseComponent
from lionagi.libs import CallDecorator as cd, SysUtil

from .._status import WorkStatus

class Work(BaseComponent):
    """
    Represents an asynchronous work unit in an application, encapsulating task execution,
    status tracking, and result handling.

    Attributes:
        form_id (Optional[str]): Identifier for a specific form associated with the work.
        status (WorkStatus): The current status of the work, defaulting to PENDING.
        result (Any): The result of the work if completed successfully.
        error (Any): Any error encountered during the work's execution.
        async_task (Optional[asyncio.Task]): The asyncio task associated with the work.
        completion_timestamp (Optional[str]): Timestamp marking the completion of the work.
        execution_duration (Optional[str]): The duration of the task execution.
    """

    form_id: Optional[str] = None
    status: WorkStatus = WorkStatus.PENDING
    result: Any = None
    error: Any = None
    async_task: Optional[asyncio.Task] = None
    completion_timestamp: Optional[str] = None
    execution_duration: Optional[str] = None

    @cd.count_calls
    async def perform(self):
        """
        Asynchronously performs the assigned task and handles the outcome by updating
        the work's status, result, and error attributes.

        This method is decorated to count its calls, helping in monitoring how often it's executed.
        """
        try:
            result, duration = await self.async_task
            self.result = result
            self.execution_duration = f"{duration:.6f}"
            self.status = WorkStatus.COMPLETED
        except Exception as e:
            self.error = e
            self.status = WorkStatus.FAILED
        finally:
            del self.async_task  # Cleanup the task after completion or failure.
            self.completion_timestamp = SysUtil.get_timestamp(sep=None)

    def __str__(self):
        created_at = self.timestamp[:-6] if self.timestamp else "N/A"
        completed_at = (self.completion_timestamp[:-6] if self.completion_timestamp
                        else "N/A")
        duration = self.execution_duration or "N/A"
        return (f"Work(id={self.id_}, status={self.status.value}, "
                f"created_at={created_at}, completed_at={completed_at}, "
                f"execution_duration={duration})")
