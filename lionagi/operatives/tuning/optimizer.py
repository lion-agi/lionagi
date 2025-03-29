"""
Parameter Optimization

This module provides optimization algorithms and strategies for
parameter tuning, including gradient-based and evolutionary approaches.
"""

import random
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np
from scipy.stats import norm


@dataclass
class OptimizationState:
    """Tracks optimization progress."""

    iteration: int = 0
    best_score: float = float("-inf")
    best_params: dict[str, Any] = None
    history: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


class BaseOptimizer(ABC):
    """Base class for parameter optimizers."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._state: OptimizationState | None = OptimizationState()

    @abstractmethod
    def optimize(self) -> Iterator[dict[str, Any]]:
        """Run optimization process."""
        pass

    def early_stopping(self) -> bool:
        """Check early stopping conditions."""
        if not self._state:
            return False

        iterations_without_improvement = 0
        patience = self.config.get("patience", 10)
        tolerance = self.config.get("tolerance", 1e-4)

        if len(self._state.history) > patience:
            recent_scores = [
                h.get("score", float("-inf"))
                for h in self._state.history[-patience:]
            ]

            if max(recent_scores) - self._state.best_score < tolerance:
                return True

        return False

    @abstractmethod
    def explore_parameters(self) -> dict[str, Any]:
        """Generate next set of parameters to try."""
        pass


class GridSearchOptimizer(BaseOptimizer):
    """Grid search optimization strategy."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.param_grid = self._create_param_grid()
        self.current_idx = 0

    def _validate_param_ranges(self, param_ranges: dict[str, Any]) -> None:
        """Validate parameter ranges configuration."""
        if not param_ranges:
            raise ValueError("param_ranges cannot be empty")

        for param, range_info in param_ranges.items():
            if isinstance(range_info, dict):
                if "type" not in range_info:
                    raise ValueError(f"Missing type for parameter {param}")

                if range_info["type"] in ("float", "int"):
                    if not ("min" in range_info and "max" in range_info):
                        raise ValueError(
                            f"Missing min/max for numeric parameter {param}"
                        )
                    if range_info["min"] >= range_info["max"]:
                        raise ValueError(
                            f"Invalid range for {param}: min >= max"
                        )

                elif range_info["type"] == "categorical":
                    if not range_info.get("values"):
                        raise ValueError(
                            f"Empty values for categorical parameter {param}"
                        )
            else:
                raise ValueError(
                    f"Invalid range specification for parameter {param}"
                )

    def _create_param_grid(self):
        """Create grid of parameter combinations."""
        param_ranges = self.config.get("param_ranges", {})
        self._validate_param_ranges(param_ranges)
        grid_points = []

        # Create cartesian product of parameter values
        params_space = {}
        for param, range_info in param_ranges.items():
            if range_info["type"] in ("float", "int"):
                num_points = range_info.get("num_points", 5)
                if range_info["type"] == "float":
                    values = np.linspace(
                        range_info["min"], range_info["max"], num_points
                    )
                else:
                    values = np.linspace(
                        range_info["min"],
                        range_info["max"],
                        num_points,
                        dtype=int,
                    )
                params_space[param] = values
            else:  # categorical
                params_space[param] = range_info["values"]

        # Generate grid points
        keys = list(params_space.keys())
        values = [params_space[k] for k in keys]

        for v in np.ndindex(tuple(len(val) for val in values)):
            params = {k: values[i][v[i]] for i, k in enumerate(keys)}
            grid_points.append(params)

        return grid_points

    def optimize(self) -> Iterator[dict[str, Any]]:
        """Iterate through grid points."""
        while self.current_idx < len(self.param_grid):
            if self.early_stopping():
                break

            params = self.explore_parameters()
            self._state.iteration += 1
            yield params

    def explore_parameters(self) -> dict[str, Any]:
        """Get next grid point."""
        if self.current_idx >= len(self.param_grid):
            return None

        params = self.param_grid[self.current_idx]
        self.current_idx += 1
        return params


