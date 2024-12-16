import pytest

from lionagi.libs.parse import (
    deep_update,
    get_target_container,
    is_homogeneous,
    is_same_dtype,
    is_structure_homogeneous,
)


# Tests for is_homogeneous function
@pytest.mark.parametrize(
    "input_data, type_check, expected",
    [
        ([1, 2, 3], int, True),
        ([1, "2", 3], int, False),
        ({"a": 1, "b": 2}, int, True),
        ({"a": 1, "b": "2"}, int, False),
        ([], int, True),
        ({}, int, True),
        (1, int, True),
        ("1", int, False),
        ([1.0, 2.0, 3.0], float, True),
        (["a", "b", "c"], str, True),
        ([True, False, True], bool, True),
        ([1, 1.0, "1"], (int, float, str), True),
    ],
)
def test_is_homogeneous(input_data, type_check, expected):
    assert is_homogeneous(input_data, type_check) == expected


# Tests for is_same_dtype function
@pytest.mark.parametrize(
    "input_data, dtype, return_dtype, expected",
    [
        ([1, 2, 3], int, False, True),
        ([1, "2", 3], int, False, False),
        ({"a": 1, "b": 2}, int, False, True),
        ({"a": 1, "b": "2"}, int, False, False),
        ([], None, False, True),
        ({}, None, False, True),
        ([1, 2, 3], int, True, (True, int)),
        ([1, "2", 3], int, True, (False, int)),
        ([1.0, 2.0, 3.0], float, True, (True, float)),
        (["a", "b", "c"], str, True, (True, str)),
        ([True, False, True], bool, True, (True, bool)),
    ],
)
def test_is_same_dtype(input_data, dtype, return_dtype, expected):
    assert is_same_dtype(input_data, dtype, return_dtype) == expected


# Tests for is_structure_homogeneous function
@pytest.mark.parametrize(
    "input_data, return_structure_type, expected",
    [
        ({"a": {"b": 1}, "c": {"d": 2}}, False, True),
        ({"a": {"b": 1}, "c": [1, 2]}, False, False),
        ([[1], [2]], False, True),
        ([{"a": 1}, [1, 2]], False, False),
        ({"a": {"b": 1}, "c": {"d": 2}}, True, (True, dict)),
        ({"a": {"b": 1}, "c": [1, 2]}, True, (False, None)),
        ([[1], [2]], True, (True, list)),
        ([{"a": 1}, [1, 2]], True, (False, None)),
        ({"a": {"b": {"c": 1}}}, True, (True, dict)),
        ([[[1]], [[2]]], True, (True, list)),
        (1, True, (True, None)),
        ("string", True, (True, None)),
    ],
)
def test_is_structure_homogeneous(input_data, return_structure_type, expected):
    assert (
        is_structure_homogeneous(input_data, return_structure_type) == expected
    )


# Tests for deep_update function
@pytest.mark.parametrize(
    "original, update, expected",
    [
        (
            {"a": 1, "b": {"x": 2}},
            {"b": {"y": 3}, "c": 4},
            {"a": 1, "b": {"x": 2, "y": 3}, "c": 4},
        ),
        ({"a": 1, "b": {"x": 2}}, {"b": {"x": 3}}, {"a": 1, "b": {"x": 3}}),
        ({}, {"a": 1}, {"a": 1}),
        ({"a": [1, 2]}, {"a": [3]}, {"a": [3]}),
        (
            {"a": {"b": {"c": 1}}},
            {"a": {"b": {"d": 2}}},
            {"a": {"b": {"c": 1, "d": 2}}},
        ),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": {"b": 1}}, {"a": None}, {"a": None}),
    ],
)
def test_deep_update(original, update, expected):
    assert deep_update(original, update) == expected


# Tests for get_target_container function
@pytest.mark.parametrize(
    "nested, indices, expected",
    [
        ([1, [2, 3], 4], [1, 1], 3),
        ({"a": {"b": {"c": 1}}}, ["a", "b"], {"c": 1}),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 2),
        ([1, [2, [3, 4]]], [1, 1, 1], 4),
        ({"a": {"b": [{"c": 1}, {"c": 2}]}}, ["a", "b", 1, "c"], 2),
    ],
)
def test_get_target_container(nested, indices, expected):
    assert get_target_container(nested, indices) == expected


@pytest.mark.parametrize(
    "nested, indices, error",
    [
        ([1, [2, 3], 4], [1, 3], IndexError),
        ({"a": {"b": {"c": 1}}}, ["a", "x"], KeyError),
        ({"a": [1, 2]}, ["a", "b"], IndexError),
        (1, [0], TypeError),
    ],
)
def test_get_target_container_errors(nested, indices, error):
    with pytest.raises(error):
        get_target_container(nested, indices)


# Additional tests for edge cases and more complex scenarios


def test_is_homogeneous_with_custom_objects():
    class CustomObj:
        pass

    objs = [CustomObj(), CustomObj(), CustomObj()]
    assert is_homogeneous(objs, CustomObj)


def test_is_same_dtype_with_subclasses():
    class Animal:
        pass

    class Dog(Animal):
        pass

    class Cat(Animal):
        pass

    animals = [Dog(), Cat(), Animal()]
    assert is_same_dtype(animals, Animal)


def test_is_structure_homogeneous_with_empty_structures():
    assert is_structure_homogeneous({})
    assert is_structure_homogeneous([])
    assert is_structure_homogeneous({"a": {}, "b": {}})
    assert is_structure_homogeneous([[], []])


def test_deep_update_with_complex_structures():
    original = {"a": [1, {"b": 2}], "c": {"d": [3, 4], "e": {"f": 5}}}
    update = {"a": [1, {"b": 3}], "c": {"d": [3, 5, 6], "e": {"g": 7}}}
    expected = {
        "a": [1, {"b": 3}],
        "c": {"d": [3, 5, 6], "e": {"f": 5, "g": 7}},
    }
    assert deep_update(original, update) == expected


def test_get_target_container_with_mixed_types():
    nested = {"a": [{"b": [1, 2, {"c": 3}]}, {"d": {"e": [4, {"f": 5}]}}]}
    indices = ["a", 1, "d", "e", 1, "f"]
    assert get_target_container(nested, indices) == 5


# Performance tests
import time


def test_deep_update_performance():
    large_dict = {
        f"key_{i}": {f"subkey_{j}": j for j in range(100)} for i in range(1000)
    }
    update_dict = {
        f"key_{i}": {f"subkey_{50}": "updated"} for i in range(500, 1000)
    }

    start_time = time.time()
    result = deep_update(large_dict, update_dict)
    end_time = time.time()

    assert result["key_750"]["subkey_50"] == "updated"
    assert (
        end_time - start_time < 1
    )  # Assuming it should take less than 1 second


def test_get_target_container_performance():
    large_nested = {"level1": {}}
    current = large_nested["level1"]
    for i in range(2, 1001):
        current[f"level{i}"] = {}
        current = current[f"level{i}"]
    current["value"] = "deep"

    indices = [f"level{i}" for i in range(1, 1001)] + ["value"]

    start_time = time.time()
    result = get_target_container(large_nested, indices)
    end_time = time.time()

    assert result == "deep"
    assert (
        end_time - start_time < 1
    )  # Assuming it should take less than 1 second


# File: tests/test_util.py
