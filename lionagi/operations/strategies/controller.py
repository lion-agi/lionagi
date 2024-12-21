# lionagi/strategies/controller.py

from typing import Any, Dict, Optional

from .base import StrategyExecutor
from .executors.sequential import SequentialExecutor
from .factory import StrategyFactory
from .types import StrategyParams, SystemMetrics


class ExecutionController:
    """Controls strategy selection, execution, and switching."""

    def __init__(self):
        self.factory = StrategyFactory()
        self._metrics: dict[str, Any] = {
            "partial_failure_rate": 0.0,
            "executed_steps": 0,
            "system_load": 0.0,
            "memory_usage": 0.0,
            "average_latency": 0.0,
        }
        self.register_default_strategies()

    def register_default_strategies(self) -> None:
        """Register the default set of execution strategies."""
        from .executors.chunked import ChunkedExecutor
        from .executors.concurrent import ConcurrentExecutor
        from .executors.hybrid import HybridExecutor
        from .executors.sequential import SequentialExecutor

        self.factory.register_strategy("sequential", SequentialExecutor)
        self.factory.register_strategy("concurrent", ConcurrentExecutor)
        self.factory.register_strategy("chunked", ChunkedExecutor)
        self.factory.register_strategy("hybrid", HybridExecutor)

    async def execute_with_strategy(
        self,
        operative: Any,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        strategy_params: StrategyParams | None = None,
        initial_metrics: SystemMetrics | None = None,
    ) -> Any:
        """Execute the operative using the best strategy, switching if needed."""
        strategy = self.factory.select_strategy(
            operative=operative,
            session=session,
            branch=branch,
            params=strategy_params,
            metrics=initial_metrics,
        )

        switch_count = 0
        while True:
            try:
                # Execute with current strategy
                result = await strategy.execute(operative)

                # Update metrics based on result
                self._update_metrics(result, strategy)

                # Determine if a strategy switch is needed
                should_switch, new_strategy_cls = (
                    self.factory.should_switch_strategy(
                        current=strategy,
                        operative=operative,
                        metrics=self._metrics,
                    )
                )

                if should_switch and new_strategy_cls:
                    # Limit the number of switches to prevent infinite loops
                    if switch_count >= self.get_max_switches():
                        break

                    # Switch strategy
                    strategy = await self._switch_strategy(
                        current=strategy,
                        new_strategy_cls=new_strategy_cls,
                        session=session,
                        branch=branch,
                        params=strategy_params,
                    )
                    switch_count += 1
                    continue

                # If no switch is needed, return the result
                return result

            except Exception as e:
                # Handle errors: fallback to sequential if not already sequential
                if not isinstance(strategy, SequentialExecutor):
                    strategy = await self._switch_to_sequential(
                        current=strategy,
                        session=session,
                        branch=branch,
                        params=strategy_params,
                    )
                    switch_count += 1
                    continue
                raise  # Re-raise if already sequential

    async def _switch_strategy(
        self,
        current: StrategyExecutor,
        new_strategy_cls: type,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        params: StrategyParams | None,
    ) -> StrategyExecutor:
        """Perform the actual switch to a new strategy."""
        await current.finalize_in_flight_operations()

        new_strategy = new_strategy_cls(
            session=session, branch=branch, params=params or StrategyParams()
        )
        # Transfer progress and metrics
        new_strategy.load_progress(current.progress)
        new_strategy.metrics = current.metrics

        return new_strategy

    async def _switch_to_sequential(
        self,
        current: StrategyExecutor,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        params: StrategyParams | None,
    ) -> StrategyExecutor:
        """Force switch to sequential if other strategies fail."""
        from .executors.sequential import SequentialExecutor

        return await self._switch_strategy(
            current=current,
            new_strategy_cls=SequentialExecutor,
            session=session,
            branch=branch,
            params=params,
        )

    def _update_metrics(self, result: Any, strategy: StrategyExecutor) -> None:
        """Update global metrics based on strategy progress and results."""
        progress = strategy.get_progress()
        metrics = strategy.get_metrics()

        self._metrics["executed_steps"] = progress.completed_items

        if progress.total_steps > 0:
            self._metrics["partial_failure_rate"] = (
                progress.failed_items / progress.total_steps
            )

        self._metrics["system_load"] = metrics.current_system_load
        self._metrics["memory_usage"] = metrics.memory_usage

        # Attempt to glean average latency from result
        if isinstance(result, tuple) and len(result) == 2:
            _, responses = result
            latencies = []
            for r in responses:
                if isinstance(r, dict) and "latency" in r:
                    latencies.append(r["latency"])
            if latencies:
                self._metrics["average_latency"] = sum(latencies) / len(
                    latencies
                )

    @staticmethod
    def get_max_switches() -> int:
        """Prevents infinite switching loops."""
        return 3

    def get_metrics(self) -> dict[str, Any]:
        """Get current execution metrics."""
        return dict(self._metrics)

    def reset_metrics(self) -> None:
        """Reset execution metrics."""
        self._metrics = {
            "partial_failure_rate": 0.0,
            "executed_steps": 0,
            "system_load": 0.0,
            "memory_usage": 0.0,
            "average_latency": 0.0,
        }
