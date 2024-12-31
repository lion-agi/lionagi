import json
from datetime import datetime
from typing import Any

import pytest

from lionagi.protocols.action.tool import Tool


# Helper functions - not test cases
def example_func(x: int, y: str = "default") -> str:
    """Test function with docstring.

    Args:
        x: An integer parameter
        y: A string parameter with default

    Returns:
        A string result
    """
    return f"{x}-{y}"


def example_processor(data: dict) -> dict:
    """Test processor function."""
    return data


def example_parser(data: Any) -> str:
    """Test parser function."""
    return str(data)


# Actual test cases
def test_tool_initialization():
    """Test Tool class initialization"""
    tool = Tool(func_callable=example_func)
    assert callable(tool.func_callable)
    assert tool.func_callable == example_func
    assert tool.tool_schema is not None
    assert "function" in tool.tool_schema
    assert tool.tool_schema["function"]["name"] == "example_func"
    assert tool.preprocessor is None
    assert tool.postprocessor is None


def test_tool_with_processors():
    """Test Tool with pre/post processors"""
    tool = Tool(
        func_callable=example_func,
        preprocessor=example_processor,
        postprocessor=example_processor,
        preprocessor_kwargs={"key": "value"},
        postprocessor_kwargs={"key": "value"},
    )

    assert tool.preprocessor == example_processor
    assert tool.postprocessor == example_processor
    assert tool.preprocessor_kwargs == {"key": "value"}
    assert tool.postprocessor_kwargs == {"key": "value"}


def test_tool_validation():
    """Test Tool validation"""
    # Test non-callable function
    with pytest.raises(ValueError):
        Tool(func_callable="not_callable")

    # Test lambda function
    lambda_func = lambda x: x
    tool = Tool(func_callable=lambda_func)
    assert tool.func_callable.__name__ == "<lambda>"


def test_tool_serialization():
    """Test Tool serialization"""
    tool = Tool(
        func_callable=example_func,
        preprocessor=example_processor,
        postprocessor=example_processor,
        preprocessor_kwargs={"key": "value"},
        postprocessor_kwargs={"key": "value"},
    )

    serialized = tool.to_dict()
    assert serialized["func_callable"] == "example_func"
    assert serialized["preprocessor"] == "example_processor"
    assert serialized["postprocessor"] == "example_processor"
    assert json.loads(serialized["preprocessor_kwargs"]) == {"key": "value"}
    assert json.loads(serialized["postprocessor_kwargs"]) == {"key": "value"}


def test_tool_function_name():
    """Test Tool function_name property"""
    tool = Tool(func_callable=example_func)
    assert tool.function == "example_func"


def test_tool_str_representation():
    """Test Tool string representation"""
    tool = Tool(func_callable=example_func)
    str_rep = str(tool)
    assert "Tool" in str_rep
    assert "id" in str_rep
    assert "created_timestamp" in str_rep
    assert "tool_schema" in str_rep


def test_tool_schema_generation():
    """Test schema generation for Tool"""
    tool = Tool(func_callable=example_func)
    schema = tool.tool_schema

    assert "function" in schema
    assert "name" in schema["function"]
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]

    params = schema["function"]["parameters"]
    assert "properties" in params
    assert "x" in params["properties"]
    assert "y" in params["properties"]

    # Check parameter types
    assert (
        params["properties"]["x"]["type"] == "number"
    )  # int maps to number in JSON schema
    assert params["properties"]["y"]["type"] == "string"

    # Check required parameters - all parameters are required in OpenAI function format
    assert "required" in params
    assert "x" in params["required"]
    assert (
        "y" in params["required"]
    )  # Even parameters with defaults are marked as required
