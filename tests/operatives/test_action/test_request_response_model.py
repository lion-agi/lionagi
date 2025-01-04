import pytest
from pydantic import BaseModel

from lionagi.operatives.action.utils import (
    ACTION_REQUIRED_FIELD,
    ARGUMENTS_FIELD,
    FUNCTION_FIELD,
    parse_action_request,
    validate_arguments,
    validate_boolean_field,
    validate_function_name,
)

# Import the relevant parts from your code
# Make sure the import paths match your actual code layout
from lionagi.operatives.models.field_model import FieldModel
from lionagi.operatives.types import ActionRequestModel, ActionResponseModel

#######################################
#         Test Helper Classes         #
#######################################


class MockBaseModel(BaseModel):
    function: str
    arguments: dict


class AnotherMockBaseModel(BaseModel):
    data: str


#######################################
#       Tests for parse_action_request
#######################################


def test_parse_action_request_with_empty_string():
    """If an empty string is passed, parse_action_request should return an empty list."""
    result = parse_action_request("")
    assert result == [], "Expected empty list for empty string input."


def test_parse_action_request_with_valid_json_string():
    """
    If a valid JSON string with 'function' and 'arguments' is passed,
    it should parse and return a list of dicts.
    """
    content = '{"function": {"name": "foo"}, "arguments": {"x": 1, "y": 2}}'
    result = parse_action_request(content)
    assert len(result) == 1
    assert result[0]["function"] == "foo"
    assert result[0]["arguments"] == {"x": 1, "y": 2}


def test_parse_action_request_with_python_block():
    """
    If the string includes Python code blocks, parse_action_request should
    attempt to find them and parse them as JSON/dict.
    """
    content = """
    Here is some info:
    ```python
    {"function": {"name": "bar"}, "arguments": {"a": "hello"}}
    ```
    And some other text.
    """
    result = parse_action_request(content)
    assert len(result) == 1
    assert result[0]["function"] == "bar"
    assert result[0]["arguments"] == {"a": "hello"}


def test_parse_action_request_with_dict_input():
    """If a dict is passed, parse_action_request should wrap it in a list if valid."""
    content = {"function": {"name": "baz"}, "arguments": {"param": "value"}}
    result = parse_action_request(content)
    assert len(result) == 1
    assert result[0]["function"] == "baz"
    assert result[0]["arguments"] == {"param": "value"}


def test_parse_action_request_with_invalid_str():
    """
    If the string can't be parsed as JSON or found inside code blocks,
    the parser should return an empty list.
    """
    content = "just some random text"
    result = parse_action_request(content)
    assert result == [], "Expected empty list for un-parseable string input."


def test_parse_action_request_with_basemodel():
    """
    If a BaseModel is passed, parse_action_request should convert it via model_dump()
    and return it in a list if it has 'function' and 'arguments'.
    """
    mock_model = MockBaseModel(function="my_func", arguments={"key": "val"})
    result = parse_action_request(mock_model)
    assert len(result) == 1
    assert result[0]["function"] == "my_func"
    assert result[0]["arguments"] == {"key": "val"}


def test_parse_action_request_ignores_irrelevant_keys():
    """
    If the dictionary has different field names, parse_action_request should
    try to map them to 'function' or 'arguments' if possible.
    Otherwise, it returns empty or partial results.
    """
    content = {
        "action_name": "test_func",
        "param": {"x": 1},
    }
    # 'action_name' -> 'function'; 'param' -> 'arguments'
    result = parse_action_request(content)
    assert len(result) == 1
    assert result[0]["function"] == "test_func"
    assert result[0]["arguments"] == {"x": 1}


#######################################
#       Tests for Validators
#######################################


def test_validate_function_name():
    """Test that validate_function_name returns None if not a string, else the string."""
    assert validate_function_name(None, 123) is None
    assert validate_function_name(None, "func_name") == "func_name"


