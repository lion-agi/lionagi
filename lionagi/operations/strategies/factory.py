# strategies/factory.py

from typing import Any, Dict, Optional, Tuple, Type

from pydantic import BaseModel

from .analyzer import ModelAnalyzer
from .base import StrategyExecutor
from .types import ExecutionProgress, StrategyParams, SystemMetrics


class StrategyFactory:
    """Factory for creating and managing execution strategies."""

    def __init__(self):
        self._strategies: dict[str, type[StrategyExecutor]] = {}
        self._analyzer = ModelAnalyzer()
        self._weights = {"concurrency": 0.4, "memory": 0.3, "performance": 0.3}

    def register_strategy(
        self, name: str, strategy_cls: type[StrategyExecutor]
    ) -> None:
        """Register a new strategy class."""
        self._strategies[name] = strategy_cls

    def select_strategy(
        self,
        operative: BaseModel,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        params: StrategyParams | None = None,
        metrics: SystemMetrics | None = None,
    ) -> StrategyExecutor:
        """
        Select and instantiate the optimal strategy based on model analysis + system metrics.
        """
        if not self._strategies:
            raise ValueError("No strategies registered")

        # Analyze model
        analysis = self._analyzer.analyze_model(operative)
        current_metrics = metrics or SystemMetrics()

        # Compute strategy scores
        scores = self._analyzer.compute_strategy_scores(
            analysis=analysis,
            metrics=current_metrics,
            available_strategies=self._strategies,
            weights=self._weights,
        )

        best_score = max(scores, key=lambda s: s.score)
        best_strategy_cls = self._strategies[best_score.strategy_name]

        # Instantiate strategy
        return best_strategy_cls(
            session=session, branch=branch, params=params or StrategyParams()
        )

    def should_switch_strategy(
        self,
        current: StrategyExecutor,
        operative: BaseModel,
        metrics: dict[str, Any],
    ) -> tuple[bool, type[StrategyExecutor] | None]:
        """
        Determine if a strategy switch is needed based on real-time metrics.
        """
        partial_failure_rate = metrics.get("partial_failure_rate", 0.0)
        system_load = metrics.get("system_load", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)

        # Create up-to-date SystemMetrics
        current_metrics = SystemMetrics(
            current_system_load=system_load,
            memory_usage=memory_usage,
            historical_success_rate=1.0 - partial_failure_rate,
            historical_latency=metrics.get("average_latency", 0.0),
        )

        high_failure_rate = partial_failure_rate > 0.3
        high_system_load = system_load > 0.8
        high_memory_usage = memory_usage > 0.8

        if high_failure_rate or high_system_load or high_memory_usage:
            analysis = self._analyzer.analyze_model(operative)
            scores = self._analyzer.compute_strategy_scores(
                analysis=analysis,
                metrics=current_metrics,
                available_strategies=self._strategies,
                weights=self._weights,
            )

            if high_failure_rate:
                # Prefer more conservative strategies
                fallback_candidates = [
                    s
                    for s in scores
                    if s.strategy_name in ["sequential", "chunked"]
                ]
            elif high_system_load:
                # Avoid heavy concurrency
                fallback_candidates = [
                    s for s in scores if s.strategy_name != "concurrent"
                ]
            elif high_memory_usage:
                # Prefer chunked or hybrid
                fallback_candidates = [
                    s
                    for s in scores
                    if s.strategy_name in ["chunked", "hybrid"]
                ]
            else:
                fallback_candidates = scores

            if not fallback_candidates:
                return (False, None)

            fallback_best = max(fallback_candidates, key=lambda s: s.score)
            current_name = (
                type(current).__name__.replace("Executor", "").lower()
            )

            if fallback_best.strategy_name != current_name:
                new_strategy_cls = self._strategies[
                    fallback_best.strategy_name
                ]
                return (True, new_strategy_cls)

        return (False, None)

    def create_strategy(
        self,
        name: str,
        session: "Session",  # type: ignore
        branch: "Branch",  # type: ignore
        params: StrategyParams | None = None,
        progress: ExecutionProgress | None = None,
    ) -> StrategyExecutor:
        """Create a specific strategy instance by name."""
        if name not in self._strategies:
            raise ValueError(f"Strategy '{name}' not found")

        strategy_cls = self._strategies[name]
        strategy = strategy_cls(
            session=session, branch=branch, params=params or StrategyParams()
        )
        if progress:
            strategy.load_progress(progress)
        return strategy

    def update_weights(self, new_weights: dict[str, float]) -> None:
        """Update scoring factor weights."""
        self._weights.update(new_weights)

    @property
    def available_strategies(self) -> dict[str, type[StrategyExecutor]]:
        """Get dictionary of registered strategies."""
        return self._strategies.copy()
