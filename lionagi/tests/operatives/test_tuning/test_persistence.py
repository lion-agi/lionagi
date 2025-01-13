"""Tests for tuning persistence implementations."""

import json
import tempfile
from pathlib import Path

import pytest

from lionagi.operatives.tuning.persistence import (
    ExampleDatabase,
    FileStateManager,
    MetricHistory,
    SQLiteResultTracker,
)
from lionagi.operatives.tuning.types import (
    ExampleSet,
    OptimizationState,
    TuningMetrics,
)


# Fixtures
@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


# Test FileStateManager
def test_file_state_manager(temp_file):
    manager = FileStateManager(temp_file)
    state = OptimizationState(iteration=1, best_score=0.5)

    manager.save_state(state)
    loaded_state = manager.load_state()

    assert loaded_state is not None
    assert loaded_state.iteration == state.iteration
    assert loaded_state.best_score == state.best_score

    manager.clear_state()
    assert manager.load_state() is None


def test_file_state_manager_missing_file():
    manager = FileStateManager("nonexistent.json")
    assert manager.load_state() is None


# Test SQLiteResultTracker
def test_sqlite_result_tracker(temp_db):
    tracker = SQLiteResultTracker(temp_db)
    result = TuningMetrics(
        loss=0.5,
        accuracy=0.8,
        duration=1.0,
        iteration=1,
        additional_metrics={"f1": 0.75},
    )

    tracker.add_result(result)
    best_result = tracker.get_best_result()

    assert best_result is not None
    assert best_result["loss"] == result["loss"]
    assert best_result["accuracy"] == result["accuracy"]

    history = tracker.get_history()
    assert len(history) == 1
    assert history[0]["loss"] == result["loss"]


def test_sqlite_result_tracker_multiple_results(temp_db):
    tracker = SQLiteResultTracker(temp_db)
    results = [
        TuningMetrics(loss=0.5, accuracy=0.8, duration=1.0, iteration=1),
        TuningMetrics(loss=0.3, accuracy=0.9, duration=1.0, iteration=2),
        TuningMetrics(loss=0.4, accuracy=0.85, duration=1.0, iteration=3),
    ]

    for result in results:
        tracker.add_result(result)

    best_result = tracker.get_best_result()
    assert best_result is not None
    assert best_result["loss"] == 0.3

    history = tracker.get_history()
    assert len(history) == 3
    assert [r["iteration"] for r in history] == [1, 2, 3]


# Test ExampleDatabase
def test_example_database(temp_db):
    db = ExampleDatabase(temp_db)
    examples = ExampleSet(
        inputs=[{"x": 1}, {"x": 2}],
        outputs=[{"y": 2}, {"y": 4}],
        weights=[1.0, 1.0],
    )

    db.save_examples(examples)
    loaded_examples = db.load_examples()

    assert len(loaded_examples.inputs) == 2
    assert loaded_examples.inputs[0]["x"] == 1
    assert loaded_examples.outputs[1]["y"] == 4
    assert loaded_examples.weights == [1.0, 1.0]


def test_example_database_empty(temp_db):
    db = ExampleDatabase(temp_db)
    examples = db.load_examples()
    assert len(examples.inputs) == 0
    assert len(examples.outputs) == 0
    assert len(examples.weights) == 0


# Test MetricHistory
def test_metric_history():
    history = MetricHistory(max_size=3)
    metrics = [
        TuningMetrics(loss=0.5, accuracy=0.8, duration=1.0, iteration=1),
        TuningMetrics(loss=0.4, accuracy=0.85, duration=1.0, iteration=2),
        TuningMetrics(loss=0.3, accuracy=0.9, duration=1.0, iteration=3),
        TuningMetrics(loss=0.2, accuracy=0.95, duration=1.0, iteration=4),
    ]

    for metric in metrics:
        history.add_metric(metric)

    assert len(history.metrics) == 3
    assert history.metrics[-1]["loss"] == 0.2

    trend = history.get_trend(window=2)
    assert len(trend) == 2
    assert trend[0] == pytest.approx((0.3 + 0.4) / 2)


def test_metric_history_no_limit():
    history = MetricHistory()
    metrics = [
        TuningMetrics(loss=0.5, accuracy=0.8, duration=1.0, iteration=1),
        TuningMetrics(loss=0.4, accuracy=0.85, duration=1.0, iteration=2),
    ]

    for metric in metrics:
        history.add_metric(metric)

    assert len(history.metrics) == 2
    trend = history.get_trend()
    assert len(trend) == 1
    assert trend[0] == pytest.approx(0.45)


def test_metric_history_empty():
    history = MetricHistory()
    assert history.get_trend() == []
