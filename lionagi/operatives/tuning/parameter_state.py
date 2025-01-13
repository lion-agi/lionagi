"""
Parameter State Management

This module handles the state management of tunable parameters,
including tracking, versioning, and persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ...protocols.generic import Element
from ...utils import time


@dataclass
class MetricRecord:
    """Records metrics for a parameter state."""

    timestamp: float
    metrics: dict[str, float]
    parameters: dict[str, Any]


class TuningState(Element):
    """Manages the state and history of tunable parameters.

    Tracks current parameter values, enforces constraints, and maintains
    a history of parameter states and their associated metrics.

    Attributes:
        parameters: Current parameter values
        constraints: Valid ranges/options for parameters
        history: Record of past states and metrics
    """

    def __init__(
        self,
        parameters: dict[str, Any],
        constraints: dict[str, dict[str, Any]] | None = None,
    ):
        """Initialize tuning state.

        Args:
            parameters: Initial parameter values
            constraints: Parameter constraints (optional)
        """
        super().__init__()
        self.parameters = parameters
        self.constraints = constraints or {}
        self.history: list[MetricRecord] = []

    def validate_state(self) -> bool:
        """Validate current parameters against constraints.

        Returns:
            bool: True if all parameters are valid

        Raises:
            ValueError: If any parameter violates constraints
        """
        if not self.constraints:
            return True

        for param, value in self.parameters.items():
            if param in self.constraints:
                constraint = self.constraints[param]
                if "min" in constraint and value < constraint["min"]:
                    raise ValueError(f"{param} below minimum: {value}")
                if "max" in constraint and value > constraint["max"]:
                    raise ValueError(f"{param} above maximum: {value}")
                if (
                    "options" in constraint
                    and value not in constraint["options"]
                ):
                    raise ValueError(f"Invalid {param} value: {value}")
        return True

    def update_parameters(self, updates: dict[str, Any]) -> None:
        """Update parameter values.

        Args:
            updates: Parameter updates to apply

        Raises:
            ValueError: If updates violate constraints
        """
        new_params = self.parameters.copy()
        new_params.update(updates)

        # Create temporary state to validate
        temp_state = TuningState(new_params, self.constraints)
        if temp_state.validate_state():
            self.parameters = new_params

    def record_metrics(self, metrics: dict[str, float]) -> None:
        """Record metrics for current parameter state.

        Args:
            metrics: Dictionary of metric names and values
        """
        record = MetricRecord(
            timestamp=time(),
            metrics=metrics,
            parameters=self.parameters.copy(),
        )
        self.history.append(record)

    def save_state(self) -> dict[str, Any]:
        """Serialize state for persistence.

        Returns:
            Dictionary containing complete state
        """
        return {
            "parameters": self.parameters,
            "constraints": self.constraints,
            "history": [
                {
                    "timestamp": record.timestamp,
                    "metrics": record.metrics,
                    "parameters": record.parameters,
                }
                for record in self.history
            ],
        }

    @classmethod
    def load_state(cls, state_dict: dict[str, Any]) -> "TuningState":
        """Create TuningState from serialized state.

        Args:
            state_dict: Dictionary containing serialized state

        Returns:
            New TuningState instance
        """
        instance = cls(
            parameters=state_dict["parameters"],
            constraints=state_dict["constraints"],
        )

        # Reconstruct history
        instance.history = [
            MetricRecord(
                timestamp=h["timestamp"],
                metrics=h["metrics"],
                parameters=h["parameters"],
            )
            for h in state_dict["history"]
        ]
        return instance
