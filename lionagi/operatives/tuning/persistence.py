"""
Persistence Implementation

This module implements persistence mechanisms for tuning state,
results, examples, and metric history.
"""

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .protocols import BaseResultTracker, BaseStateManager
from .types import (
    ExampleSet,
    OptimizationState,
    Parameter,
    ParameterSet,
    TuningMetrics,
)


@dataclass
class FileStateManager(BaseStateManager[OptimizationState]):
    """Manages optimization state persistence to files."""

    filepath: str | Path

    def save_state(self, state: OptimizationState) -> None:
        """Save state to JSON file."""
        with open(self.filepath, "w") as f:
            json.dump(state, f)

    def load_state(self) -> OptimizationState | None:
        """Load state from JSON file."""
        try:
            with open(self.filepath) as f:
                return OptimizationState(**json.load(f))
        except FileNotFoundError:
            return None

    def clear_state(self) -> None:
        """Remove state file."""
        Path(self.filepath).unlink(missing_ok=True)


@dataclass
class SQLiteResultTracker(BaseResultTracker[TuningMetrics]):
    """Tracks optimization results in SQLite database."""

    db_path: str | Path
    table_name: str = "tuning_results"

    def __post_init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    loss REAL,
                    accuracy REAL,
                    duration REAL,
                    iteration INTEGER,
                    additional_metrics TEXT
                )
            """
            )

    def add_result(self, result: TuningMetrics) -> None:
        """Add new result to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"""INSERT INTO {self.table_name}
                    (timestamp, loss, accuracy, duration, iteration, additional_metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    result["loss"],
                    result["accuracy"],
                    result["duration"],
                    result["iteration"],
                    json.dumps(result["additional_metrics"]),
                ),
            )

    def get_best_result(self) -> TuningMetrics | None:
        """Get result with lowest loss."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                f"SELECT * FROM {self.table_name} ORDER BY loss ASC LIMIT 1"
            ).fetchone()
            if row:
                return self._row_to_metrics(row)
        return None

    def get_history(self) -> Sequence[TuningMetrics]:
        """Get all results ordered by iteration."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT * FROM {self.table_name} ORDER BY iteration ASC"
            ).fetchall()
            return [self._row_to_metrics(row) for row in rows]

    def _row_to_metrics(self, row) -> TuningMetrics:
        """Convert database row to TuningMetrics."""
        return TuningMetrics(
            loss=row[2],
            accuracy=row[3],
            duration=row[4],
            iteration=row[5],
            additional_metrics=json.loads(row[6]),
        )


@dataclass
class ExampleDatabase:
    """Persistent storage for training examples."""

    db_path: str | Path

    def __post_init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS examples (
                    id INTEGER PRIMARY KEY,
                    input TEXT,
                    output TEXT,
                    weight REAL
                )
            """
            )

    def save_examples(self, examples: ExampleSet) -> None:
        """Save example set to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT INTO examples (input, output, weight) VALUES (?, ?, ?)",
                [
                    (json.dumps(x), json.dumps(y), w if w is not None else 1.0)
                    for x, y, w in zip(
                        examples.inputs,
                        examples.outputs,
                        examples.weights or [1.0] * len(examples.inputs),
                    )
                ],
            )

    def load_examples(self) -> ExampleSet:
        """Load all examples from database."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT input, output, weight FROM examples"
            ).fetchall()
            return ExampleSet(
                inputs=[json.loads(row[0]) for row in rows],
                outputs=[json.loads(row[1]) for row in rows],
                weights=[row[2] for row in rows],
            )


@dataclass
class MetricHistory:
    """Tracks metric history with efficient storage."""

    metrics: list[TuningMetrics] = field(default_factory=list)
    max_size: int | None = None

    def add_metric(self, metric: TuningMetrics) -> None:
        """Add new metric, maintaining size limit."""
        self.metrics.append(metric)
        if self.max_size and len(self.metrics) > self.max_size:
            self.metrics.pop(0)

    def get_trend(self, window: int = 10) -> list[float]:
        """Get moving average of loss values."""
        if not self.metrics:
            return []
        losses = [m["loss"] for m in self.metrics]
        return [
            sum(losses[i : i + window]) / min(window, len(losses) - i)
            for i in range(0, len(losses) - window + 1)
        ]
