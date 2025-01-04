"""Tests for the reason module."""

from lionagi.operatives.instruct.reason import (
    CONFIDENCE_SCORE_FIELD,
    REASON_FIELD,
    Reason,
    validate_confidence_score,
)
from lionagi.utils import UNDEFINED


class TestValidateConfidenceScore:
    def test_valid_numeric_inputs(self):
        """Test validation of valid numeric confidence scores."""
        test_cases = [
            (0.5, 0.5),  # Direct float
            (1, 1.0),  # Integer to float
            ("0.75", 0.75),  # String to float
            (0.8888, 0.889),  # Precision handling
            (0, 0.0),  # Lower bound
            (1, 1.0),  # Upper bound
        ]
        for input_val, expected in test_cases:
            assert validate_confidence_score(None, input_val) == expected

    def test_invalid_inputs(self):
        """Test validation of invalid confidence scores."""
        invalid_inputs = [
            "invalid",  # Non-numeric string
            None,  # None value
            {},  # Dict
            [],  # List
            -0.5,  # Below lower bound
            1.5,  # Above upper bound
        ]
        for input_val in invalid_inputs:
            assert validate_confidence_score(None, input_val) == -1

    def test_precision_handling(self):
        """Test that confidence scores are rounded to 3 decimal places."""
        test_cases = [
            (0.12345, 0.123),
            (0.9999, 1.0),
            (0.8888888, 0.889),
            (0.001001, 0.001),
        ]
        for input_val, expected in test_cases:
            assert validate_confidence_score(None, input_val) == expected


class TestReason:
    def test_default_values(self):
        """Test default values for Reason."""
        model = Reason()
        assert model.title is None
        assert model.content is None
        assert model.confidence_score is None

    def test_valid_values(self):
        """Test Reason with valid values."""
        data = {
            "title": "Test Reason",
            "content": "This is a test reason content",
            "confidence_score": 0.85,
        }
        model = Reason(**data)
        assert model.title == data["title"]
        assert model.content == data["content"]
        assert model.confidence_score == data["confidence_score"]

    def test_confidence_score_validation(self):
        """Test confidence score validation in Reason."""
        # Valid cases
        valid_scores = [0.5, 1.0, 0.0, "0.75"]
        for score in valid_scores:
            model = Reason(confidence_score=score)
            assert isinstance(model.confidence_score, float)
            assert 0 <= model.confidence_score <= 1

        # Invalid cases
        invalid_scores = [-1, 1.5, "invalid", None]
        for score in invalid_scores:
            if score is not None:  # None is allowed as it's the default
                model = Reason(confidence_score=score)
                assert model.confidence_score == -1

    def test_partial_initialization(self):
        """Test Reason with partial field initialization."""
        # Only title
        model = Reason(title="Test")
        assert model.title == "Test"
        assert model.content is None
        assert model.confidence_score is None

        # Only content
        model = Reason(content="Test content")
        assert model.title is None
        assert model.content == "Test content"
        assert model.confidence_score is None

        # Only confidence_score
        model = Reason(confidence_score=0.75)
        assert model.title is None
        assert model.content is None
        assert model.confidence_score == 0.75


class TestFieldModels:
    def test_confidence_score_field(self):
        """Test CONFIDENCE_SCORE_FIELD configuration."""
        assert CONFIDENCE_SCORE_FIELD.name == "confidence_score"
        assert CONFIDENCE_SCORE_FIELD.annotation == (float | None)
        assert CONFIDENCE_SCORE_FIELD.default is None
        assert CONFIDENCE_SCORE_FIELD.validator == validate_confidence_score
        assert CONFIDENCE_SCORE_FIELD.validator_kwargs == {"mode": "before"}

    def test_reason_field(self):
        """Test REASON_FIELD configuration."""
        assert REASON_FIELD.name == "reason"
        assert REASON_FIELD.annotation == Reason | None
        assert REASON_FIELD.default is UNDEFINED
        assert REASON_FIELD.title == "Reason"
