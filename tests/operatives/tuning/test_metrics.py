from typing import Any, Dict

import numpy as np
import pytest
from pydantic import Field

from lionagi.operatives.forms.tunable_form import TunableForm
from lionagi.utils import UNDEFINED


class MetricsTestForm(TunableForm):
    """Test form class for metrics evaluation."""

    accuracy_weight: float = Field(default=0.5)
    format_weight: float = Field(default=0.3)
    semantic_weight: float = Field(default=0.2)
    result: dict[str, Any] = Field(default=UNDEFINED)

    class Config:
        param_constraints = {
            "accuracy_weight": {"min": 0.0, "max": 1.0},
            "format_weight": {"min": 0.0, "max": 1.0},
            "semantic_weight": {"min": 0.0, "max": 1.0},
        }


@pytest.fixture
def metrics_form():
    """Fixture providing a clean MetricsTestForm instance."""
    return MetricsTestForm(
        assignment="accuracy_weight, format_weight, semantic_weight -> result"
    )


@pytest.fixture
def sample_responses():
    """Fixture providing sample response data for testing."""
    return {
        "perfect": {
            "content": "Valid response in correct format",
            "structure": {"field1": "value1", "field2": "value2"},
            "metadata": {"timestamp": "2024-01-01"},
        },
        "partial": {
            "content": "Partially valid response",
            "structure": {"field1": "value1"},
            "metadata": {},
        },
        "invalid": {
            "content": "Invalid response",
            "structure": {},
            "metadata": None,
        },
    }


@pytest.fixture
def evaluation_config():
    """Fixture providing evaluation configuration."""
    return {
        "accuracy_threshold": 0.8,
        "format_rules": ["json_valid", "schema_complete"],
        "semantic_criteria": ["relevance", "coherence"],
        "scoring_weights": {"accuracy": 0.5, "format": 0.3, "semantic": 0.2},
    }


class TestResponseEvaluation:
    """Test suite for response evaluation metrics."""

    def test_correctness_evaluation(self, metrics_form, sample_responses):
        """Test basic correctness evaluation."""
        perfect_score = metrics_form.evaluate_response(
            sample_responses["perfect"]
        )
        partial_score = metrics_form.evaluate_response(
            sample_responses["partial"]
        )
        invalid_score = metrics_form.evaluate_response(
            sample_responses["invalid"]
        )

        assert perfect_score > partial_score > invalid_score
        assert 0.8 <= perfect_score <= 1.0
        assert 0.3 <= partial_score <= 0.7
        assert 0.0 <= invalid_score <= 0.3

    def test_semantic_matching(self, metrics_form, sample_responses):
        """Test semantic similarity scoring."""
        reference = "Valid response in correct format"

        perfect_match = metrics_form.compute_semantic_similarity(
            sample_responses["perfect"]["content"], reference
        )
        partial_match = metrics_form.compute_semantic_similarity(
            sample_responses["partial"]["content"], reference
        )

        assert perfect_match > partial_match
        assert 0.0 <= partial_match <= perfect_match <= 1.0

    def test_structural_validation(self, metrics_form, sample_responses):
        """Test structural validation of responses."""
        required_fields = {"field1", "field2"}

        perfect_valid = metrics_form.validate_structure(
            sample_responses["perfect"]["structure"], required_fields
        )
        partial_valid = metrics_form.validate_structure(
            sample_responses["partial"]["structure"], required_fields
        )

        assert perfect_valid
        assert not partial_valid

    def test_scoring_consistency(self, metrics_form, sample_responses):
        """Test consistency of scoring across multiple evaluations."""
        scores = []
        for _ in range(5):
            score = metrics_form.evaluate_response(sample_responses["perfect"])
            scores.append(score)

        assert max(scores) - min(scores) < 0.1  # Check score stability


