import pytest

from lionagi.libs.nested.nfilter import nfilter


@pytest.mark.parametrize(
    "data, condition, expected",
    [
        (
            {"a": 1, "b": {"c": 2, "d": 3}, "e": [4, 5, 6]},
            lambda x: isinstance(x, int) and x % 2 == 0,
            {"b": {"c": 2}, "e": [4, 6]},
        ),
        (
            [1, 2, [3, 4], {"a": 5, "b": 6}],
            lambda x: isinstance(x, int) and x % 2 == 0,
            [2, [4], {"b": 6}],
        ),
        (
            {"a": [1, {"b": 2, "c": [3, 4]}], "d": 5},
            lambda x: isinstance(x, int) and x % 2 == 0,
            {"a": [{"b": 2, "c": [4]}]},
        ),
        ({}, lambda x: True, {}),
        ([], lambda x: True, []),
        ({"a": 1, "b": 2, "c": 3}, lambda x: x > 1, {"b": 2, "c": 3}),
        ([1, 2, 3, 4, 5], lambda x: x % 2 == 0, [2, 4]),
        (
            {"a": 1, "b": "string", "c": [2, 3], "d": {"e": 4}},
            lambda x: isinstance(x, int),
            {"a": 1, "c": [2, 3], "d": {"e": 4}},
        ),
        (
            [1, "string", [2, 3], {"a": 4}],
            lambda x: isinstance(x, int),
            [1, [2, 3], {"a": 4}],
        ),
        (
            {"a": [1, 2], "b": {"c": 3, "d": 4}, "e": 5},
            lambda x: x % 2 != 0 if isinstance(x, int) else True,
            {"a": [1], "b": {"c": 3}, "e": 5},
        ),
        (
            [1, [2, [3, [4]]]],
            lambda x: x % 2 != 0 if isinstance(x, int) else True,
            [1, [[3, []]]],
        ),
        (
            {"a": 1, "b": 2, "c": {"d": 3, "e": 4, "f": {"g": 5, "h": 6}}},
            lambda x: x % 2 != 0 if isinstance(x, int) else True,
            {"a": 1, "c": {"d": 3, "f": {"g": 5}}},
        ),
        (
            [1, 2, 3, [4, 5, [6, 7, 8]]],
            lambda x: x > 3 if isinstance(x, int) else True,
            [[4, 5, [6, 7, 8]]],
        ),
        (
            {"a": "hello", "b": [1, "world", 3], "c": {"d": "python", "e": 2}},
            lambda x: isinstance(x, str),
            {"a": "hello", "b": ["world"], "c": {"d": "python"}},
        ),
        (
            [{"a": 1, "b": "x"}, {"c": 2, "d": "y"}, {"e": 3, "f": "z"}],
            lambda x: isinstance(x, str),
            [{"b": "x"}, {"d": "y"}, {"f": "z"}],
        ),
    ],
)
def test_nfilter(data, condition, expected):
    assert nfilter(data, condition) == expected


def test_nfilter_with_empty_result():
    data = {"a": 1, "b": 2, "c": 3}
    condition = lambda x: x > 10
    assert nfilter(data, condition) == {}


def test_nfilter_with_all_true_condition():
    data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [4, 5]}
    condition = lambda x: True
    assert nfilter(data, condition) == data


def test_nfilter_with_nested_empty_structures():
    data = {"a": [], "b": {}, "c": {"d": []}}
    condition = lambda x: isinstance(x, (list, dict))
    assert nfilter(data, condition) == data


def test_nfilter_with_custom_objects():
    class CustomObj:
        def __init__(self, value):
            self.value = value

    data = {
        "a": CustomObj(1),
        "b": CustomObj(2),
        "c": [CustomObj(3), CustomObj(4)],
    }
    condition = lambda x: isinstance(x, CustomObj) and x.value % 2 == 0
    expected = {"b": CustomObj(2), "c": [CustomObj(4)]}
    result = nfilter(data, condition)
    assert isinstance(result["b"], CustomObj) and result["b"].value == 2
    assert isinstance(result["c"][0], CustomObj) and result["c"][0].value == 4


def test_nfilter_with_none_values():
    data = {"a": None, "b": 1, "c": {"d": None, "e": 2}}
    condition = lambda x: x is not None
    expected = {"b": 1, "c": {"e": 2}}
    assert nfilter(data, condition) == expected


def test_invalid_input():
    with pytest.raises(
        TypeError,
        match="The nested_structure must be either a dict or a list.",
    ):
        nfilter(42, lambda x: True)


def test_nfilter_with_exception_in_condition():
    def faulty_condition(x):
        if isinstance(x, int):
            raise ValueError("Error in condition")
        return True

    data = {"a": 1, "b": "string", "c": [2, 3]}
    with pytest.raises(ValueError, match="Error in condition"):
        nfilter(data, faulty_condition)


# File: tests/test_nfilter.py
