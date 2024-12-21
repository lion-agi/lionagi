# lionagi/strategies/executors/sequential.py

from typing import Any, List, Tuple

from ..base import StrategyExecutor


class SequentialExecutor(StrategyExecutor):
    """Sequential execution strategy.

    Executes steps one at a time in order.
    Best for:
    - Tasks with strict ordering
    - Operations that must be atomic
    - Debugging and testing scenarios
    """

    async def execute(self, operative: Any) -> tuple[list[Any], list[Any]]:
        """Execute steps sequentially."""
        await self.prepare_execution()

        tasks = []
        responses = []

        try:
            # Retrieve tasks
            if hasattr(operative, "instruct_models"):
                tasks = operative.instruct_models
            total_steps = len(tasks)
            self.progress.total_steps = total_steps

            for idx, task in enumerate(tasks, 1):
                self.progress.current_step = idx
                try:
                    response = await self.branch.instruct(
                        task, **self.params.dict()
                    )
                    responses.append(response)
                    self.progress.completed_items += 1
                    self.progress.checkpoints[str(idx)] = {
                        "task_id": task.ln_id,
                        "status": "completed",
                        "response": response,
                    }
                except Exception as e:
                    self.progress.failed_items += 1
                    self.progress.checkpoints[str(idx)] = {
                        "task_id": task.ln_id,
                        "status": "failed",
                        "error": str(e),
                    }
                    if self.progress.failed_items >= self.params.retry_limit:
                        raise

            return tasks, responses
        finally:
            await self.cleanup()

    async def finalize_in_flight_operations(self) -> None:
        """Nothing special to finalize for sequential execution."""
        pass