class TestFormatCompliance:
    """Test suite for format compliance metrics."""

    def test_format_validation(self, metrics_form, sample_responses):
        """Test format validation rules."""
        valid = metrics_form.validate_format(sample_responses["perfect"])
        partial = metrics_form.validate_format(sample_responses["partial"])
        invalid = metrics_form.validate_format(sample_responses["invalid"])

        assert valid
        assert partial
        assert not invalid

    def test_schema_compliance(self, metrics_form, sample_responses):
        """Test schema compliance checking."""
        schema = {
            "type": "object",
            "required": ["content", "structure", "metadata"],
        }

        assert metrics_form.validate_schema(
            sample_responses["perfect"], schema
        )
        assert not metrics_form.validate_schema(
            sample_responses["invalid"], schema
        )

    def test_custom_format_handlers(self, metrics_form):
        """Test custom format validation handlers."""
        custom_format = {"type": "custom", "data": {"key": "value"}}

        handler_result = metrics_form.handle_custom_format(custom_format)
        assert isinstance(handler_result, dict)
        assert "validation_result" in handler_result

    def test_error_detection(self, metrics_form, sample_responses):
        """Test error detection in responses."""
        errors = metrics_form.detect_errors(sample_responses["invalid"])
        assert len(errors) > 0
        assert all(isinstance(error, dict) for error in errors)


class TestExampleValidation:
    """Test suite for example validation metrics."""

    def test_example_verification(self, metrics_form):
        """Test example verification process."""
        valid_example = {
            "parameters": {
                "accuracy_weight": 0.5,
                "format_weight": 0.3,
                "semantic_weight": 0.2,
            },
            "score": 0.85,
        }

        assert metrics_form.verify_example(valid_example)

        invalid_example = {"parameters": {}, "score": -1}

        assert not metrics_form.verify_example(invalid_example)

    def test_consistency_checks(self, metrics_form):
        """Test consistency between examples."""
        examples = [
            {"parameters": {"accuracy_weight": 0.5}, "score": 0.8},
            {"parameters": {"accuracy_weight": 0.6}, "score": 0.85},
            {"parameters": {"accuracy_weight": 0.4}, "score": 0.75},
        ]

        consistency_score = metrics_form.check_example_consistency(examples)
        assert 0.0 <= consistency_score <= 1.0

    def test_coverage_analysis(self, metrics_form):
        """Test parameter space coverage analysis."""
        examples = [
            {"parameters": {"accuracy_weight": 0.1}, "score": 0.7},
            {"parameters": {"accuracy_weight": 0.5}, "score": 0.8},
            {"parameters": {"accuracy_weight": 0.9}, "score": 0.9},
        ]

        coverage = metrics_form.analyze_parameter_coverage(examples)
        assert isinstance(coverage, dict)
        assert "coverage_score" in coverage
        assert "gaps" in coverage

    def test_example_scoring(self, metrics_form):
        """Test example scoring mechanisms."""
        example = {
            "parameters": {
                "accuracy_weight": 0.5,
                "format_weight": 0.3,
                "semantic_weight": 0.2,
            },
            "response": "Test response",
            "expected": "Expected response",
        }

        score = metrics_form.score_example(example)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestMetricAggregation:
    """Test suite for metric aggregation methods."""

    def test_metric_aggregation(self, metrics_form):
        """Test basic metric aggregation."""
        metrics = [
            {"accuracy": 0.8, "format": 0.9, "semantic": 0.7},
            {"accuracy": 0.7, "format": 0.8, "semantic": 0.8},
            {"accuracy": 0.9, "format": 0.7, "semantic": 0.9},
        ]

        aggregated = metrics_form.aggregate_metrics(metrics)
        assert isinstance(aggregated, dict)
        assert all(0.0 <= v <= 1.0 for v in aggregated.values())

    def test_weighting_schemes(self, metrics_form):
        """Test different weighting schemes."""
        scores = {"accuracy": 0.8, "format": 0.7, "semantic": 0.9}

        weighted_score = metrics_form.apply_weights(scores)
        assert isinstance(weighted_score, float)
        assert 0.0 <= weighted_score <= 1.0

    def test_threshold_handling(self, metrics_form):
        """Test threshold-based metric handling."""
        metrics = [0.7, 0.8, 0.9, 0.6]
        threshold = 0.75

        above_threshold = metrics_form.filter_by_threshold(metrics, threshold)
        assert all(m >= threshold for m in above_threshold)

    def test_summary_statistics(self, metrics_form):
        """Test statistical summaries of metrics."""
        metrics = [0.7, 0.8, 0.9, 0.6, 0.75]

        stats = metrics_form.compute_statistics(metrics)
        assert isinstance(stats, dict)
        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
