# lionagi/strategies/executors/chunked.py

import asyncio
from collections.abc import Iterator
from typing import Any, List, Tuple

from ..base import StrategyExecutor


class ChunkedExecutor(StrategyExecutor):
    """Chunked execution strategy.

    Processes steps in batches (chunks).
    Best for:
    - Large numbers of operations
    - Memory-constrained environments
    - Balanced throughput vs. resource usage
    """

    def chunk_iterator(
        self, items: list[Any]
    ) -> Iterator[tuple[int, list[Any]]]:
        """Yield (start_idx, chunk) tuples."""
        chunk_size = self.params.chunk_size
        for i in range(0, len(items), chunk_size):
            yield i, items[i : i + chunk_size]

    async def execute_chunk(
        self, chunk: list[Any], start_idx: int
    ) -> list[Any]:
        """Execute a single chunk sequentially."""
        responses = []
        for idx, task in enumerate(chunk, start_idx + 1):
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
                responses.append(response)
            except Exception as e:
                self.progress.failed_items += 1
                self.progress.checkpoints[str(idx)] = {
                    "task_id": task.ln_id,
                    "status": "failed",
                    "error": str(e),
                }
                if self.progress.failed_items >= self.params.retry_limit:
                    raise
        return responses

    async def execute(self, operative: Any) -> tuple[list[Any], list[Any]]:
        """Execute steps in chunks."""
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

                # Example: yield to event loop or do memory checks
                if self.metrics.memory_usage > 0.8:
                    await asyncio.sleep(0.1)  # Let memory settle

            return tasks, all_responses
        finally:
            await self.cleanup()

    async def finalize_in_flight_operations(self) -> None:
        """No special finalization for chunked execution."""
        pass
