"""
Optimization Metrics

This module defines metrics and evaluation functions for measuring
parameter optimization performance.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Dict, List, Optional, Union

from .types import Metric


class BaseMetric(ABC):
    """Abstract base class for all metrics."""

    @abstractmethod
    def __call__(self, predicted: Any, expected: Any) -> float:
        """Calculate metric value."""
        pass


class ResponseCorrectnessMetric(BaseMetric):
    """Measures semantic correctness of responses."""

    def __call__(self, predicted: str, expected: str) -> float:
        # TODO: Implement semantic similarity calculation
        return 0.0


class FormatAccuracyMetric(BaseMetric):
    """Measures adherence to expected output format."""

    def __call__(self, predicted: str, expected: str) -> float:
        # TODO: Implement format validation
        return 0.0


class ExampleComplianceMetric(BaseMetric):
    """Measures compliance with provided examples."""

    def __call__(
        self, predicted: str, examples: list[tuple[str, str]]
    ) -> float:
        # TODO: Implement example compliance checking
        return 0.0


class MetricAggregator:
    """Combines multiple metrics into a single score."""

    def __init__(self):
        self._metrics: dict[str, tuple[BaseMetric, float]] = {}

    def add_metric(self, name: str, metric: BaseMetric, weight: float = 1.0):
        """Register a new metric with optional weight."""
        self._metrics[name] = (metric, weight)

    def compute(self, predicted: Any, expected: Any) -> dict[str, float]:
        """Compute all metrics and return results."""
        results = {}
        for name, (metric, weight) in self._metrics.items():
            score = metric(predicted, expected) * weight
            results[name] = score
        return results


# Global metric registry
_METRIC_REGISTRY: dict[str, type[BaseMetric]] = {}


def register_metric(name: str):
    """Decorator to register custom metrics."""

    def decorator(cls: type[BaseMetric]):
        _METRIC_REGISTRY[name] = cls
        return cls

    return decorator


def get_metric(name: str) -> type[BaseMetric]:
    """Retrieve a registered metric class."""
    if name not in _METRIC_REGISTRY:
        raise KeyError(f"Metric '{name}' not found in registry")
    return _METRIC_REGISTRY[name]
