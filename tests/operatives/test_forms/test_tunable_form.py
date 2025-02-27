import pytest
from pydantic import Field

from lionagi.operatives.forms.tunable_form import TunableForm, TuningState
from lionagi.utils import UNDEFINED


class SimpleTunableForm(TunableForm):
    """A simple tunable form for testing."""

    param1: float = Field(default=UNDEFINED)
    param2: int = Field(default=UNDEFINED)
    result: float = Field(default=UNDEFINED)

    class Config:
        param_constraints = {
            "param1": {"min": 0.0, "max": 1.0},
            "param2": {"min": 1, "max": 10},
        }


@pytest.fixture
def form():
    """Fixture providing a clean SimpleTunableForm instance."""
    return SimpleTunableForm(assignment="param1, param2 -> result")


def test_initialization(form):
    """Test basic initialization of TunableForm."""
    assert form.assignment == "param1, param2 -> result"
    assert form.best_params is None
    assert form.examples == []
    assert form.current_state == TuningState.INITIALIZED
    assert form.param1 is UNDEFINED
    assert form.param2 is UNDEFINED
    assert form.result is UNDEFINED


def test_parameter_constraints(form):
    """Test parameter constraints validation."""
    # Test direct validate_params call
    params = {"param1": 0.5, "param2": 5}
    assert form.validate_params(params)

    # Test invalid parameters
    with pytest.raises(
        ValueError, match="Parameter 'param1' must be between 0.0 and 1.0"
    ):
        form.validate_params({"param1": 1.5, "param2": 5})

    with pytest.raises(
        ValueError, match="Parameter 'param2' must be between 1 and 10"
    ):
        form.validate_params({"param1": 0.5, "param2": 0})

    # Test boundary values
    assert form.validate_params(
        {"param1": 0.0, "param2": 10}
    )  # Min/Max values
    assert form.validate_params({"param1": 1.0, "param2": 1})  # Max/Min values

    # Test parameter setting
    form.set_parameters(params)
    assert form.param1 == 0.5
    assert form.param2 == 5


def test_example_management(form):
    """Test example addition and management."""
    # Test valid example addition
    example = {"parameters": {"param1": 0.5, "param2": 5}, "score": 2.5}
    form.add_example(example)
    assert len(form.examples) == 1
    assert form.examples[0] == example

    # Test type validation
    with pytest.raises(TypeError, match="Example must be a dictionary"):
        form.add_example([])

    # Test empty example handling
    with pytest.raises(
        ValueError, match="Example must contain 'parameters' and 'score'"
    ):
        form.add_example({})

    # Test missing fields
    with pytest.raises(
        ValueError, match="Example must contain 'parameters' and 'score'"
    ):
        form.add_example({"parameters": {"param1": 0.5}})

    # Test invalid structure
    with pytest.raises(
        ValueError, match="Example must contain 'parameters' and 'score'"
    ):
        form.add_example({"param1": 0.5, "score": 2.5})


def test_state_transitions(form):
    """Test state transitions and validation."""
    # Test initial state
    assert form.current_state == TuningState.INITIALIZED

    # Test manual state setting
    form.set_state(TuningState.IN_PROGRESS)
    assert form.current_state == TuningState.IN_PROGRESS

    # Test transition after adding example
    example = {"parameters": {"param1": 0.5, "param2": 5}, "score": 2.5}
    form.add_example(example)
    assert form.current_state == TuningState.IN_PROGRESS

    # Test completion
    form.set_state(TuningState.COMPLETED)
    assert form.current_state == TuningState.COMPLETED

    # Test invalid state transition
    with pytest.raises(ValueError, match="Invalid state transition"):
        form.set_state("INVALID_STATE")


