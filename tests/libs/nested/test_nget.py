import pytest

from lionagi.libs.nested.nget import nget


@pytest.mark.parametrize(
    "data, indices, expected",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 3),
        ([1, [2, [3, 4]]], [1, 1, 0], 3),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 2),
        ({"a": 1, "b": 2}, ["b"], 2),
        ({"a": {"b": [{"c": 1}, {"c": 2}]}}, ["a", "b", 1, "c"], 2),
        ({"a": {"b": {"c": {"d": {"e": 5}}}}}, ["a", "b", "c", "d", "e"], 5),
        ([[[1]]], [0, 0, 0], 1),
        ({"a": [1, 2, {"b": [3, 4, {"c": 5}]}]}, ["a", 2, "b", 2, "c"], 5),
    ],
)
def test_nget_valid_paths(data, indices, expected):
    assert nget(data, indices) == expected


@pytest.mark.parametrize(
    "data, indices, default, expected",
    [
        ({"a": {"b": 2}}, ["a", "c"], 10, 10),
        ({"a": [1, 2, 3]}, [0, 1], "default", "default"),
        ({}, ["a", "b"], None, None),
    ],
)
def test_nget_with_default(data, indices, default, expected):
    assert nget(data, indices, default) == expected


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
def test_nget_raises_lookup_error(data, indices):
    with pytest.raises(LookupError):
        nget(data, indices)


@pytest.mark.parametrize(
    "data, indices",
    [
        ([1, 2, 3], ["a"]),
        ({"a": 1}, [0]),
        ({"a": [1, 2, 3]}, ["a", "b"]),
    ],
)
def test_nget_raises_type_error(data, indices):
    with pytest.raises(LookupError):
        nget(data, indices)


def test_nget_empty_indices():
    with pytest.raises(
        LookupError, match="Target not found and no default value provided."
    ):
        nget({"a": 1}, [])


def test_nget_none_data():
    with pytest.raises(LookupError):
        nget(None, ["a"])


def test_nget_non_subscriptable():
    with pytest.raises(LookupError):
        nget(42, [0])


def test_nget_with_zero_index():
    data = [1, 2, 3]
    assert nget(data, [0]) == 1


def test_nget_with_string_index_for_list():
    data = [1, 2, 3]
    with pytest.raises(LookupError):
        nget(data, ["0"])


def test_nget_with_int_index_for_dict():
    data = {"0": "value"}
    assert nget(data, ["0"]) == "value"


@pytest.mark.parametrize(
    "data, indices, expected",
    [
        ([1, 2, [3, 4, [5, 6]]], [2, 2, 1], 6),
        ({"a": [{"b": {"c": [1, 2, 3]}}]}, ["a", 0, "b", "c", 2], 3),
    ],
)
def test_nget_long_paths(data, indices, expected):
    assert nget(data, indices) == expected


def test_nget_with_large_nested_structure():
    large_data = {"level1": {}}
    current = large_data["level1"]
    for i in range(2, 101):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    indices = [f"level{i}" for i in range(1, 101)] + ["value"]
    assert nget(large_data, indices) == "deep"


def test_nget_with_all_python_basic_types():
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
    for key in data.keys():
        assert nget(data, [key]) == data[key]


# File: tests/test_nget.py
