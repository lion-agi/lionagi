"""
Parameter Compilation

This module handles the compilation and validation of parameter configurations,
ensuring type safety and constraint satisfaction.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from lionagi._errors import ItemNotFoundError, ValidationError

from .examples import Example
from .parameter_state import TuningState
from .types import Parameter, ParameterType


class ParameterValidationError(ValidationError):
    """Raised when parameter validation fails"""

    pass


class ExampleValidationError(ValidationError):
    """Raised when example validation fails"""

    pass


class TuningCompiler:
    """Compiles and optimizes parameter tuning configurations.

    Handles validation, normalization and optimization of parameter configurations
    for tuning tasks. Supports example-based validation and search space constraints.

    Attributes:
        _search_space: Dictionary mapping parameter names to their valid ranges/constraints
        _examples: List of (input, output) tuples for validation
    """

    def __init__(self, search_space: dict[str, Any] = None):
        """Initialize compiler with optional search space definition.

        Args:
            search_space: Optional dictionary defining parameter constraints

        Raises:
            ValueError: If search space contains invalid parameters
        """
        self._search_space = search_space or {}
        self._examples: list[tuple[Any, Any]] = []

        # Validate search space parameters
        for name, param in self._search_space.items():
            if not isinstance(param, Parameter):
                raise ValueError(
                    f"Search space parameter {name} must be a Parameter instance, got {type(param)}"
                )

    def add_example(self, example: Example) -> None:
        """Add a training example for validation.

        Args:
            example: Example object containing input_data and expected_output

        Raises:
            ExampleValidationError: If example format is invalid
        """
        if not hasattr(example, "input_data") or not hasattr(
            example, "expected_output"
        ):
            raise ExampleValidationError(
                "Example must have input_data and expected_output"
            )

        # Validate input data matches parameter types
        if isinstance(example.input_data, dict):
            for param_name, value in example.input_data.items():
                if param_name in self._search_space:
                    param = self._search_space[param_name]
                    try:
                        if not param.validate(value):
                            raise ExampleValidationError(
                                f"Example input '{param_name}' with value {value} "
                                f"does not match parameter constraints"
                            )
                    except Exception as e:
                        raise ExampleValidationError(
                            f"Failed to validate example input '{param_name}': {str(e)}"
                        )

        self._examples.append((example.input_data, example.expected_output))

    def optimize_prompt(self, prompt_template: str) -> str:
        """Optimize prompt structure and ordering.

        Args:
            prompt_template: Template string to optimize

        Returns:
            Optimized prompt template
        """
        # TODO: Implement prompt optimization logic
        return prompt_template

    def define_search_space(self, param_name: str, param_range: Any) -> None:
        """Define parameter search ranges.

        Args:
            param_name: Name of parameter
            param_range: Valid range/constraints for parameter
        """
        self._search_space[param_name] = param_range

    def validate(self, param_values: dict[str, Any]) -> bool:
        """Validate parameter values against constraints.

        Args:
            param_values: Dictionary of parameter values to validate

        Returns:
            True if valid

        Raises:
            ItemNotFoundError: If parameter not found in search space
            ValueError: If parameters violate constraints
        """
        # Check all params exist in search space
        for name in param_values:
            if name not in self._search_space:
                raise ItemNotFoundError(
                    f"Parameter {name} not found in search space"
                )

        self._validate_search_space(param_values)
        self._validate_examples(param_values)
        return True

    def compile(self, params: dict[str, Any]) -> dict[str, Any]:
        """Compile validated parameter configuration.

        Args:
            params: Parameter values to compile and validate

        Returns:
            Normalized and validated parameter configuration

        Raises:
            ValueError: If configuration is invalid
        """
        config = self._normalize_config(params)
        if self.validate(config):
            return config
        raise ValueError("Invalid parameter configuration")

    def _validate_search_space(self, params: dict[str, Any]) -> None:
        """Check params are within defined ranges.

        Args:
            params: Parameter values to validate

        Raises:
            ParameterValidationError: If parameters violate constraints
        """
        # Check for required parameters
        for name, param in self._search_space.items():
            if param.required and name not in params:
                raise ParameterValidationError(
                    f"Required parameter '{name}' is missing"
                )

        for name, value in params.items():
            if name in self._search_space:
                param = self._search_space[name]

                # Handle None values
                if value is None:
                    if param.required:
                        raise ParameterValidationError(
                            f"Required parameter '{name}' cannot be None"
                        )
                    continue

                try:
                    if not param.validate(value):
                        if (
                            param.type == ParameterType.NUMERIC
                            and param.bounds
                        ):
                            raise ParameterValidationError(
                                f"Parameter '{name}' value {value} is outside "
                                f"bounds [{param.bounds[0]}, {param.bounds[1]}]"
                            )
                        elif (
                            param.type == ParameterType.CATEGORICAL
                            and param.choices
                        ):
                            raise ParameterValidationError(
                                f"Parameter '{name}' value {value} must be one of: "
                                f"{param.choices}"
                            )
                        else:
                            raise ParameterValidationError(
                                f"Parameter '{name}' value {value} is invalid"
                            )
                except Exception as e:
                    raise ParameterValidationError(
                        f"Failed to validate parameter '{name}': {str(e)}"
                    )

    def _validate_examples(self, params: dict[str, Any]) -> None:
        """Validate against provided examples.

        Args:
            params: Parameter values to validate

        Raises:
            ExampleValidationError: If parameters fail example validation
        """
        if not self._examples:
            return

        for idx, (input_data, expected) in enumerate(self._examples):
            # Validate input structure
            if not isinstance(input_data, dict):
                raise ExampleValidationError(
                    f"Example {idx}: Input data must be a dictionary"
                )

            # Check parameter types match example
            for name, value in input_data.items():
                if name in params:
                    param_value = params[name]
                    if not isinstance(param_value, type(value)):
                        raise ExampleValidationError(
                            f"Example {idx}: Parameter '{name}' type mismatch. "
                            f"Expected {type(value)}, got {type(param_value)}"
                        )

            # Validate required parameters are present
            for name, param in self._search_space.items():
                if param.required and name not in input_data:
                    raise ExampleValidationError(
                        f"Example {idx}: Missing required parameter '{name}'"
                    )

    def _normalize_config(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create normalized parameter configuration.

        Args:
            params: Initial parameter values

        Returns:
            Normalized configuration dictionary
        """
        config = params.copy()
        for name, constraints in self._search_space.items():
            if name not in config and isinstance(constraints, Parameter):
                # Use default value if not specified
                config[name] = getattr(constraints, "default", None)
        return config