def test_results_tracking(form):
    """Test results tracking and scoring."""
    results = [
        {"parameters": {"param1": 0.1, "param2": 3}, "score": 1.0},
        {"parameters": {"param1": 0.2, "param2": 4}, "score": 2.0},
        {"parameters": {"param1": 0.3, "param2": 5}, "score": 3.0},
    ]

    # Test progressive addition of results
    for i, result in enumerate(results, 1):
        form.add_example(result)
        assert len(form.examples) == i
        best_result = form.get_best_result()
        assert best_result["score"] == result["score"]
        assert best_result["parameters"] == result["parameters"]

    # Test best result tracking
    best_result = form.get_best_result()
    assert best_result["score"] == 3.0
    assert best_result["parameters"] == {"param1": 0.3, "param2": 5}

    # Test no results case
    form.reset()
    assert form.get_best_result() is None


def test_form_reset(form):
    """Test form reset functionality."""
    # Setup form with data
    example = {"parameters": {"param1": 0.5, "param2": 5}, "score": 2.5}
    form.add_example(example)
    form.set_parameters({"param1": 0.6, "param2": 6})
    form.set_state(TuningState.IN_PROGRESS)

    # Verify pre-reset state
    assert form.current_state == TuningState.IN_PROGRESS
    assert len(form.examples) == 1
    assert form.param1 == 0.6
    assert form.param2 == 6

    # Test reset
    form.reset()

    # Verify post-reset state
    assert form.current_state == TuningState.INITIALIZED
    assert len(form.examples) == 0
    assert form.param1 is UNDEFINED
    assert form.param2 is UNDEFINED
    assert form.best_params is None
    assert form.get_best_result() is None


def test_metaprompt_specification(form):
    """Test metaprompt specification and validation."""
    # Test setting/getting basic metaprompt
    metaprompt = "Convert {input} to {output} format"
    form.set_metaprompt(metaprompt)
    assert form.metaprompt == metaprompt

    # Test template substitution
    form.set_parameters({"param1": 0.5, "param2": 5})
    formatted = form.format_metaprompt({"input": "JSON", "output": "XML"})
    assert formatted == "Convert JSON to XML format"

    # Test empty metaprompt
    form.set_metaprompt("")
    assert form.metaprompt == ""

    # Test invalid template variables
    with pytest.raises(KeyError):
        form.format_metaprompt({"invalid": "value"})


def test_metaprompt_optimization(form):
    """Test metaprompt optimization tracking."""
    # Setup test data
    metaprompts = [
        "Convert input to output version {param1}",
        "Transform data using parameter {param2}",
    ]
    scores = [0.8, 0.9]

    # Add optimization results
    for prompt, score in zip(metaprompts, scores):
        form.add_metaprompt_result(prompt, score)

    # Check optimization history
    history = form.get_metaprompt_history()
    assert len(history) == 2
    assert all(h["metaprompt"] in metaprompts for h in history)
    assert all(h["score"] in scores for h in history)

    # Verify best metaprompt selection
    best = form.get_best_metaprompt()
    assert best["metaprompt"] == metaprompts[1]
    assert best["score"] == 0.9


def test_metaprompt_effectiveness(form):
    """Test metaprompt effectiveness scoring."""
    # Setup test prompts with different effectiveness scores
    test_data = [
        {"prompt": "Basic conversion", "scores": [0.5, 0.6, 0.7]},
        {"prompt": "Enhanced processing", "scores": [0.8, 0.9, 0.7]},
    ]

    # Test effectiveness calculation
    for data in test_data:
        scores = []
        for score in data["scores"]:
            result = form.evaluate_metaprompt(data["prompt"], score)
            scores.append(result["score"])

        # Verify average calculation
        assert len(scores) == len(data["scores"])
        avg = sum(scores) / len(scores)
        stored_avg = form.get_metaprompt_effectiveness(data["prompt"])
        assert abs(stored_avg - avg) < 0.0001  # Account for float precision

    # Verify effectiveness thresholds
    assert form.meets_effectiveness_threshold(
        "Enhanced processing", threshold=0.7
    )
    assert not form.meets_effectiveness_threshold(
        "Basic conversion", threshold=0.7
    )
