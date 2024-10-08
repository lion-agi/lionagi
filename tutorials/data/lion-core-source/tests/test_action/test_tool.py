import asyncio
import json
from typing import Any

import pytest

from lion_core.action.tool import Tool, func_to_tool


# Sample functions for testing
def sample_function(x: int, y: int) -> int:
    """
    A sample function that adds two numbers.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The sum of x and y.
    """
    return x + y


async def async_sample_function(x: int, y: int) -> int:
    """
    An async sample function that adds two numbers.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The sum of x and y.
    """
    return x + y


def sample_preprocessor(args: dict[str, Any]) -> dict[str, Any]:
    """A sample preprocessor that doubles the input values."""
    return {k: v * 2 for k, v in args.items()}


def sample_postprocessor(result: int) -> str:
    """A sample postprocessor that converts the result to a string."""
    return f"Result: {result}"


def sample_parser(result: Any) -> dict[str, Any]:
    """A sample parser that wraps the result in a dictionary."""
    return {"parsed_result": result}


# Test Tool class
def test_tool_init():
    tool = Tool(function=sample_function)
    assert callable(tool.function)
    assert tool.schema_ is not None
    assert tool.schema_["function"]["name"] == "sample_function"


def test_tool_init_with_schema():
    custom_schema = {"function": {"name": "custom_function"}}
    tool = Tool(function=sample_function, schema_=custom_schema)
    assert tool.schema_ == custom_schema


def test_tool_function_name():
    tool = Tool(function=sample_function)
    assert tool.function_name == "sample_function"


def test_tool_str_representation():
    tool = Tool(function=sample_function)
    str_repr = str(tool)
    assert "Tool(ln_id=" in str_repr
    assert "timestamp=" in str_repr
    assert "schema_=" in str_repr


def test_tool_serialization():
    tool = Tool(
        function=sample_function,
        pre_processor=sample_preprocessor,
        post_processor=sample_postprocessor,
        parser=sample_parser,
        pre_processor_kwargs={"arg1": "value1"},
        post_processor_kwargs={"arg2": "value2"},
    )
    serialized = tool.model_dump_json()
    deserialized = json.loads(serialized)

    assert deserialized["function"] == "sample_function"
    assert deserialized["pre_processor"] == "sample_preprocessor"
    assert deserialized["post_processor"] == "sample_postprocessor"
    assert deserialized["parser"] == "sample_parser"
    assert json.loads(deserialized["pre_processor_kwargs"]) == {
        "arg1": "value1"
    }
    assert json.loads(deserialized["post_processor_kwargs"]) == {
        "arg2": "value2"
    }


# Test func_to_tool function
def test_func_to_tool_single_function():
    tools = func_to_tool(sample_function)
    assert len(tools) == 1
    assert isinstance(tools[0], Tool)
    assert tools[0].function == sample_function


def test_func_to_tool_multiple_functions():
    functions = [sample_function, async_sample_function]
    tools = func_to_tool(functions)
    assert len(tools) == 2
    assert all(isinstance(tool, Tool) for tool in tools)
    assert [tool.function for tool in tools] == functions


def test_func_to_tool_with_parser():
    tools = func_to_tool(sample_function, parser=sample_parser)
    assert len(tools) == 1
    assert tools[0].parser == sample_parser


def test_func_to_tool_multiple_functions_with_parsers():
    functions = [sample_function, async_sample_function]
    parsers = [sample_parser, None]
    tools = func_to_tool(functions, parser=parsers)
    assert len(tools) == 2
    assert tools[0].parser == sample_parser
    assert tools[1].parser is None


def test_func_to_tool_docstring_style():
    tools = func_to_tool(sample_function, docstring_style="rest")
    assert (
        tools[0].schema_["function"]["description"]
        == "A sample function that adds two numbers."
    )


def test_func_to_tool_additional_kwargs():
    tools = func_to_tool(sample_function, pre_processor=sample_preprocessor)
    assert tools[0].pre_processor == sample_preprocessor


def test_func_to_tool_mismatched_parsers():
    with pytest.raises(ValueError):
        func_to_tool(
            [sample_function, async_sample_function], parser=[sample_parser]
        )


# Edge cases and additional tests
def test_tool_with_lambda_function():
    lambda_func = lambda x, y: x * y
    tool = Tool(function=lambda_func)
    assert tool.function == lambda_func
    assert "lambda" in tool.function_name.lower()


def test_tool_with_class_method():
    class SampleClass:
        @classmethod
        def class_method(cls, x: int) -> int:
            return x * 2

    tool = Tool(function=SampleClass.class_method)
    assert tool.function == SampleClass.class_method
    assert tool.function_name == "class_method"


def test_tool_with_static_method():
    class SampleClass:
        @staticmethod
        def static_method(x: int) -> int:
            return x * 3

    tool = Tool(function=SampleClass.static_method)
    assert tool.function == SampleClass.static_method
    assert tool.function_name == "static_method"


def test_func_to_tool_empty_input():
    func_to_tool([])


def test_func_to_tool_non_callable():
    with pytest.raises(AttributeError):
        func_to_tool("not_a_function")


def test_tool_with_function_without_docstring():
    def no_docstring_func(x: int) -> int:
        return x + 1

    tool = Tool(function=no_docstring_func)
    assert tool.schema_["function"]["description"] == None


def test_func_to_tool_preserve_metadata():
    def metadata_func() -> None:
        """Test function with metadata."""
        pass

    metadata_func.custom_attr = "test_value"

    tools = func_to_tool(metadata_func)
    assert hasattr(tools[0].function, "custom_attr")
    assert tools[0].function.custom_attr == "test_value"


@pytest.mark.asyncio
async def test_tool_with_async_function():
    tool = Tool(function=async_sample_function)
    assert asyncio.iscoroutinefunction(tool.function)


def test_tool_schema_generation():
    def typed_func(a: int, b: str, c: bool = False) -> dict:
        """
        A function with typed parameters.

        Args:
            a: An integer parameter
            b: A string parameter
            c: A boolean parameter with default value

        Returns:
            A dictionary
        """
        return {"a": a, "b": b, "c": c}

    tool = Tool(function=typed_func)
    schema = tool.schema_["function"]
    assert schema["name"] == "typed_func"
    assert (
        "An integer parameter"
        in schema["parameters"]["properties"]["a"]["description"]
    )
    assert schema["parameters"]["properties"]["a"]["type"] == "number"
    assert schema["parameters"]["properties"]["b"]["type"] == "string"
    assert schema["parameters"]["properties"]["c"]["type"] == "boolean"
    assert "c" in schema["parameters"]["required"]


def test_tool_with_variable_arguments():
    def var_args_func(*args, **kwargs):
        pass

    tool = Tool(function=var_args_func)
    assert "parameters" in tool.schema_["function"]
