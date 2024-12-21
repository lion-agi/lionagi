# strategies/analyzer.py

from typing import Any, Dict, List, Optional, Type

from .base import StrategyExecutor
from .types import ModelAnalysis, StrategyScore, SystemMetrics


class ModelAnalyzer:
    """Analyzes the operative or model for strategy selection."""

    def analyze_model(self, operative: Any) -> ModelAnalysis:
        """
        Analyze model structure and characteristics.

        Args:
            operative: The operative to analyze, which should have a 'request_type'
                       or a similar Pydantic model with fields.

        Returns:
            ModelAnalysis containing structural analysis
        """
        request_fields = {}
        if hasattr(operative, "request_type") and operative.request_type:
            request_fields = operative.request_type.__fields__

        # Find fields with dependencies
        dependent_fields = []
        for field_name, field_info in request_fields.items():
            if getattr(field_info, "depends_on", None):
                dependent_fields.append(field_name)

        # Compute metrics (simple heuristics)
        field_count = len(request_fields)
        validation_complexity = float(field_count) * 0.1
        concurrent_safety = max(0.0, 1.0 - (len(dependent_fields) * 0.1))
        memory_footprint = float(field_count) * 0.05

        return ModelAnalysis(
            field_count=field_count,
            dependent_fields=dependent_fields,
            validation_complexity=validation_complexity,
            concurrent_safety=concurrent_safety,
            memory_footprint=memory_footprint,
        )

    def compute_strategy_scores(
        self,
        analysis: ModelAnalysis,
        metrics: SystemMetrics,
        available_strategies: dict[str, type[StrategyExecutor]],
        weights: dict[str, float] | None = None,
    ) -> list[StrategyScore]:
        """
        Compute scores for each available strategy based on model analysis and system metrics.

        Args:
            analysis: Model analysis results
            metrics: Current system metrics
            available_strategies: Dictionary of strategy name to class
            weights: Optional weights for different factors

        Returns:
            Sorted list of StrategyScore objects (descending by score)
        """
        if weights is None:
            weights = {"concurrency": 0.4, "memory": 0.3, "performance": 0.3}

        scores = []
        for strategy_name, strategy_cls in available_strategies.items():
            score = 0.0
            factors = {}
            constraints = {}

            # Concurrency factor (favor concurrency if concurrent_safety is high)
            if strategy_name in ["concurrent", "hybrid"]:
                concurrency_factor = (
                    analysis.concurrent_safety * weights["concurrency"]
                )
                score += concurrency_factor
                factors["concurrency_factor"] = concurrency_factor

            # Memory factor (favor strategies if memory usage is low)
            memory_factor = (
                max(
                    0.0,
                    1.0 - (analysis.memory_footprint + metrics.memory_usage),
                )
                * weights["memory"]
            )
            score += memory_factor
            factors["memory_factor"] = memory_factor

            # Performance factor (favor simpler strategies if validation complexity is high)
            if strategy_name in ["sequential", "chunked"]:
                complexity_factor = max(
                    0, 1.0 - analysis.validation_complexity * 0.05
                )
                performance_factor = complexity_factor * weights["performance"]
                score += performance_factor
                factors["performance_factor"] = performance_factor

            # Add constraints or metadata
            constraints["max_concurrency"] = (
                10 if strategy_name in ["concurrent", "hybrid"] else 1
            )
            constraints["supports_partial_failures"] = strategy_name in [
                "chunked",
                "hybrid",
            ]

            scores.append(
                StrategyScore(
                    strategy_name=strategy_name,
                    score=score,
                    factors=factors,
                    constraints=constraints,
                )
            )

        return sorted(scores, key=lambda s: s.score, reverse=True)
