from collections import OrderedDict, namedtuple

import pytest
from pydantic import BaseModel

from lionagi.libs.parse.types import to_str
from lionagi.utils import UNDEFINED, UndefinedType


class CustomModel(BaseModel):
    field: str = "value"


class CustomObject:
    def __str__(self):
        return "CustomObject"


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (123, "123"),
        (3.14, "3.14"),
        (True, "True"),
    ],
)
def test_primitive_types(input_value, expected):
    assert to_str(input_value) == expected


@pytest.mark.parametrize(
    "input_value, strip_lower_flag, chars, expected",
    [
        ("Hello", False, None, "Hello"),
        ("  WORLD  ", True, None, "world"),
        ("__TEST__", True, "_", "test"),
    ],
)
def test_string_input(input_value, strip_lower_flag, chars, expected):
    assert (
        to_str(input_value, strip_lower=strip_lower_flag, chars=chars)
        == expected
    )


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (b"hello", "hello"),
        (bytearray(b"world"), "world"),
    ],
)
def test_bytes_and_bytearray(input_value, expected):
    assert to_str(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([1, 2, 3], "[1, 2, 3]"),
        ([1, [2, 3]], "[1, [2, 3]]"),
    ],
)
def test_list_input(input_value, expected):
    assert to_str(input_value) == expected


def test_tuple_input():
    assert to_str((1, 2, 3)) == "(1, 2, 3)"


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ({"a": 1, "b": 2}, '{"a": 1, "b": 2}'),
        (OrderedDict([("a", 1), ("b", 2)]), '{"a": 1, "b": 2}'),
    ],
)
def test_dict_input(input_value, expected):
    assert to_str(input_value) == expected


def test_nested_structures():
    nested = [1, [2, 3], {"a": 4}]
    assert to_str(nested) == "[1, [2, 3], {'a': 4}]"


@pytest.mark.parametrize("use_model_dump", [True, False])
def test_pydantic_model(use_model_dump):
    model = CustomModel(field="test")
    if use_model_dump:
        assert (
            to_str(model, use_model_dump=True, serialize_as="json")
            == '{"field": "test"}'
        )
    else:
        assert to_str(model, use_model_dump=False) == "field='test'"


def test_custom_object():
    obj = CustomObject()
    assert to_str(obj) == "CustomObject"


def test_mixed_types_in_sequence():
    mixed = [1, "two", 3.0, [4, 5], {"six": 6}]
    expected = "[1, 'two', 3.0, [4, 5], {'six': 6}]"
    assert to_str(mixed) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([], ""),
        ({}, ""),
        (set(), ""),
    ],
)
def test_empty_inputs(input_value, expected):
    assert to_str(input_value) == expected


def test_large_input():
    large_list = list(range(1000))
    result = to_str(large_list)
    assert len(result.split(", ")) == 1000


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("こんにちは", "こんにちは"),
        ("こんにちは".encode(), "こんにちは"),
    ],
)
def test_unicode_handling(input_value, expected):
    assert to_str(input_value) == expected


def test_escape_characters():
    text = 'Line 1\nLine 2\t"Quoted"'
    expected = '{"text": "Line 1\\nLine 2\\t\\"Quoted\\""}'
    assert to_str(text) == text
    assert to_str({"text": text}) == expected


def test_combination_of_options():
    data = "  WORLD:123  "
    expected = "world:123"
    assert to_str(data, strip_lower=True) == expected


def test_error_handling():
    class ErrorObject:
        def __str__(self):
            raise Exception("Str conversion error")

    with pytest.raises(
        ValueError,
        match="Could not convert input of type <ErrorObject> to string",
    ):
        to_str(ErrorObject())


def test_namedtuple():
    Point = namedtuple("Point", ["x", "y"])
    p = Point(1, 2)
    assert to_str(p) == "Point(x=1, y=2)"


def test_complex_number():
    assert to_str(1 + 2j) == "(1+2j)"


import json


def test_bytes_with_non_utf8():
    assert to_str(b"\xff\xfe") == "��"


def test_very_long_string():
    long_string = "a" * 1000000
    result = to_str(long_string)
    assert len(result) == 1000000


def test_recursive_structure():
    recursive_dict = {}
    recursive_dict["a"] = recursive_dict
    with pytest.raises(ValueError, match="Circular reference detected"):
        to_str(recursive_dict)


def test_custom_object_with_repr():
    class CustomRepr:
        def __repr__(self):
            return "CustomRepr()"

    assert to_str(CustomRepr()) == "CustomRepr()"


def test_enum():
    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2

    assert to_str(Color.RED) == "Color.RED"


def test_function():
    def test_func():
        pass

    assert "test_func" in to_str(test_func)


def test_module():
    import math

    assert "module 'math'" in to_str(math)


def test_memoryview():
    mv = memoryview(b"hello")
    assert to_str(mv).startswith("<memory at")


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (range(5), "range(0, 5)"),
        (slice(1, 5, 2), "slice(1, 5, 2)"),
    ],
)
def test_builtin_types(input_value, expected):
    assert to_str(input_value) == expected


# File: tests/test_to_str.py
