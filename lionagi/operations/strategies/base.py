# strategies/base.py

from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from .types import ExecutionProgress, StrategyParams, SystemMetrics


class StrategyExecutor(ABC):
    """Base class for execution strategies."""

    def __init__(
        self,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        params: StrategyParams,
    ) -> None:
        self.session = session
        self.branch = branch
        self.params = params
        self.progress = ExecutionProgress()
        self.metrics = SystemMetrics()

    @abstractmethod
    async def execute(self, operative: Any) -> tuple[list[Any], list[Any]]:
        """
        Execute the strategy.

        Returns:
            (list_of_tasks, list_of_task_responses)
        """
        raise NotImplementedError

    async def finalize_in_flight_operations(self) -> None:
        """
        Cleanup and finalize any in-progress operations.
        Called before switching strategies.
        """
        # Default implementation - override in child classes if needed
        pass

    def load_progress(self, progress: ExecutionProgress) -> None:
        """Load execution progress from another strategy."""
        self.progress = progress

    def update_metrics(
        self, current_load: float = None, memory_usage: float = None
    ) -> None:
        """Update system metrics."""
        if current_load is not None:
            self.metrics.current_system_load = current_load
        if memory_usage is not None:
            self.metrics.memory_usage = memory_usage

    async def prepare_execution(self) -> None:
        """Prepare for execution. Override if needed for resource setup."""
        pass

    async def cleanup(self) -> None:
        """Cleanup after execution. Override if needed for resource teardown."""
        pass

    def get_progress(self) -> ExecutionProgress:
        """Get current execution progress."""
        return self.progress

    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return self.metrics
