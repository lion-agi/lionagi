"""
Tuning Protocol Interfaces

This module defines the core protocols and interfaces for parameter tuning,
state management, result tracking, and optimization processes.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator, Sequence
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from .types import (
    ExampleSet,
    Metric,
    OptimizationConfig,
    OptimizationState,
    Parameter,
    ParameterSet,
    TuningMetrics,
)

T = TypeVar("T")
StateT = TypeVar("StateT")
ResultT = TypeVar("ResultT")


@runtime_checkable
class StateManager(Protocol[StateT]):
    """Protocol for managing optimization state."""

    def save_state(self, state: StateT) -> None: ...
    def load_state(self) -> StateT | None: ...
    def clear_state(self) -> None: ...


@runtime_checkable
class ResultTracker(Protocol[ResultT]):
    """Protocol for tracking optimization results."""

    def add_result(self, result: ResultT) -> None: ...
    def get_best_result(self) -> ResultT | None: ...
    def get_history(self) -> Sequence[ResultT]: ...


@runtime_checkable
class Optimizer(Protocol):
    """Protocol for optimization algorithms."""

    def suggest(self, state: OptimizationState) -> dict[str, Any]: ...
    def update(self, params: dict[str, Any], score: float) -> None: ...


@runtime_checkable
class AsyncOptimizer(Protocol):
    """Protocol for async optimization algorithms."""

    async def suggest(self, state: OptimizationState) -> dict[str, Any]: ...
    async def update(self, params: dict[str, Any], score: float) -> None: ...


@runtime_checkable
class TuningStrategy(Protocol):
    """Protocol for parameter tuning strategies."""

    def optimize(
        self,
        param_set: ParameterSet,
        metric: Metric,
        config: OptimizationConfig,
    ) -> Iterator[OptimizationState]: ...


@runtime_checkable
class AsyncTuningStrategy(Protocol):
    """Protocol for async parameter tuning strategies."""

    async def optimize(
        self,
        param_set: ParameterSet,
        metric: Metric,
        config: OptimizationConfig,
    ) -> AsyncIterator[OptimizationState]: ...


class BaseStateManager(ABC, Generic[StateT]):
    """Abstract base class for state management."""

    @abstractmethod
    def save_state(self, state: StateT) -> None:
        """Save current optimization state."""
        pass

    @abstractmethod
    def load_state(self) -> StateT | None:
        """Load saved optimization state."""
        pass

    @abstractmethod
    def clear_state(self) -> None:
        """Clear saved state."""
        pass


class BaseResultTracker(ABC, Generic[ResultT]):
    """Abstract base class for result tracking."""

    @abstractmethod
    def add_result(self, result: ResultT) -> None:
        """Add new optimization result."""
        pass

    @abstractmethod
    def get_best_result(self) -> ResultT | None:
        """Get best result so far."""
        pass

    @abstractmethod
    def get_history(self) -> Sequence[ResultT]:
        """Get full optimization history."""
        pass


@dataclass
class TuningProtocol(Generic[StateT, ResultT]):
    """Combines state management and result tracking."""

    state_manager: StateManager[StateT]
    result_tracker: ResultTracker[ResultT]
    optimizer: Optimizer
