"""Tests for tuning protocol implementations."""

from typing import Any, Dict, Optional

import pytest

from lionagi.operatives.tuning.protocols import (
    AsyncOptimizer,
    AsyncTuningStrategy,
    BaseResultTracker,
    BaseStateManager,
    Optimizer,
    ResultTracker,
    StateManager,
    TuningProtocol,
    TuningStrategy,
)
from lionagi.operatives.tuning.types import (
    Metric,
    OptimizationConfig,
    OptimizationState,
    Parameter,
    ParameterSet,
    TuningMetrics,
)


# Mock implementations for testing
class MockStateManager(BaseStateManager[OptimizationState]):
    def __init__(self):
        self.state = None

    def save_state(self, state: OptimizationState) -> None:
        self.state = state

    def load_state(self) -> OptimizationState | None:
        return self.state

    def clear_state(self) -> None:
        self.state = None


class MockResultTracker(BaseResultTracker[TuningMetrics]):
    def __init__(self):
        self.results = []

    def add_result(self, result: TuningMetrics) -> None:
        self.results.append(result)

    def get_best_result(self) -> TuningMetrics | None:
        return (
            min(self.results, key=lambda x: x["loss"])
            if self.results
            else None
        )

    def get_history(self) -> list[TuningMetrics]:
        return self.results


class MockOptimizer:
    def suggest(self, state: OptimizationState) -> dict[str, Any]:
        return {"param1": 0.5}

    def update(self, params: dict[str, Any], score: float) -> None:
        pass


# Test protocol interface compatibility
def test_state_manager_protocol():
    manager = MockStateManager()
    assert isinstance(manager, StateManager)

    state = OptimizationState(iteration=1, best_score=0.5)
    manager.save_state(state)
    assert manager.load_state() == state

    manager.clear_state()
    assert manager.load_state() is None


def test_result_tracker_protocol():
    tracker = MockResultTracker()
    assert isinstance(tracker, ResultTracker)

    result = TuningMetrics(loss=0.5, accuracy=0.8, duration=1.0, iteration=1)
    tracker.add_result(result)
    assert tracker.get_best_result() == result
    assert tracker.get_history() == [result]


def test_optimizer_protocol():
    optimizer = MockOptimizer()
    assert isinstance(optimizer, Optimizer)

    state = OptimizationState(iteration=1, best_score=0.5)
    suggestion = optimizer.suggest(state)
    assert isinstance(suggestion, dict)

    optimizer.update({"param1": 0.5}, 0.3)


# Test TuningProtocol integration
def test_tuning_protocol_integration():
    state_manager = MockStateManager()
    result_tracker = MockResultTracker()
    optimizer = MockOptimizer()

    protocol = TuningProtocol(
        state_manager=state_manager,
        result_tracker=result_tracker,
        optimizer=optimizer,
    )

    assert protocol.state_manager == state_manager
    assert protocol.result_tracker == result_tracker
    assert protocol.optimizer == optimizer


# Test error handling
def test_invalid_state():
    manager = MockStateManager()
    with pytest.raises(TypeError):
        manager.save_state("invalid state")  # type: ignore


def test_invalid_result():
    tracker = MockResultTracker()
    with pytest.raises(TypeError):
        tracker.add_result("invalid result")  # type: ignore


# Test edge cases
def test_empty_result_tracker():
    tracker = MockResultTracker()
    assert tracker.get_best_result() is None
    assert tracker.get_history() == []


def test_multiple_results():
    tracker = MockResultTracker()
    results = [
        TuningMetrics(loss=0.5, accuracy=0.8, duration=1.0, iteration=1),
        TuningMetrics(loss=0.3, accuracy=0.9, duration=1.0, iteration=2),
        TuningMetrics(loss=0.4, accuracy=0.85, duration=1.0, iteration=3),
    ]

    for result in results:
        tracker.add_result(result)

    assert tracker.get_best_result() == results[1]  # lowest loss
    assert len(tracker.get_history()) == 3
