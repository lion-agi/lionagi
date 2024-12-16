import json
from datetime import datetime
from typing import Any

import pytest

from lionagi.core.action.tool import Tool, func_to_tool


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
    tool = Tool(function=example_func)
    assert callable(tool.function)
    assert tool.function == example_func
    assert tool.schema_ is not None
    assert "function" in tool.schema_
    assert tool.schema_["function"]["name"] == "example_func"
    assert tool.pre_processor is None
    assert tool.post_processor is None
    assert tool.parser is None


def test_tool_with_processors():
    """Test Tool with pre/post processors"""
    tool = Tool(
        function=example_func,
        pre_processor=example_processor,
        post_processor=example_processor,
        parser=example_parser,
        pre_processor_kwargs={"key": "value"},
        post_processor_kwargs={"key": "value"},
    )

    assert tool.pre_processor == example_processor
    assert tool.post_processor == example_processor
    assert tool.parser == example_parser
    assert tool.pre_processor_kwargs == {"key": "value"}
    assert tool.post_processor_kwargs == {"key": "value"}


def test_tool_validation():
    """Test Tool validation"""
    # Test non-callable function
    with pytest.raises(ValueError):
        Tool(function="not_callable")

    # Test lambda function
    lambda_func = lambda x: x
    tool = Tool(function=lambda_func)
    assert tool.function.__name__ == "<lambda>"


def test_tool_serialization():
    """Test Tool serialization"""
    tool = Tool(
        function=example_func,
        pre_processor=example_processor,
        post_processor=example_processor,
        parser=example_parser,
        pre_processor_kwargs={"key": "value"},
        post_processor_kwargs={"key": "value"},
    )

    serialized = tool.to_dict()
    assert serialized["function"] == "example_func"
    assert serialized["pre_processor"] == "example_processor"
    assert serialized["post_processor"] == "example_processor"
    assert serialized["parser"] == "example_parser"
    assert json.loads(serialized["pre_processor_kwargs"]) == {"key": "value"}
    assert json.loads(serialized["post_processor_kwargs"]) == {"key": "value"}


def test_tool_function_name():
    """Test Tool function_name property"""
    tool = Tool(function=example_func)
    assert tool.function_name == "example_func"


def test_tool_str_representation():
    """Test Tool string representation"""
    tool = Tool(function=example_func)
    str_rep = str(tool)
    assert "Tool" in str_rep
    assert "ln_id" in str_rep
    assert "created_timestamp" in str_rep
    assert "schema_" in str_rep


def test_func_to_tool_single():
    """Test func_to_tool with single function"""
    tools = func_to_tool(example_func)
    assert isinstance(tools, list)
    assert len(tools) == 1
    assert isinstance(tools[0], Tool)
    assert tools[0].function == example_func


def test_func_to_tool_multiple():
    """Test func_to_tool with multiple functions"""
    funcs = [example_func, example_processor]
    tools = func_to_tool(funcs)
    assert len(tools) == 2
    assert all(isinstance(t, Tool) for t in tools)
    assert [t.function_name for t in tools] == [
        "example_func",
        "example_processor",
    ]


def test_func_to_tool_with_parser():
    """Test func_to_tool with parser"""
    tools = func_to_tool(example_func, parser=example_parser)
    assert tools[0].parser == example_parser


def test_func_to_tool_validation():
    """Test func_to_tool validation"""
    # Test mismatched parsers
    with pytest.raises(ValueError):
        func_to_tool(
            [example_func, example_processor], parser=[example_parser]
        )


def test_func_to_tool_docstring_styles():
    """Test func_to_tool with different docstring styles"""
    # Test google style (default)
    tools = func_to_tool(example_func)
    assert "description" in tools[0].schema_["function"]

    # Test rest style
    tools = func_to_tool(example_func, docstring_style="rest")
    assert "description" in tools[0].schema_["function"]


def test_tool_schema_generation():
    """Test schema generation for Tool"""
    tool = Tool(function=example_func)
    schema = tool.schema_

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
