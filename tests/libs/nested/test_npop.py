import pytest

from lionagi.libs.nested.npop import npop
from lionagi.utils import UNDEFINED


@pytest.mark.parametrize(
    "data, indices, expected_result, expected_data",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 3, {"a": {"b": {}}}),
        ({"a": {"b": [1, 2, 3]}}, ["a", "b", 2], 3, {"a": {"b": [1, 2]}}),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 2, {"a": [1, {}]}),
        ({"a": 1, "b": 2}, ["b"], 2, {"a": 1}),
        ([1, [2, [3, 4]], 5], [1, 1, 0], 3, [1, [2, [4]], 5]),
        (
            {"key with spaces": {"nested": "value"}},
            ["key with spaces", "nested"],
            "value",
            {"key with spaces": {}},
        ),
        ({0: "zero", 1: "one"}, [1], "one", {0: "zero"}),
        ({"a": {"b": None}}, ["a", "b"], None, {"a": {}}),
        ({"": {"nested": "value"}}, ["", "nested"], "value", {"": {}}),
        ({True: "true", False: "false"}, [True], "true", {False: "false"}),
        ({(1, 2): "tuple key"}, [(1, 2)], "tuple key", {}),
        (
            {"a": {"b": {"c": {"d": 1}}}},
            ["a", "b", "c", "d"],
            1,
            {"a": {"b": {"c": {}}}},
        ),
    ],
)
def test_npop_various_scenarios(data, indices, expected_result, expected_data):
    assert npop(data, indices) == expected_result
    assert data == expected_data


@pytest.mark.parametrize(
    "data, indices",
    [
        ({}, ["a"]),
        ([], [0]),
        ({"a": {"b": 2}}, ["a", "c"]),
        ([1, 2, 3], [3]),
        ({"a": [1, 2]}, ["a", 2]),
        ({"a": {"b": 1}}, ["a", "b", "c"]),
    ],
)
def test_npop_raises_key_error(data, indices):
    with pytest.raises(KeyError):
        npop(data, indices)


@pytest.mark.parametrize(
    "data, indices",
    [
        ([1, 2, 3], ["a"]),
        ({"a": 1}, [0]),
        ({"a": [1, 2, 3]}, ["a", "b"]),
    ],
)
def test_npop_raises_type_error(data, indices):
    with pytest.raises(KeyError):
        npop(data, indices)


def test_npop_empty_indices():
    data = {"a": 1}
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        npop(data, [])


def test_npop_none_data():
    with pytest.raises(KeyError):
        npop(None, ["a"])


def test_npop_non_subscriptable():
    with pytest.raises(KeyError):
        npop(42, [0])


def test_npop_with_zero_index():
    data = [1, 2, 3]
    assert npop(data, [0]) == 1
    assert data == [2, 3]


def test_npop_with_negative_index():
    data = [1, 2, 3]
    assert npop(data, [-1]) == 3


def test_npop_with_string_index_for_list():
    data = [1, 2, 3]
    with pytest.raises(KeyError):
        npop(data, ["0"])


def test_npop_with_int_index_for_dict():
    data = {"0": "value"}
    assert npop(data, ["0"]) == "value"
    assert data == {}


def test_npop_with_nested_default_dict():
    from collections import defaultdict

    data = defaultdict(lambda: defaultdict(int))
    data["a"]["b"] = 1
    assert npop(data, ["a", "b"]) == 1
    assert dict(data) == {"a": {}}


def test_npop_with_property():
    class PropObj:
        def __init__(self):
            self._data = {"key": "value"}

        @property
        def data(self):
            return self._data

    obj = PropObj()
    assert npop(obj.data, ["key"]) == "value"
    assert obj._data == {}


@pytest.mark.parametrize(
    "data, indices, expected_result, expected_data",
    [
        ({"a": 1, "b": 2, "c": 3}, ["c"], 3, {"a": 1, "b": 2}),
        ([1, 2, [3, 4, [5, 6]]], [2, 2, 1], 6, [1, 2, [3, 4, [5]]]),
        (
            {"a": [{"b": {"c": [1, 2, 3]}}]},
            ["a", 0, "b", "c", 2],
            3,
            {"a": [{"b": {"c": [1, 2]}}]},
        ),
    ],
)
def test_npop_long_paths(data, indices, expected_result, expected_data):
    assert npop(data, indices) == expected_result
    assert data == expected_data


def test_npop_with_all_python_basic_types():
    data = {
        "int": 1,
        "float": 2.0,
        "complex": 1 + 2j,
        "str": "string",
        "list": [1, 2, 3],
        "tuple": (4, 5, 6),
        "dict": {"key": "value"},
        "set": {7, 8, 9},
        "frozenset": frozenset([10, 11, 12]),
        "bool": True,
        "none": None,
        "bytes": b"bytes",
        "bytearray": bytearray(b"bytearray"),
    }
    for key in list(data.keys()):
        value = data[key]
        assert npop(data, [key]) == value
    assert data == {}


def is_recursive_dict(d):
    """Check if the dictionary has a recursive structure."""
    seen = set()

    def check(obj):
        if id(obj) in seen:
            return True
        if isinstance(obj, dict):
            seen.add(id(obj))
            return any(check(v) for v in obj.values())

    return check(d)


def test_npop_with_recursive_structure():
    data = {"a": 1}
    data["b"] = data
    assert npop(data, ["a"]) == 1
    assert len(data) == 1
    assert "b" in data
    assert is_recursive_dict(data)
    assert data["b"] is data


def test_npop_with_custom_classes():
    class CustomList(list):
        pass

    class CustomDict(dict):
        pass

    data = CustomDict({"a": CustomList([1, 2, 3])})
    assert npop(data, ["a", 1]) == 2
    assert data == CustomDict({"a": CustomList([1, 3])})


# File: tests/test_npop.py
