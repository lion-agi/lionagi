"""Tests for the step module."""

import pytest
from pydantic import BaseModel

from lionagi.operatives.action.request_response_model import (
    ACTION_REQUESTS_FIELD,
    ACTION_RESPONSES_FIELD,
    ActionRequestModel,
    ActionResponseModel,
)
from lionagi.operatives.action.utils import ACTION_REQUIRED_FIELD
from lionagi.operatives.instruct.reason import Reason
from lionagi.operatives.step import Step, StepModel
from lionagi.operatives.types import ModelParams


class SampleModel(BaseModel):
    """Sample model for testing."""

    name: str
    value: int


class TestStepModel:
    def test_basic_step(self):
        """Test basic StepModel initialization."""
        step = StepModel(
            title="Test Step",
            description="Test step description",
            reason=None,
            action_requests=[],
            action_required=False,
            action_responses=[],
        )
        assert step.title == "Test Step"
        assert step.description == "Test step description"
        assert step.reason is None
        assert step.action_requests == []
        assert step.action_required is False
        assert step.action_responses == []

    def test_step_with_reason(self):
        """Test StepModel with reason."""
        reason = Reason(
            title="Test Reason",
            content="Test reason content",
            confidence_score=0.85,
        )
        step = StepModel(
            title="Test Step",
            description="Test step description",
            reason=reason,
            action_requests=[],
            action_required=False,
            action_responses=[],
        )
        assert step.reason == reason
        assert step.reason.title == "Test Reason"
        assert step.reason.confidence_score == 0.85

    def test_step_with_actions(self):
        """Test StepModel with actions."""
        action_request = ActionRequestModel(
            function="test_function", arguments={"arg": "value"}
        )
        action_response = ActionResponseModel(
            function="test_function",
            arguments={"arg": "value"},
            output="test output",
        )
        step = StepModel(
            title="Test Step",
            description="Test step description",
            reason=None,
            action_requests=[action_request],
            action_required=True,
            action_responses=[action_response],
        )
        assert len(step.action_requests) == 1
        assert step.action_required is True
        assert len(step.action_responses) == 1
        assert step.action_requests[0].function == "test_function"
        assert step.action_responses[0].output == "test output"


class TestStep:
    def test_request_operative_basic(self):
        """Test basic request operative creation."""
        operative = Step.request_operative(
            operative_name="test_operative", base_type=SampleModel
        )
        assert operative.name == "test_operative"
        assert operative.request_type is not None
        assert issubclass(operative.request_type, BaseModel)

    def test_request_operative_with_reason(self):
        """Test request operative with reason field."""
        operative = Step.request_operative(
            operative_name="test_operative", reason=True, base_type=SampleModel
        )
        assert "reason" in operative.request_type.model_fields
        assert (
            operative.request_type.model_fields["reason"].annotation
            == Reason | None
        )

    def test_request_operative_with_actions(self):
        """Test request operative with action fields."""
        operative = Step.request_operative(
            operative_name="test_operative",
            actions=True,
            base_type=SampleModel,
        )
        assert "action_requests" in operative.request_type.model_fields
        assert "action_required" in operative.request_type.model_fields

    def test_respond_operative_basic(self):
        """Test basic respond operative creation."""
        request_operative = Step.request_operative(
            operative_name="test_operative", base_type=SampleModel
        )

        # Create initial response
        request_operative.update_response_model(
            text='{"name": "test", "value": 42}'
        )

        # Update with response operative
        response_operative = Step.respond_operative(
            operative=request_operative
        )

        assert response_operative.response_type is not None
        assert response_operative.response_model is not None
        assert response_operative.response_model.name == "test"
        assert response_operative.response_model.value == 42

    def test_respond_operative_with_additional_data(self):
        """Test respond operative with additional data."""
        request_operative = Step.request_operative(
            operative_name="test_operative", base_type=SampleModel
        )

        # Create initial response
        request_operative.update_response_model(
            text='{"name": "test", "value": 42}'
        )

        # Update with additional data
        additional_data = {"name": "updated"}
        response_operative = Step.respond_operative(
            operative=request_operative, additional_data=additional_data
        )

        assert response_operative.response_model.name == "updated"
        assert response_operative.response_model.value == 42

    def test_respond_operative_with_actions(self):
        """Test respond operative with action fields."""
        # Create request operative with actions enabled
        request_operative = Step.request_operative(
            operative_name="test_operative",
            actions=True,
            base_type=SampleModel,
        )

        # Create initial response with actions
        request_operative.update_response_model(
            text="""{
                "name": "test",
                "value": 42,
                "action_required": true,
                "action_requests": [
                    {
                        "function": "test_function",
                        "arguments": {"arg": "value"}
                    }
                ]
            }"""
        )

        # Create response type with action fields
        response_params = ModelParams(
            base_type=SampleModel,
            field_models=[
                ACTION_RESPONSES_FIELD,
                ACTION_REQUIRED_FIELD,
                ACTION_REQUESTS_FIELD,
            ],
        )

        # Update with response operative
        response_operative = Step.respond_operative(
            operative=request_operative, response_params=response_params
        )

        # Verify action fields are present in response type
        assert (
            "action_responses" in response_operative.response_type.model_fields
        )
        assert (
            "action_required" in response_operative.response_type.model_fields
        )
        assert (
            "action_requests" in response_operative.response_type.model_fields
        )

    def test_error_cases(self):
        """Test error handling in Step methods."""
        # Test with invalid base type
        with pytest.raises(Exception):
            Step.request_operative(base_type="not a model")

        # Test respond without request
        with pytest.raises(Exception):
            Step.respond_operative(operative=None)

        # Test with invalid additional data
        request_operative = Step.request_operative(
            operative_name="test_operative", base_type=SampleModel
        )
        with pytest.raises(Exception):
            Step.respond_operative(
                operative=request_operative, additional_data="not a dict"
            )