def test_validate_arguments():
    """Test that validate_arguments attempts to parse the value into a dict."""
    # Valid dict
    d = {"x": 1, "y": 2}
    assert validate_arguments(None, d) == d

    # JSON string
    json_str = '{"a": 10}'
    assert validate_arguments(None, json_str) == {"a": 10}

    # Invalid string
    invalid_str = "not valid json"
    assert validate_arguments(None, invalid_str) == {}


def test_validate_boolean_field():
    """Test that validate_boolean_field returns a boolean, with default=False on error."""
    # True-like values
    for val in [True, "true", "on", 1]:
        assert validate_boolean_field(None, val, False) is True

    # False-like values
    for val in [False, "false", "off", 0]:
        assert validate_boolean_field(None, val, False) is False

    # Garbage input
    assert validate_boolean_field(None, "??", False) is False


#######################################
#     Tests for ActionRequestModel
#######################################


def test_action_request_model_init():
    """Basic test for direct initialization."""
    model = ActionRequestModel(function="foo", arguments={"bar": "baz"})
    assert model.function == "foo"
    assert model.arguments == {"bar": "baz"}


def test_action_request_model_validator_arguments():
    """Check that the arguments validator transforms a JSON string into a dict."""
    model = ActionRequestModel(function="foo", arguments='{"x": 1}')
    assert model.arguments == {"x": 1}


def test_action_request_model_validator_function():
    """Check that the function validator returns None if input is not a string."""
    model = ActionRequestModel(function=123, arguments={})
    # Should end up as None because 123 is not a string
    assert model.function is None


def test_action_request_model_create_single():
    """
    The create method should parse a single valid JSON string
    into a list containing one ActionRequestModel.
    """
    content = '{"function": {"name": "my_func"}, "arguments": {"foo": 42}}'
    result = ActionRequestModel.create(content)
    assert len(result) == 1
    instance = result[0]
    assert isinstance(instance, ActionRequestModel)
    assert instance.function == "my_func"
    assert instance.arguments == {"foo": 42}


def test_action_request_model_create_multiple():
    """
    If the string has multiple code blocks or JSON objects,
    create should parse them all.
    """
    content = """
    ```python
    {"function": {"name": "f1"}, "arguments": {"a": 1}}
    ```
    ```python
    {"function": {"name": "f2"}, "arguments": {"b": 2}}
    ```
    """
    result = ActionRequestModel.create(content)
    assert len(result) == 2
    assert result[0].function == "f1"
    assert result[0].arguments == {"a": 1}
    assert result[1].function == "f2"
    assert result[1].arguments == {"b": 2}


def test_action_request_model_create_invalid():
    """
    If the input is not parseable or does not yield any valid function/arguments,
    create should return an empty list.
    """
    content = "just random text"
    result = ActionRequestModel.create(content)
    assert result == []


#######################################
#     Additional FieldModel Tests
#######################################


def test_function_field_model():
    """Sanity check that FUNCTION_FIELD is a FieldModel with the correct name."""
    assert FUNCTION_FIELD.name == "function"
    assert "Name of the function" in FUNCTION_FIELD.description


def test_arguments_field_model():
    """Sanity check that ARGUMENTS_FIELD is a FieldModel with the correct name."""
    assert ARGUMENTS_FIELD.name == "arguments"
    assert "Dictionary of arguments" in ARGUMENTS_FIELD.description


def test_action_required_field_model():
    """Sanity check that ACTION_REQUIRED_FIELD is a FieldModel with the correct name."""
    assert ACTION_REQUIRED_FIELD.name == "action_required"
    assert (
        "Whether this step strictly requires performing actions"
        in ACTION_REQUIRED_FIELD.description
    )


#######################################
#   Test ActionResponseModel (basic)
#######################################


def test_action_response_model_init():
    """Basic initialization test for ActionResponseModel."""
    resp = ActionResponseModel(
        function="my_function",
        arguments={"key": "value"},
        output="some output",
    )
    assert resp.function == "my_function"
    assert resp.arguments == {"key": "value"}
    assert resp.output == "some output"
