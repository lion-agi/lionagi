# lionagi/strategies/executors/hybrid.py

import asyncio
from collections.abc import Iterator
from typing import Any, Dict, List, Optional, Tuple

from lionagi.protocols.operatives.tasks import Task

from ..base import StrategyExecutor


class HybridExecutor(StrategyExecutor):
    """Hybrid execution strategy combining chunked and concurrent execution.

    Processes chunks of steps concurrently.
    Best for:
    - Mixed workloads
    - Dynamic resource environments
    - Balancing throughput and resource usage
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

    def chunk_iterator(
        self, items: list[Any]
    ) -> Iterator[tuple[int, list[Any]]]:
        """Yield (start_idx, chunk) tuples with dynamic chunk sizing."""
        if not items:
            return
        concurrency = max(1, self.params.concurrency_limit)
        base_chunk_size = max(1, self.params.chunk_size)

        # Attempt to distribute tasks among concurrency
        chunk_size = max(
            1, min(base_chunk_size, len(items) // concurrency or 1)
        )

        for i in range(0, len(items), chunk_size):
            yield i, items[i : i + chunk_size]

    async def execute_chunk(
        self, chunk: list[Any], start_idx: int
    ) -> list[Any]:
        """Execute a chunk of tasks concurrently."""
        chunk_responses = []
        tasks = []

        # Acquire the semaphore once per chunk
        async with self._semaphore:
            for idx, task in enumerate(chunk, start_idx + 1):
                job = asyncio.create_task(self.execute_single(task, idx))
                tasks.append(job)
                self._tasks[str(idx)] = job

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    if self.progress.failed_items >= self.params.retry_limit:
                        raise result
                else:
                    chunk_responses.append(result)

            # Example: if memory usage is high, add a delay
            if self.metrics.memory_usage > 0.8:
                await asyncio.sleep(0.1)

        return chunk_responses

    async def execute_single(self, task: Task, idx: int) -> Any:
        """Execute a single task."""
        try:
            response = await self.branch.instruct(task, **self.params.dict())

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
        """Execute steps using a hybrid approach: chunked + concurrent."""
        await self.prepare_execution()

        tasks = []
        all_responses = []

        try:
            if hasattr(operative, "instruct_models"):
                tasks = operative.instruct_models
            total_steps = len(tasks)
            self.progress.total_steps = total_steps

            for start_idx, chunk in self.chunk_iterator(tasks):
                self.progress.current_step = start_idx + 1
                chunk_responses = await self.execute_chunk(chunk, start_idx)
                all_responses.extend(chunk_responses)

                # Example: adjust concurrency if system load is high
                if self.metrics.current_system_load > 0.8:
                    self.params.concurrency_limit = max(
                        1, self.params.concurrency_limit - 1
                    )
                    # Reinitialize semaphore with new concurrency limit
                    self._semaphore = asyncio.Semaphore(
                        self.params.concurrency_limit
                    )

            return tasks, all_responses
        finally:
            await self.cleanup()

    async def finalize_in_flight_operations(self) -> None:
        """Cleanup any running tasks."""
        await self.cleanup()
