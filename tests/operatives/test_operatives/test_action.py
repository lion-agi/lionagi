import pytest
from pydantic import BaseModel

from lionagi.protocols.action.request_response_model import (
    ActionRequestModel,
    ActionResponseModel,
    parse_action_request,
)


class TestActionRequestModel:
    def test_valid_function_name(self):
        """Test validation of valid function names."""
        model = ActionRequestModel(
            function="test_function", arguments={"arg": 1}
        )
        assert model.function == "test_function"
        assert model.arguments == {"arg": 1}

    def test_none_function_name(self):
        """Test that None is accepted as function name."""
        model = ActionRequestModel(function=None, arguments={})
        assert model.function is None

    def test_invalid_function_name(self):
        """Test that non-string function names raise validation error."""
        with pytest.raises(Exception):
            ActionRequestModel(function=123, arguments={})

    def test_arguments_validation(self):
        """Test arguments field validation with various inputs."""
        test_cases = [
            ({"x": 1, "y": 2}, {"x": 1, "y": 2}),  # Direct dict
            (None, {}),  # None becomes empty dict
        ]

        for input_val, expected in test_cases:
            model = ActionRequestModel(function="test", arguments=input_val)
            assert model.arguments == expected

    def test_create_from_json_string(self):
        """Test create method with JSON string input."""
        json_str = '{"function": "test", "arguments": {"x": 1}}'  # Fixed JSON format with comma
        models = ActionRequestModel.create(json_str)
        assert len(models) == 1
        assert models[0].function == "test"
        assert models[0].arguments == {"x": 1}

    def test_create_from_python_block(self):
        """Test create method with Python code block string."""
        python_str = """```python
{
    "function": "test",
    "arguments": {"x": 1}
}
```"""
        models = ActionRequestModel.create(python_str)
        assert len(models) == 1
        assert models[0].function == "test"
        assert models[0].arguments == {"x": 1}

    def test_create_from_dict(self):
        """Test create method with dictionary input."""
        data = {"function": "test", "arguments": {"x": 1}}
        models = ActionRequestModel.create(data)
        assert len(models) == 1
        assert models[0].function == "test"
        assert models[0].arguments == {"x": 1}

    def test_create_from_base_model(self):
        """Test create method with BaseModel input."""

        class TestModel(BaseModel):
            function: str
            arguments: dict

        model_input = TestModel(function="test", arguments={"x": 1})
        models = ActionRequestModel.create(model_input)
        assert len(models) == 1
        assert models[0].function == "test"
        assert models[0].arguments == {"x": 1}

    def test_create_with_invalid_input(self):
        """Test create method with invalid inputs returns empty list."""
        invalid_inputs = [
            "",  # Empty string
            "invalid json",  # Invalid JSON
            123,  # Number
            None,  # None
            [],  # Empty list
            {},  # Empty dict
        ]
        for input_val in invalid_inputs:
            models = ActionRequestModel.create(input_val)
            assert models == []


class TestActionResponseModel:
    def test_default_values(self):
        """Test default values for ActionResponseModel."""
        model = ActionResponseModel()
        assert model.function == ""
        assert model.arguments == {}
        assert model.output is None

    def test_custom_values(self):
        """Test ActionResponseModel with custom values."""
        model = ActionResponseModel(
            function="test", arguments={"x": 1}, output="result"
        )
        assert model.function == "test"
        assert model.arguments == {"x": 1}
        assert model.output == "result"


class TestParseActionRequest:
    def test_parse_dict_input(self):
        """Test parsing dictionary input."""
        input_dict = {"function": "test", "arguments": {"x": 1}}
        result = parse_action_request(input_dict)
        assert len(result) == 1
        assert result[0]["function"] == "test"
        assert result[0]["arguments"] == {"x": 1}

    def test_parse_json_string(self):
        """Test parsing JSON string input."""
        json_str = '{"function": "test", "arguments": {"x": 1}}'  # Fixed JSON format with comma
        result = parse_action_request(json_str)
        assert len(result) == 1
        assert result[0]["function"] == "test"
        assert result[0]["arguments"] == {"x": 1}

    def test_parse_python_block(self):
        """Test parsing Python code block string."""
        python_str = """```python
{
    "function": "test",
    "arguments": {"x": 1}
}
```"""
        result = parse_action_request(python_str)
        assert len(result) == 1
        assert result[0]["function"] == "test"
        assert result[0]["arguments"] == {"x": 1}

    def test_parse_base_model(self):
        """Test parsing BaseModel input."""

        class TestModel(BaseModel):
            function: str
            arguments: dict

        model = TestModel(function="test", arguments={"x": 1})
        result = parse_action_request(model)
        assert len(result) == 1
        assert result[0]["function"] == "test"
        assert result[0]["arguments"] == {"x": 1}

    def test_parse_invalid_input(self):
        """Test parsing invalid inputs returns empty list."""
        invalid_inputs = [
            "",  # Empty string
            "invalid json",  # Invalid JSON string
            123,  # Number
            None,  # None
            [],  # Empty list
            {},  # Empty dict
        ]
        for input_val in invalid_inputs:
            result = parse_action_request(input_val)
            assert result == []

    def test_parse_alternative_key_names(self):
        """Test parsing with alternative key names."""
        test_cases = [
            {"action_name": "test", "parameters": {"x": 1}},
            {"recipient_name": "test", "args": {"x": 1}},
            {"name": "test", "parameter": {"x": 1}},
        ]
        for test_case in test_cases:
            result = parse_action_request(test_case)
            assert len(result) == 1
            assert result[0]["function"] == "test"
            assert result[0]["arguments"] == {"x": 1}

    def test_parse_nested_function(self):
        """Test parsing nested function structure."""
        nested_input = {"function": {"name": "test", "parameters": {"x": 1}}}
        result = parse_action_request(nested_input)
        assert len(result) == 1
        assert result[0]["function"] == "test"
        assert result[0]["arguments"] == {"x": 1}
