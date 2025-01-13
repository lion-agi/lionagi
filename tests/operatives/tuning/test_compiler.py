from typing import Any, Dict

import pytest

from lionagi._errors import ItemNotFoundError, OperationError
from lionagi.operatives.tuning.compiler import TuningCompiler
from lionagi.operatives.tuning.examples import Example
from lionagi.operatives.tuning.types import Parameter, ParameterType


@pytest.fixture
def basic_compiler():
    """Creates a basic TuningCompiler instance with simple search space."""
    search_space = {
        "learning_rate": Parameter(
            type=ParameterType.NUMERIC, default=0.001, bounds=(0.0001, 0.1)
        ),
        "batch_size": Parameter(
            type=ParameterType.DISCRETE, default=32, bounds=(8, 128)
        ),
    }

    # Set names from keys before passing to compiler
    for name, param in search_space.items():
        param.name = name

    return TuningCompiler(search_space=search_space)


@pytest.fixture
def example_data():
    """Sample training examples."""
    return [
        Example(
            input_data={"x": 1},
            expected_output={"y": 2},
            metadata={"score": 0.95},
        ),
        Example(
            input_data={"x": 2},
            expected_output={"y": 4},
            metadata={"score": 0.98},
        ),
    ]


class TestTuningCompiler:
    """Test suite for TuningCompiler class."""

    def test_initialization(self, basic_compiler):
        """Test basic initialization with search space."""
        assert basic_compiler._search_space is not None
        assert len(basic_compiler._search_space) == 2
        assert "learning_rate" in basic_compiler._search_space
        assert "batch_size" in basic_compiler._search_space

    def test_add_example(self, basic_compiler, example_data):
        """Test adding valid examples."""
        basic_compiler.add_example(example_data[0])
        assert len(basic_compiler._examples) == 1

        basic_compiler.add_example(example_data[1])
        assert len(basic_compiler._examples) == 2

    def test_validate_params(self, basic_compiler):
        """Test parameter validation against search space."""
        valid_params = {"learning_rate": 0.01, "batch_size": 64}
        assert basic_compiler.validate(valid_params) == True

        invalid_params = {
            "learning_rate": 0.2,  # Outside bounds
            "batch_size": 64,
        }
        assert basic_compiler.validate(invalid_params) == False

    def test_compile_params(self, basic_compiler):
        """Test parameter compilation and normalization."""
        params = {"learning_rate": 0.01, "batch_size": 64}
        compiled = basic_compiler.compile(params)
        assert isinstance(compiled, dict)
        assert all(key in compiled for key in params)
        assert compiled["learning_rate"] == 0.01
        assert compiled["batch_size"] == 64

    def test_error_handling(self, basic_compiler):
        """Test error cases and invalid inputs."""
        with pytest.raises(ItemNotFoundError):
            basic_compiler.validate({"invalid_param": 1.0})

        with pytest.raises(OperationError):
            basic_compiler.compile(
                {"learning_rate": "invalid", "batch_size": 64}  # Wrong type
            )

    def test_search_space_validation(self):
        """Test search space validation during initialization."""
        with pytest.raises(ValueError):
            TuningCompiler(
                search_space={"param": "invalid"}  # Not a Parameter instance
            )

    def test_example_validation(self, basic_compiler):
        """Test example validation logic."""
        invalid_example = Example(
            input_data={"invalid": True}, expected_output={}, metadata={}
        )

        with pytest.raises(ValueError):
            basic_compiler.add_example(invalid_example)

    def test_parameter_bounds(self, basic_compiler):
        """Test parameter bounds enforcement."""
        params = {
            "learning_rate": 0.0001,  # At lower bound
            "batch_size": 128,  # At upper bound
        }
        assert basic_compiler.validate(params) == True

        params = {
            "learning_rate": 0.00009,  # Below lower bound
            "batch_size": 129,  # Above upper bound
        }
        assert basic_compiler.validate(params) == False
