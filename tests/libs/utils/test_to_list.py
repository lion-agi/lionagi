from collections import OrderedDict, deque, namedtuple

import pytest
from pydantic import BaseModel

from lionagi.utils import to_list


class CustomIterable:
    def __iter__(self):
        return iter([1, 2, 3])


class CustomMapping:
    def __getitem__(self, key):
        return {1: "a", 2: "b", 3: "c"}[key]

    def keys(self):
        return [1, 2, 3]


class TestModel(BaseModel):
    field_: str = "value"


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (1, [1]),
        (1.5, [1.5]),
        (True, [True]),
        ("string", ["string"]),
        (b"bytes", [b"bytes"]),
        (bytearray(b"bytearray"), [bytearray(b"bytearray")]),
    ],
)
def test_primitive_types(input_value, expected):
    assert to_list(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected, flatten",
    [
        ([1, 2, 3], [1, 2, 3], False),
        ([1, [2, 3]], [1, [2, 3]], False),
        ([1, [2, 3]], [1, 2, 3], True),
    ],
)
def test_list_input(input_value, expected, flatten):
    assert to_list(input_value, flatten=flatten) == expected


@pytest.mark.parametrize(
    "input_value, expected, flatten",
    [
        ((1, 2, 3), [1, 2, 3], False),
        ((1, (2, 3)), [1, 2, 3], True),
    ],
)
def test_tuple_input(input_value, expected, flatten):
    assert (
        to_list(input_value, flatten=flatten, flatten_tuple_set=True)
        == expected
    )


def test_set_input():
    assert set(to_list({1, 2, 3})) == {1, 2, 3}


def test_dict_input():
    assert to_list({"a": 1, "b": 2}) == [{"a": 1, "b": 2}]


def test_ordereddict_input():
    od = OrderedDict([("a", 1), ("b", 2)])
    assert to_list(od) == [od]


def test_custom_mapping():
    cm = CustomMapping()
    assert to_list(cm) == [cm]


def test_generator_input():
    def gen():
        yield from range(3)

    assert to_list(gen()) == [0, 1, 2]


def test_custom_iterable():
    ci = CustomIterable()
    assert to_list(ci) == [1, 2, 3]


def test_deque_input():
    d = deque([1, 2, 3])
    assert to_list(d) == [1, 2, 3]


def test_namedtuple_input():
    Point = namedtuple("Point", ["x", "y"])
    p = Point(1, 2)
    assert to_list(p) == [1, 2]


def test_pydantic_model():
    model = TestModel()
    assert to_list(model) == [model]


@pytest.mark.parametrize(
    "input_value, expected, flatten",
    [
        ([1, [2, [3, [4]]]], [1, [2, [3, [4]]]], False),
        ([1, [2, [3, [4]]]], [1, 2, 3, 4], True),
    ],
)
def test_nested_structures(input_value, expected, flatten):
    assert to_list(input_value, flatten=flatten) == expected


@pytest.mark.parametrize(
    "input_value, expected, flatten",
    [
        ([1, "two", [3, [4, "five"]]], [1, "two", [3, [4, "five"]]], False),
        ([1, "two", [3, [4, "five"]]], [1, "two", 3, 4, "five"], True),
    ],
)
def test_mixed_types(input_value, expected, flatten):
    assert to_list(input_value, flatten=flatten) == expected


@pytest.mark.parametrize(
    "input_value, expected, flatten, dropna",
    [
        ([1, None, 2, [3, None, 4]], [1, 2, [3, 4]], False, True),
        ([1, None, 2, [3, None, 4]], [1, 2, 3, 4], True, True),
    ],
)
def test_dropna(input_value, expected, flatten, dropna):
    assert to_list(input_value, flatten=flatten, dropna=dropna) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([], []),
        ({}, [{}]),
        (set(), []),
    ],
)
def test_empty_inputs(input_value, expected):
    assert to_list(input_value) == expected


def test_large_input():
    large_list = list(range(10000))
    assert to_list(large_list) == large_list


