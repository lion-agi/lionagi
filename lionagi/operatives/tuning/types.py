"""
Type Definitions

This module defines core types and interfaces used throughout
the tuning package, including parameter sets, metrics, and example sets.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from numbers import Number
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from ...protocols.generic import Element

# Type variables
T = TypeVar("T")
MetricT = TypeVar("MetricT", bound=Number)
ParamT = TypeVar("ParamT")


class ParameterType(Enum):
    """Supported parameter types for tuning."""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DISCRETE = "discrete"


@dataclass
class Parameter(Generic[ParamT]):
    """Single parameter definition with constraints."""

    type: ParameterType
    default: ParamT
    name: str | None = None
    bounds: tuple[ParamT, ParamT] | None = None
    choices: Sequence[ParamT] | None = None

    def validate(self, value: ParamT) -> bool:
        """Validate if a value meets parameter constraints."""
        if self.type == ParameterType.NUMERIC and self.bounds:
            return self.bounds[0] <= value <= self.bounds[1]
        elif self.type == ParameterType.CATEGORICAL and self.choices:
            return value in self.choices
        elif self.type == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        return True


@dataclass
class ParameterSet(Element):
    """Collection of parameters with validation."""

    parameters: dict[str, Parameter] = field(default_factory=dict)

    def add_parameter(self, param: Parameter) -> None:
        """Add a new parameter definition."""
        self.parameters[param.name] = param

    def validate_values(self, values: dict[str, Any]) -> bool:
        """Validate a set of parameter values."""
        return all(
            param.validate(values.get(name, param.default))
            for name, param in self.parameters.items()
        )


@runtime_checkable
class Metric(Protocol):
    """Protocol for metric implementations."""

    def __call__(self, predicted: Any, expected: Any) -> float: ...


class OptimizationState(TypedDict):
    """Current state of optimization process."""

    iteration: int
    best_score: float
    best_params: dict[str, Any]
    history: list[dict[str, Any]]


class TuningMetrics(TypedDict):
    """Metrics collected during parameter tuning."""

    loss: float
    accuracy: float | None
    duration: float
    iteration: int
    additional_metrics: dict[str, Number]


@dataclass
class OptimizationConfig:
    """Configuration for optimization process."""

    max_iterations: int
    tolerance: float
    patience: int
    random_state: int | None
    parallel_jobs: int


@dataclass
class ExampleSet(Generic[T]):
    """Collection of input/output training examples."""

    inputs: Sequence[T]
    outputs: Sequence[T]
    weights: Sequence[float] | None = None

    def __post_init__(self):
        if len(self.inputs) != len(self.outputs):
            raise ValueError(
                "Input and output sequences must have same length"
            )
        if self.weights and len(self.weights) != len(self.inputs):
            raise ValueError("Weights sequence must match input/output length")


@dataclass
class TuningConfig:
    """Base configuration for tuning strategies."""

    max_iterations: int = 100
    patience: int = 10
    min_improvement: float = 0.001
    random_seed: int | None = None
    parallel_trials: int = 1
    save_history: bool = True
