import inspect
from typing import Any

import pytest

from lionagi.libs.base import FunctionSchema
from lionagi.libs.parse.function_to_schema import (
    _extract_docstring_details_google,
    _extract_docstring_details_rest,
    _get_docstring_lines,
    extract_docstring,
    function_to_schema,
)


def test_get_docstring_lines():
    def example_func():
        """
        Line 1
        Line 2
        Line 3
        """
        pass

    lines = _get_docstring_lines(example_func)
    assert len(lines) == 3
    assert lines[0].strip() == "Line 1"
    assert lines[1].strip() == "Line 2"
    assert lines[2].strip() == "Line 3"


def test_get_docstring_lines_no_docstring():
    def example_func():
        pass

    lines = _get_docstring_lines(example_func)
    assert lines == []


def test_extract_docstring_google_style():
    def example_func(param1: int, param2: str):
        """Example function.

        Args:
            param1 (int): First parameter.
            param2 (str): Second parameter.
        """
        pass

    desc, params = extract_docstring(example_func, style="google")
    assert desc == "Example function."
    assert params == {
        "param1": "First parameter.",
        "param2": "Second parameter.",
    }


def test_extract_docstring_rest_style():
    def example_func(param1: int, param2: str):
        """Example function.

        :param param1: First parameter.
        :type param1: int
        :param param2: Second parameter.
        :type param2: str
        """
        pass

    desc, params = extract_docstring(example_func, style="rest")
    assert desc == "Example function."
    assert params == {
        "param1": "First parameter.",
        "param2": "Second parameter.",
    }


def test_extract_docstring_invalid_style():
    def example_func():
        pass

    with pytest.raises(ValueError, match="not supported"):
        extract_docstring(example_func, style="invalid")


def test_extract_docstring_google_multiline_param():
    def example_func(param1: int):
        """Example function.

        Args:
            param1 (int): First parameter
                with multiple lines
                of description.
        """
        pass

    desc, params = extract_docstring(example_func, style="google")
    assert desc == "Example function."
    assert (
        params["param1"]
        == "First parameter with multiple lines of description."
    )


def test_extract_docstring_rest_multiline_param():
    def example_func(param1: int):
        """Example function.

        :param param1: First parameter
            with multiple lines
            of description.
        :type param1: int
        """
        pass

    desc, params = extract_docstring(example_func, style="rest")
    assert desc == "Example function."
    assert (
        params["param1"]
        == "First parameter with multiple lines of description."
    )


def test_extract_docstring_google_no_args_section():
    def example_func():
        """Example function without args section."""
        pass

    desc, params = extract_docstring(example_func, style="google")
    assert desc == "Example function without args section."
    assert params == {}


def test_extract_docstring_rest_no_params():
    def example_func():
        """Example function without params."""
        pass

    desc, params = extract_docstring(example_func, style="rest")
    assert desc == "Example function without params."
    assert params == {}


def test_function_to_schema_basic():
    def example_func(param1: int, param2: str = "default") -> bool:
        """Example function.

        Args:
            param1 (int): First parameter.
            param2 (str): Second parameter.
        """
        return True

    schema = function_to_schema(example_func)
    assert isinstance(schema, FunctionSchema)
    assert schema.name == "example_func"
    assert schema.description == "Example function."
    assert schema.parameters["type"] == "object"
    assert "param1" in schema.parameters["properties"]
    assert "param2" in schema.parameters["properties"]
    assert schema.parameters["properties"]["param1"]["type"] == "integer"
    assert schema.parameters["properties"]["param2"]["type"] == "string"
    assert schema.parameters["required"] == ["param1"]


def test_function_to_schema_custom_descriptions():
    def example_func(param1: int, param2: str):
        pass

    schema = function_to_schema(
        example_func,
        func_description="Custom function description",
        params_description={
            "param1": "Custom param1 description",
            "param2": "Custom param2 description",
        },
    )
    assert schema.description == "Custom function description"
    assert (
        schema.parameters["properties"]["param1"]["description"]
        == "Custom param1 description"
    )
    assert (
        schema.parameters["properties"]["param2"]["description"]
        == "Custom param2 description"
    )


def test_function_to_schema_no_type_hints():
    def example_func(param1, param2):
        """Example function.

        Args:
            param1: First parameter.
            param2: Second parameter.
        """
        pass

    schema = function_to_schema(example_func)
    assert schema.parameters["properties"]["param1"]["type"] == "string"
    assert schema.parameters["properties"]["param2"]["type"] == "string"


def test_function_to_schema_no_docstring():
    def example_func(param1: int, param2: str):
        pass

    schema = function_to_schema(example_func)
    assert schema.description == "No description provided."
    assert schema.parameters["properties"]["param1"]["description"] == ""
    assert schema.parameters["properties"]["param2"]["description"] == ""


def test_function_to_schema_with_defaults():
    def example_func(param1: int = 0, param2: str = "default"):
        pass

    schema = function_to_schema(example_func)
    assert schema.parameters["required"] == []


def test_function_to_schema_unknown_type():
    class CustomType:
        pass

    def example_func(param: CustomType):
        pass

    schema = function_to_schema(example_func)
    assert schema.parameters["properties"]["param"]["type"] == "string"
