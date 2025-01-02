"""Tests for the operative module."""

import pytest
from pydantic import BaseModel, Field

from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.models.model_params import ModelParams
from lionagi.operatives.operative import Operative


# Define test model outside test class to avoid pytest collection warning
class SampleModel(BaseModel):
    """Test model for operative testing."""

    name: str
    value: int


class TestOperative:
    def test_initialization(self):
        """Test basic initialization of Operative."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)
        assert operative.name == "SampleModel"
        assert operative.request_type is not None
        assert issubclass(operative.request_type, BaseModel)

    def test_custom_name(self):
        """Test Operative with custom name."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(name="CustomName", request_params=params)
        assert operative.name == "CustomName"

    def test_response_type_creation(self):
        """Test creation of response type."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Create response type with additional field
        field_models = [
            FieldModel(
                name="status",
                annotation=str,
                default="success",
                description="Status field",
            )
        ]
        operative.create_response_type(field_models=field_models)

        assert operative.response_type is not None
        assert "status" in operative.response_type.model_fields
        assert "name" in operative.response_type.model_fields
        assert "value" in operative.response_type.model_fields

    def test_response_model_update_with_text(self):
        """Test updating response model with text input."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Valid JSON text
        text = '{"name": "test", "value": 42}'
        result = operative.update_response_model(text=text)
        assert isinstance(result, BaseModel)
        assert result.name == "test"
        assert result.value == 42

        # Invalid JSON text
        operative = Operative(request_params=params)  # Fresh instance
        text = "invalid json"
        result = operative.update_response_model(text=text)
        assert isinstance(
            result, (str, dict, list)
        )  # Should return raw text, dict, or list for invalid JSON

    def test_response_model_update_with_data(self):
        """Test updating response model with dict data."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # First set initial model with valid JSON
        response_model = operative.update_response_model(
            text='{"name": "test", "value": 42}'
        )

        # Create response type to enable model updates
        operative.create_response_type()

        # Update with new data
        data = {"name": "updated"}
        result = operative.update_response_model(data=data)
        assert isinstance(result, BaseModel)
        assert result.name == "updated"
        assert result.value == 42  # Original value should be preserved

    def test_validation_methods(self):
        """Test strict and force validation methods."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Test strict validation
        valid_text = '{"name": "test", "value": 42}'
        operative.raise_validate_pydantic(valid_text)
        assert operative.response_model is not None
        assert operative.response_model.name == "test"
        assert operative.response_model.value == 42

        # Test force validation with extra fields
        text_with_extra = '{"name": "test", "value": 42, "extra": "field"}'
        operative.force_validate_pydantic(text_with_extra)
        assert operative.response_model is not None
        assert operative.response_model.name == "test"
        assert operative.response_model.value == 42

    def test_retry_behavior(self):
        """Test auto retry behavior for validation."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(
            request_params=params, auto_retry_parse=True, max_retries=3
        )

        # Invalid input should set retry flag
        invalid_text = '{"name": "test"}'  # Missing required field
        operative.raise_validate_pydantic(invalid_text)
        assert operative._should_retry is True

        # Valid input should clear retry flag
        valid_text = '{"name": "test", "value": 42}'
        operative.raise_validate_pydantic(valid_text)
        assert operative._should_retry is False

    def test_list_response_handling(self):
        """Test handling of list responses."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Test with list of valid items
        list_text = (
            '[{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]'
        )
        result = operative.update_response_model(text=list_text)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, BaseModel) for item in result)

    def test_error_cases(self):
        """Test error handling cases."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Test with no input
        with pytest.raises(ValueError):
            operative.update_response_model()

        # Test with invalid field types
        invalid_types = '{"name": 123, "value": "not an int"}'
        result = operative.update_response_model(text=invalid_types)
        assert isinstance(
            result, (str, dict, list)
        )  # Should return raw text, dict, or list for invalid types

    def test_exclude_fields(self):
        """Test excluding fields in response type."""

        # Create a new model type with only the name field
        class ReducedModel(BaseModel):
            name: str

        params = ModelParams(base_type=ReducedModel)
        operative = Operative(request_params=params)
        operative.create_response_type()

        assert "value" not in operative.response_type.model_fields
        assert "name" in operative.response_type.model_fields

    def test_field_descriptions(self):
        """Test field descriptions in response type."""
        params = ModelParams(base_type=SampleModel)
        operative = Operative(request_params=params)

        # Create new response type with field descriptions
        field_models = [
            FieldModel(
                name="name", annotation=str, description="Test name field"
            )
        ]
        operative.create_response_type(field_models=field_models)

        assert (
            operative.response_type.model_fields["name"].description
            == "Test name field"
        )
