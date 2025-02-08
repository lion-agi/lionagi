from typing import Any, Dict

import numpy as np
import pytest

from lionagi.operatives.tuning.optimizer import (
    BaseOptimizer,
    BayesianOptimizer,
    GridSearchOptimizer,
    RandomSearchOptimizer,
)
from lionagi.operatives.tuning.protocols import OptimizationState


class MockOptimizationState(OptimizationState):
    """Mock optimization state for testing."""

    def __init__(self, search_space: dict[str, Any]):
        self.search_space = search_space
        self.best_score = float("-inf")
        self.iterations = 0
        self.history = []


@pytest.fixture
def simple_search_space():
    """Fixture providing a simple parameter search space."""
    return {
        "x": {"type": "float", "min": -5.0, "max": 5.0},
        "y": {"type": "int", "min": -5, "max": 5},
    }


@pytest.fixture
def complex_search_space():
    """Fixture providing a more complex parameter search space."""
    return {
        "learning_rate": {
            "type": "float",
            "min": 0.0001,
            "max": 0.1,
            "log": True,
        },
        "batch_size": {"type": "int", "values": [16, 32, 64, 128]},
        "layers": {"type": "int", "min": 1, "max": 5},
        "activation": {
            "type": "categorical",
            "values": ["relu", "tanh", "sigmoid"],
        },
    }


class TestGridSearchOptimizer:
    """Test suite for GridSearchOptimizer."""

    def test_initialization(self, simple_search_space):
        """Test proper initialization of GridSearchOptimizer."""
        optimizer = GridSearchOptimizer(simple_search_space, num_points=5)
        assert optimizer.search_space == simple_search_space
        assert optimizer.num_points == 5
        assert not optimizer.explored_params

    def test_parameter_generation(self, simple_search_space):
        """Test parameter generation within constraints."""
        optimizer = GridSearchOptimizer(simple_search_space, num_points=3)
        state = MockOptimizationState(simple_search_space)

        params = optimizer.explore_parameters()
        assert "x" in params and "y" in params
        assert -5.0 <= params["x"] <= 5.0
        assert -5 <= params["y"] <= 5

    def test_grid_coverage(self, simple_search_space):
        """Test if grid search covers the space systematically."""
        optimizer = GridSearchOptimizer(simple_search_space, num_points=5)
        seen_params = set()

        for _ in range(25):  # Should cover all combinations
            params = optimizer.explore_parameters()
            param_tuple = (params["x"], params["y"])
            seen_params.add(param_tuple)

        assert len(seen_params) == 25  # 5x5 grid


class TestRandomSearchOptimizer:
    """Test suite for RandomSearchOptimizer."""

    def test_initialization(self, complex_search_space):
        """Test proper initialization of RandomSearchOptimizer."""
        optimizer = RandomSearchOptimizer(complex_search_space)
        assert optimizer.search_space == complex_search_space
        assert not optimizer.explored_params

    def test_random_sampling(self, complex_search_space):
        """Test random sampling within constraints."""
        optimizer = RandomSearchOptimizer(complex_search_space)
        samples = [optimizer.explore_parameters() for _ in range(10)]

        # Test numerical constraints
        assert all(0.0001 <= s["learning_rate"] <= 0.1 for s in samples)
        assert all(1 <= s["layers"] <= 5 for s in samples)

        # Test categorical constraints
        assert all(s["batch_size"] in [16, 32, 64, 128] for s in samples)
        assert all(
            s["activation"] in ["relu", "tanh", "sigmoid"] for s in samples
        )

    def test_distribution(self, simple_search_space):
        """Test if random search provides good coverage."""
        optimizer = RandomSearchOptimizer(simple_search_space)
        samples = [optimizer.explore_parameters() for _ in range(100)]

        x_values = [s["x"] for s in samples]
        y_values = [s["y"] for s in samples]

        # Basic statistical checks
        assert -5.0 <= min(x_values) <= -3.0  # Should reach lower range
        assert 3.0 <= max(x_values) <= 5.0  # Should reach upper range
        assert -5 <= min(y_values) <= -3  # Should reach lower range
        assert 3 <= max(y_values) <= 5  # Should reach upper range


class TestBayesianOptimizer:
    """Test suite for BayesianOptimizer."""

    def test_initialization(self, simple_search_space):
        """Test proper initialization of BayesianOptimizer."""
        optimizer = BayesianOptimizer(simple_search_space)
        assert optimizer.search_space == simple_search_space
        assert optimizer.gp is not None
        assert not optimizer.X
        assert not optimizer.y

    def test_exploration_exploitation_balance(self, simple_search_space):
        """Test balance between exploration and exploitation."""
        optimizer = BayesianOptimizer(simple_search_space)
        state = MockOptimizationState(simple_search_space)

        # Initial random sampling
        first_params = optimizer.explore_parameters()
        assert -5.0 <= first_params["x"] <= 5.0
        assert -5 <= first_params["y"] <= 5

        # Simulate optimization
        for i in range(5):
            params = optimizer.explore_parameters()
            score = -(
                params["x"] ** 2 + params["y"] ** 2
            )  # Simple quadratic function
            optimizer.update(params, score)

        # Check if optimization improves scores
        assert len(optimizer.X) == 6  # Initial + 5 iterations
        assert len(optimizer.y) == 6

        # Scores should generally improve
        scores = optimizer.y.tolist()
        assert max(scores[3:]) >= max(scores[:3])

    def test_convergence(self, simple_search_space):
        """Test if optimizer converges to optimal region."""
        optimizer = BayesianOptimizer(simple_search_space)

        # Optimize simple quadratic function
        best_score = float("-inf")
        for _ in range(20):
            params = optimizer.explore_parameters()
            score = -(params["x"] ** 2 + params["y"] ** 2)  # Optimal at (0,0)
            optimizer.update(params, score)
            best_score = max(best_score, score)

        # Should have found a point close to optimal
        final_params = optimizer.explore_parameters()
        assert abs(final_params["x"]) < 1.0
        assert abs(final_params["y"]) < 1.0


def test_optimizer_integration(complex_search_space):
    """Test integration of different optimizers with same search space."""
    optimizers = [
        GridSearchOptimizer(complex_search_space, num_points=3),
        RandomSearchOptimizer(complex_search_space),
        BayesianOptimizer(complex_search_space),
    ]

    for optimizer in optimizers:
        # Test basic optimization loop
        for _ in range(5):
            params = optimizer.explore_parameters()

            # Verify parameter constraints
            assert 0.0001 <= params["learning_rate"] <= 0.1
            assert params["batch_size"] in [16, 32, 64, 128]
            assert 1 <= params["layers"] <= 5
            assert params["activation"] in ["relu", "tanh", "sigmoid"]

            # Simulate evaluation
            score = np.random.random()
            if hasattr(optimizer, "update"):
                optimizer.update(params, score)


def test_error_handling():
    """Test error handling in optimizers."""
    # Test invalid search space
    invalid_space = {"x": {"type": "invalid"}}
    with pytest.raises(ValueError):
        GridSearchOptimizer(invalid_space)

    # Test invalid parameter ranges
    invalid_range = {"x": {"type": "float", "min": 5.0, "max": 1.0}}
    with pytest.raises(ValueError):
        RandomSearchOptimizer(invalid_range)

    # Test missing required fields
    missing_fields = {"x": {"type": "float"}}
    with pytest.raises(ValueError):
        BayesianOptimizer(missing_fields)
