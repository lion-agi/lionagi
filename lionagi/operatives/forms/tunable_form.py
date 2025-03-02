from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import UNDEFINED, Field, validator

from ...utils import to_dict
from .form import Form


class TuningState(str, Enum):
    """Enumeration of possible tuning states."""

    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TunableForm(Form):
    """Form with parameter tuning and example management capabilities.

    Extends the base Form class to support parameter tuning workflows,
    including example set management, tuning state tracking, and
    optimization metric collection.

    Attributes:
        parameters (Dict[str, Any]):
            Current parameter set being evaluated
        parameter_constraints (Dict[str, Dict]):
            Validation rules and bounds for parameters
        examples (List[Dict]):
            Training/validation examples for tuning
        tuning_state (TuningState):
            Current state of the tuning process
        results (Dict[str, Any]):
            Collected metrics and results
        best_parameters (Dict[str, Any]):
            Best performing parameter set found
    """

    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Current parameter set"
    )

    parameter_constraints: Dict[str, Dict] = Field(
        default_factory=dict, description="Parameter validation rules"
    )

    examples: List[Dict] = Field(
        default_factory=list, description="Training examples"
    )

    tuning_state: TuningState = Field(
        default=TuningState.INITIALIZED, description="Current tuning state"
    )

    results: Dict[str, Any] = Field(
        default_factory=dict, description="Collected metrics"
    )

    best_parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Best parameter set"
    )

    metaprompt: str = Field(default="", description="Metaprompt template")

    metaprompt_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="History of metaprompt results"
    )

    @validator("examples")
    def validate_examples(cls, v):
        """Validate training examples format."""
        if not isinstance(v, list):
            raise TypeError("Examples must be a list")
        for example in v:
            if not isinstance(example, dict):
                raise TypeError("Example must be a dictionary")
            if not all(k in example for k in ("parameters", "score")):
                raise ValueError(
                    "Example must contain 'parameters' and 'score'"
                )
            if not isinstance(example["parameters"], dict):
                raise ValueError("Example parameters must be a dictionary")
        return v

    @validator("parameter_constraints")
    def validate_constraints(cls, v: Dict) -> Dict:
        """Validates parameter constraint definitions."""
        for param, constraints in v.items():
            if not isinstance(constraints, dict):
                raise ValueError(
                    f"Constraints for {param} must be a dictionary"
                )
            required_keys = {"type", "bounds"}
            if not all(key in constraints for key in required_keys):
                raise ValueError(
                    f"Constraints for {param} missing required keys: {required_keys}"
                )
        return v

    def add_example(self, example: Dict[str, Any]) -> None:
        """Add a training example."""
        if not isinstance(example, dict):
            raise TypeError("Example must be a dictionary")
        if not all(k in example for k in ("parameters", "score")):
            raise ValueError("Example must contain 'parameters' and 'score'")
        if not isinstance(example["parameters"], dict):
            raise ValueError("Example parameters must be a dictionary")
        self.examples.append(example)

    def add_examples(self, examples: List[Dict[str, Any]]) -> None:
        """Adds multiple examples to the training set.

        Args:
            examples: List of example dictionaries
        """
        self.examples.extend(examples)

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set form parameter values."""
        if self.validate_params(params):
            self.parameters.update(params)
            for name, value in params.items():
                setattr(self, name, value)  # Update individual param fields

    def update_results(self, metrics: Dict[str, Any]) -> None:
        """Records new tuning results/metrics.

        Args:
            metrics: Dictionary of metric names and values
        """
        self.results.update(metrics)

        # Update best parameters if improved
        if self.best_parameters is None or metrics.get(
            "score", 0
        ) > self.results.get("best_score", 0):
            self.best_parameters = self.parameters.copy()
            self.results["best_score"] = metrics.get("score", 0)

    def set_state(self, state: Union[TuningState, str]) -> None:
        """Updates the tuning state.

        Args:
            state: New state to set

        Raises:
            ValueError: If state is invalid or transition not allowed
        """
        try:
            if isinstance(state, str):
                state = TuningState(state)
            elif not isinstance(state, TuningState):
                raise ValueError(f"Invalid state type: {type(state)}")

            # Add validation logic here if needed
            # e.g., check if transition from current to new state is valid

            self.tuning_state = state
        except ValueError as e:
            raise ValueError(f"Invalid tuning state: {state}") from e

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters against constraints."""
        for param_name, value in params.items():
            constraints = self.parameter_constraints.get(param_name, {})
            if not constraints:
                continue

            param_type = constraints.get("type")
            if param_type and not isinstance(value, param_type):
                raise TypeError(
                    f"Parameter '{param_name}' must be of type {param_type.__name__}"
                )

            bounds = constraints.get("bounds", {})
            min_val = bounds.get("min")
            max_val = bounds.get("max")

            if min_val is not None and value < min_val:
                raise ValueError(
                    f"Parameter '{param_name}' below minimum value {min_val}"
                )
            if max_val is not None and value > max_val:
                raise ValueError(
                    f"Parameter '{param_name}' above maximum value {max_val}"
                )
        return True

    def get_best_result(self) -> Dict[str, Any]:
        """Get the example with the highest score."""
        if not self.examples:
            return None
        return max(self.examples, key=lambda x: x["score"])

    def reset(self) -> None:
        """Resets the form to initial state."""
        # Reset collections
        self.parameters = {}
        self.examples = []
        self.results = {}
        self.metaprompt_history = []

        # Reset state and best results
        self.best_parameters = None
        self.tuning_state = TuningState.INITIALIZED
        self.metaprompt = ""

        # Reset any parameter fields to undefined
        for field_name, field in self.__fields__.items():
            if field_name not in {
                "parameters",
                "examples",
                "results",
                "best_parameters",
                "tuning_state",
                "metaprompt",
            }:
                setattr(self, field_name, UNDEFINED)

    @property
    def best_params(self) -> Optional[Dict[str, Any]]:
        """Access the best parameters found during tuning."""
        return self.best_parameters

    @property
    def current_state(self) -> TuningState:
        """Access the current tuning state."""
        return self.tuning_state

    def set_metaprompt(self, metaprompt: str) -> None:
        """Set the metaprompt template."""
        self.metaprompt = metaprompt

    def format_metaprompt(self, template_vars: Dict[str, str]) -> str:
        """Format metaprompt with provided variables.

        Args:
            template_vars: Dictionary of variable names and values

        Returns:
            Formatted metaprompt string

        Raises:
            KeyError: If required template variables are missing
            ValueError: If metaprompt template is empty
        """
        if not self.metaprompt:
            raise ValueError("Metaprompt template is empty")

        try:
            return self.metaprompt.format(**template_vars)
        except KeyError as e:
            raise KeyError(f"Missing required template variable: {e.args[0]}")
        except ValueError as e:
            raise ValueError(f"Invalid template format: {e}")

    def add_metaprompt_result(self, prompt: str, score: float) -> None:
        """Add metaprompt optimization result."""
        self.metaprompt_history.append({"metaprompt": prompt, "score": score})

    def get_metaprompt_history(self) -> List[Dict[str, Any]]:
        """Get full metaprompt optimization history."""
        return self.metaprompt_history

    def get_best_metaprompt(self) -> Dict[str, Any]:
        """Get metaprompt with highest score."""
        if not self.metaprompt_history:
            return None
        return max(self.metaprompt_history, key=lambda x: x["score"])

    def evaluate_metaprompt(self, prompt: str, score: float) -> Dict[str, Any]:
        """Evaluate a single metaprompt's effectiveness."""
        result = {"prompt": prompt, "score": score}
        self.add_metaprompt_result(prompt, score)
        return result

    def get_metaprompt_effectiveness(self, prompt: str) -> float:
        """Get average effectiveness score for a metaprompt."""
        scores = [
            h["score"]
            for h in self.metaprompt_history
            if h["metaprompt"] == prompt
        ]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def meets_effectiveness_threshold(
        self, prompt: str, threshold: float
    ) -> bool:
        """Check if metaprompt meets effectiveness threshold."""
        return self.get_metaprompt_effectiveness(prompt) >= threshold

    def to_dict(self, **kwargs) -> dict:
        """Converts form to dictionary representation.

        Returns:
            Dictionary containing all form data
        """
        return {
            **super().to_dict(**kwargs),
            "parameters": to_dict(self.parameters),
            "parameter_constraints": to_dict(self.parameter_constraints),
            "examples": [to_dict(ex) for ex in self.examples],
            "tuning_state": self.tuning_state.value,
            "results": to_dict(self.results),
            "best_parameters": (
                to_dict(self.best_parameters) if self.best_parameters else None
            ),
        }