class RandomSearchOptimizer(BaseOptimizer):
    """Random search optimization strategy."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._validate_param_ranges(self.config.get("param_ranges", {}))
        self._state.explored_params = set()

    def _validate_param_ranges(self, param_ranges: dict[str, Any]) -> None:
        """Validate parameter ranges configuration."""
        if not param_ranges:
            raise ValueError("param_ranges cannot be empty")

        for param, range_info in param_ranges.items():
            if isinstance(range_info, dict):
                if "type" not in range_info:
                    raise ValueError(f"Missing type for parameter {param}")

                if range_info["type"] in ("float", "int"):
                    if not ("min" in range_info and "max" in range_info):
                        raise ValueError(
                            f"Missing min/max for numeric parameter {param}"
                        )
                    if range_info["min"] >= range_info["max"]:
                        raise ValueError(
                            f"Invalid range for {param}: min >= max"
                        )

                elif range_info["type"] == "categorical":
                    if not range_info.get("values"):
                        raise ValueError(
                            f"Empty values for categorical parameter {param}"
                        )
            else:
                raise ValueError(
                    f"Invalid range specification for parameter {param}"
                )

    def optimize(self) -> Iterator[dict[str, Any]]:
        """Generate random parameter combinations."""
        max_iterations = self.config.get("max_iterations", 100)

        while self._state.iteration < max_iterations:
            if self.early_stopping():
                break

            params = self.explore_parameters()
            if params:
                self._state.iteration += 1
                self._state.explored_params.add(tuple(sorted(params.items())))
                yield params
            else:
                break

    def explore_parameters(self) -> dict[str, Any]:
        """Sample random point in parameter space."""
        param_ranges = self.config.get("param_ranges", {})
        max_attempts = 100  # Prevent infinite loops

        for _ in range(max_attempts):
            params = {}
            for param, range_info in param_ranges.items():
                if range_info["type"] == "float":
                    params[param] = random.uniform(
                        range_info["min"], range_info["max"]
                    )
                elif range_info["type"] == "int":
                    params[param] = random.randint(
                        range_info["min"], range_info["max"]
                    )
                else:  # categorical
                    params[param] = random.choice(range_info["values"])

            # Check if this combination was already explored
            param_tuple = tuple(sorted(params.items()))
            if param_tuple not in self._state.explored_params:
                return params

        return None  # Could not find unexplored combination


class BayesianOptimizer(BaseOptimizer):
    """Bayesian optimization strategy using Gaussian Processes."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._validate_param_ranges(self.config.get("param_ranges", {}))

        try:
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import RBF, ConstantKernel

            kernel = ConstantKernel(1.0) * RBF([1.0])
            self.gp = GaussianProcessRegressor(
                kernel=kernel, n_restarts_optimizer=5
            )
        except ImportError:
            raise ImportError("sklearn is required for BayesianOptimizer")

        self.X_observed = []
        self.y_observed = []
        self._state.explored_params = set()

    def _validate_param_ranges(self, param_ranges: dict[str, Any]) -> None:
        """Validate parameter ranges configuration."""
        if not param_ranges:
            raise ValueError("param_ranges cannot be empty")

        for param, range_info in param_ranges.items():
            if isinstance(range_info, dict):
                if "type" not in range_info:
                    raise ValueError(f"Missing type for parameter {param}")

                if range_info["type"] in ("float", "int"):
                    if not ("min" in range_info and "max" in range_info):
                        raise ValueError(
                            f"Missing min/max for numeric parameter {param}"
                        )
                    if range_info["min"] >= range_info["max"]:
                        raise ValueError(
                            f"Invalid range for {param}: min >= max"
                        )

                elif range_info["type"] == "categorical":
                    if not range_info.get("values"):
                        raise ValueError(
                            f"Empty values for categorical parameter {param}"
                        )
            else:
                raise ValueError(
                    f"Invalid range specification for parameter {param}"
                )

    def _expected_improvement(self, X: np.ndarray) -> np.ndarray:
        """Calculate expected improvement acquisition function."""
        try:
            mu, sigma = self.gp.predict(X, return_std=True)
            best_f = np.max(self.y_observed)

            with np.errstate(divide="warn"):
                imp = mu - best_f
                Z = imp / sigma
                ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
                ei[sigma == 0.0] = 0.0

            return ei
        except Exception as e:
            print(f"Warning: EI calculation failed: {str(e)}")
            return np.zeros(X.shape[0])

    def optimize(self) -> Iterator[dict[str, Any]]:
        """Run Bayesian optimization process."""
        max_iterations = self.config.get("max_iterations", 50)

        # Initial random exploration
        n_initial = min(5, max_iterations)
        random_optimizer = RandomSearchOptimizer(self.config)

        for _ in range(n_initial):
            params = random_optimizer.explore_parameters()
            if params:
                self._state.iteration += 1
                self._state.explored_params.add(tuple(sorted(params.items())))
                yield params

        # Bayesian optimization loop
        while self._state.iteration < max_iterations:
            if self.early_stopping():
                break

            params = self.explore_parameters()
            if params:
                self._state.iteration += 1
                self._state.explored_params.add(tuple(sorted(params.items())))
                yield params
            else:
                break

    def explore_parameters(self) -> dict[str, Any]:
        """Use acquisition function to propose next point."""
        if len(self.X_observed) == 0:
            return RandomSearchOptimizer(self.config).explore_parameters()

        try:
            self.gp.fit(self.X_observed, self.y_observed)
        except Exception as e:
            print(f"Warning: GP fit failed: {str(e)}")
            return RandomSearchOptimizer(self.config).explore_parameters()

        # Generate candidate points
        n_candidates = 1000
        random_optimizer = RandomSearchOptimizer(self.config)
        candidates = []
        for _ in range(n_candidates):
            params = random_optimizer.explore_parameters()
            if params:
                candidates.append(params)

        if not candidates:
            return None

        # Convert candidates to array format
        X_candidates = np.array(
            [[p[k] for k in sorted(p.keys())] for p in candidates]
        )

        # Calculate expected improvement
        ei_values = self._expected_improvement(X_candidates)
        best_idx = np.argmax(ei_values)

        return candidates[best_idx]