@pytest.mark.parametrize(
    "input_value, expected",
    [
        (
            [1, "nested", [2, ["deep", "list"]]],
            [1, "nested", 2, "deep", "list"],
        ),
    ],
)
def test_flatten_with_strings(input_value, expected):
    assert to_list(input_value, flatten=True) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ([1, (2, 3), [4, (5, 6)]], [1, 2, 3, 4, 5, 6]),
    ],
)
def test_flatten_with_tuple(input_value, expected):
    assert (
        to_list(input_value, flatten=True, flatten_tuple_set=True) == expected
    )


def test_flatten_with_set():
    input_with_set = [1, {2, 3}, [4, {5, 6}]]
    flattened = to_list(input_with_set, flatten=True, flatten_tuple_set=True)
    assert len(flattened) == 6
    assert set(flattened) == {1, 2, 3, 4, 5, 6}


def test_flatten_with_dict():
    input_with_dict = [1, {"a": 2}, [3, {"b": 4}]]
    expected = [1, {"a": 2}, 3, {"b": 4}]
    assert to_list(input_with_dict, flatten=True) == expected


def test_generator_with_none():
    def gen_with_none():
        yield 1
        yield None
        yield 2

    assert to_list(gen_with_none(), dropna=True) == [1, 2]


def test_deeply_nested_structure():
    deeply_nested = [1, [2, [3, [4, [5, [6]]]]]]
    assert to_list(deeply_nested, flatten=True) == [1, 2, 3, 4, 5, 6]


def test_input_with_all_none():
    assert to_list([None, None, None], dropna=True) == []


def test_custom_objects():
    class CustomObj:
        pass

    obj = CustomObj()
    assert to_list(obj) == [obj]


def test_flatten_with_empty_nested_structures():
    input_with_empty = [1, [], [2, []], [[], 3]]
    assert to_list(input_with_empty, flatten=True) == [1, 2, 3]


def test_flatten_and_dropna_combination():
    complex_input = [1, None, [2, None, [3, None, 4]]]
    assert to_list(complex_input, flatten=True, dropna=True) == [1, 2, 3, 4]


def test_input_types_preservation():
    mixed_types = [1, "two", 3.0, True, b"four"]
    assert to_list(mixed_types) == mixed_types


def test_very_large_nested_structure():
    large_nested = list(range(1000)) + [list(range(1000, 2000))]
    flattened = to_list(large_nested, flatten=True)
    assert len(flattened) == 2000
    assert flattened[-1] == 1999


def test_to_list_with_frozenset():
    fs = frozenset([1, 2, 3])
    assert set(to_list(fs)) == {1, 2, 3}


def test_to_list_with_view():
    d = {1: "a", 2: "b", 3: "c"}
    assert set(to_list(d.keys())) == {1, 2, 3}
    assert set(to_list(d.values())) == {"a", "b", "c"}


def test_to_list_with_enum():
    from enum import Enum

    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert to_list(Color) == [Color.RED, Color.GREEN, Color.BLUE]


def test_to_list_with_range():
    r = range(5)
    assert to_list(r) == [0, 1, 2, 3, 4]


def test_to_list_with_iterator():
    it = iter([1, 2, 3])
    assert to_list(it) == [1, 2, 3]


def test_to_list_with_generator_expression():
    gen_exp = (x for x in range(5))
    assert to_list(gen_exp) == [0, 1, 2, 3, 4]


def test_to_list_with_zip():
    z = zip([1, 2, 3], ["a", "b", "c"])
    assert to_list(z) == [(1, "a"), (2, "b"), (3, "c")]


def test_to_list_with_filter():
    f = filter(lambda x: x % 2 == 0, range(10))
    assert to_list(f) == [0, 2, 4, 6, 8]


def test_to_list_with_map():
    m = map(lambda x: x * 2, range(5))
    assert to_list(m) == [0, 2, 4, 6, 8]


def test_to_list_with_bytes():
    b = b"hello"
    assert to_list(b, use_values=True) == [104, 101, 108, 108, 111]


def test_to_list_with_memoryview():
    mv = memoryview(b"hello")
    assert to_list(mv, use_values=True) == [104, 101, 108, 108, 111]


def test_to_list_with_complex():
    c = 1 + 2j
    assert to_list(c) == [c]


def test_to_list_with_custom_flatten():
    class CustomFlatten:
        def __iter__(self):
            return iter([1, [2, 3]])

    cf = CustomFlatten()
    assert to_list(cf, flatten=True) == [1, 2, 3]


# File: tests/test_to_list.py
