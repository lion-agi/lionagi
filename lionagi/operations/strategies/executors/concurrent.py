# lionagi/strategies/executors/concurrent.py

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from lionagi.protocols.operatives.tasks import Task

from ..base import StrategyExecutor


class ConcurrentExecutor(StrategyExecutor):
    """Concurrent execution strategy.

    Executes multiple steps in parallel.
    Best for:
    - Independent operations
    - I/O-bound tasks
    - High throughput
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks: dict[str, asyncio.Task] = {}
        self._semaphore: asyncio.Semaphore | None = None

    async def prepare_execution(self) -> None:
        """Initialize concurrency controls."""
        self._tasks = {}
        self._semaphore = asyncio.Semaphore(self.params.concurrency_limit)

    async def cleanup(self) -> None:
        """Clean up any running tasks."""
        for task in self._tasks.values():
            if not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks = {}

    async def execute_single(self, task: Task, idx: int) -> Any:
        """Execute a single task with concurrency control."""
        async with self._semaphore:
            try:
                response = await self.branch.instruct(
                    task, **self.params.dict()
                )

                self.progress.completed_items += 1
                self.progress.checkpoints[str(idx)] = {
                    "task_id": task.ln_id,
                    "status": "completed",
                    "response": response,
                }
                return response

            except Exception as e:
                self.progress.failed_items += 1
                self.progress.checkpoints[str(idx)] = {
                    "task_id": task.ln_id,
                    "status": "failed",
                    "error": str(e),
                }
                raise

    async def execute(self, operative: Any) -> tuple[list[Any], list[Any]]:
        """Execute steps concurrently."""
        await self.prepare_execution()

        tasks = []
        responses = []

        try:
            if hasattr(operative, "instruct_models"):
                tasks = operative.instruct_models
            total_steps = len(tasks)
            self.progress.total_steps = total_steps

            # Create async tasks
            for idx, task in enumerate(tasks, 1):
                self.progress.current_step = idx
                job = asyncio.create_task(self.execute_single(task, idx))
                self._tasks[str(idx)] = job

            completed = await asyncio.gather(
                *self._tasks.values(), return_exceptions=True
            )

            for result in completed:
                if isinstance(result, Exception):
                    if self.progress.failed_items >= self.params.retry_limit:
                        raise result
                else:
                    responses.append(result)

            return tasks, responses
        finally:
            await self.cleanup()

    async def finalize_in_flight_operations(self) -> None:
        """Cancel any running tasks."""
        await self.cleanup()
