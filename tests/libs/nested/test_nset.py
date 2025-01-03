import pytest

from lionagi.libs.nested.nset import nset


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": {"b": {"c": 3}}}, ["a", "b", "c"], 99, {"a": {"b": {"c": 99}}}),
        ({"a": {"b": [1, 2, 3]}}, ["a", "b", 2], 99, {"a": {"b": [1, 2, 99]}}),
        ({"a": [1, {"b": 2}]}, ["a", 1, "b"], 99, {"a": [1, {"b": 99}]}),
        ({}, ["a", "b", "c"], 99, {"a": {"b": {"c": 99}}}),
        ([], [0, "a"], 99, [{"a": 99}]),
        ({"a": 1, "b": 2}, ["b"], 99, {"a": 1, "b": 99}),
        ([1, 2, 3], [1], 99, [1, 99, 3]),
        ({"a": {"b": 2}}, ["a", "c"], 99, {"a": {"b": 2, "c": 99}}),
    ],
)
def test_nset_various_scenarios(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_empty_indices():
    data = {"a": 1}
    with pytest.raises(
        ValueError,
        match="Indices list is empty, cannot determine target container",
    ):
        nset(data, [], 2)


@pytest.mark.parametrize(
    "data, indices, value",
    [
        ([1, 2, 3], ["a"], 4),
        ({"a": 1}, [0], 2),
        ({"a": {"b": 2}}, ["a", "b", "c"], 3),
    ],
)
def test_nset_type_errors(data, indices, value):
    with pytest.raises(TypeError):
        nset(data, indices, value)


def test_nset_nested_creation():
    data = {}
    nset(data, ["a", 0, "b", 1, "c"], 42)
    assert data == {"a": [{"b": [None, {"c": 42}]}]}


def test_nset_overwrite_existing():
    data = {"a": {"b": {"c": 1}}}
    nset(data, ["a", "b", "c"], 2)
    assert data == {"a": {"b": {"c": 2}}}


def test_nset_extend_list():
    data = {"a": [1, 2]}
    nset(data, ["a", 5], 3)
    assert data == {"a": [1, 2, None, None, None, 3]}


def test_nset_with_tuple():
    data = {"a": (1, 2)}
    with pytest.raises(TypeError):
        nset(data, ["a", 2], 3)


def test_nset_with_set():
    data = {"a": {1, 2}}
    with pytest.raises(TypeError):
        nset(data, ["a", 3], 3)


def test_nset_with_none():
    data = {"a": None}
    with pytest.raises(TypeError):
        nset(data, ["a", "b"], 1)


def test_nset_with_large_nested_structure():
    data = {}
    for i in range(1000):
        nset(data, ["level" + str(i)], i)
    assert data["level999"] == 999


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": 1}, ["b", "c"], 2, {"a": 1, "b": {"c": 2}}),
        ([1, 2], [2, "a"], 3, [1, 2, {"a": 3}]),
        ({}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_nset_create_intermediate_structures(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_with_negative_list_index():
    data = [1, 2, 3]
    nset(data, [-1], 4)
    assert data == [1, 2, 4]


def test_nset_with_string_key_for_list():
    data = [1, 2, 3]
    with pytest.raises(
        TypeError, match="Cannot use non-integer index on a list"
    ):
        nset(data, ["key"], 4)


def test_nset_with_int_key_for_dict():
    data = {}
    with pytest.raises(TypeError):
        nset(data, [1], "value")


def test_nset_with_existing_none_value():
    data = {"a": {"b": {}}}
    nset(data, ["a", "b", "c"], 1)
    assert data == {"a": {"b": {"c": 1}}}


def test_nset_with_custom_classes():
    class CustomList(list):
        pass

    class CustomDict(dict):
        pass

    data = {
        "custom_list": CustomList([1, 2, 3]),
        "custom_dict": CustomDict({"a": 1, "b": 2}),
    }

    nset(data, ["custom_list", 3], 4)
    assert data["custom_list"] == [1, 2, 3, 4]

    nset(data, ["custom_dict", "c"], 3)
    assert data["custom_dict"] == {"a": 1, "b": 2, "c": 3}


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": 1}, ["b", 0, "c"], 2, {"a": 1, "b": [{"c": 2}]}),
        ([], [0, "a", 0, "b"], 1, [{"a": [{"b": 1}]}]),
        ({}, ["a", 0, "b", 0, "c"], 1, {"a": [{"b": [{"c": 1}]}]}),
    ],
)
def test_nset_deep_nested_creation(initial, indices, value, expected):
    nset(initial, indices, value)
    assert initial == expected


def test_nset_with_duplicate_indices():
    data = {}
    nset(data, ["a", "a", "a"], "value")
    assert data == {"a": {"a": {"a": "value"}}}


def test_nset_replace_existing_structure():
    data = {"a": {"b": {"c": 1}}}
    nset(data, ["a", "b"], "new_value")
    assert data == {"a": {"b": "new_value"}}


def test_nset_with_empty_string_key():
    data = {}
    nset(data, ["", ""], "value")
    assert data == {"": {"": "value"}}


@pytest.mark.parametrize(
    "indices",
    [
        ["a", [], "b"],
        ["a", {}, "b"],
    ],
)
def test_nset_with_invalid_index_types(indices):
    data = {}
    with pytest.raises(TypeError):
        nset(data, indices, "value")


def test_nset_with_float_indices():
    data = {}
    with pytest.raises(TypeError):
        nset(data, [1.5], "value")


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": [1, 2]}, ["a", 2], 3, {"a": [1, 2, 3]}),
        ({"a": {}}, ["a", "0"], "value", {"a": {"0": "value"}}),
    ],
)
def test_nset_string_integer_indices(initial, indices, value, expected):
    nset(initial, indices, value)
    assert initial == expected


def test_nset_with_defaultdict():
    from collections import defaultdict

    data = defaultdict(list)
    nset(data, ["key", 0], "value")
    assert data == {"key": ["value"]}


def test_nset_with_ordered_dict():
    from collections import OrderedDict

    data = OrderedDict()
    nset(data, ["a", "b", "c"], "value")
    assert list(data.keys()) == ["a"]
    assert data["a"]["b"]["c"] == "value"


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": []}, ["a", 0, "b", "c"], 2, {"a": [{"b": {"c": 2}}]}),
        ({}, ["a", 0, "b", 0, "c"], 2, {"a": [{"b": [{"c": 2}]}]}),
    ],
)
def test_nset_create_nested_structures(data, indices, value, expected):
    nset(data, indices, value)
    assert data == expected


def test_nset_with_generator():
    def gen():
        yield 1
        yield 2

    data = {"gen": gen()}
    with pytest.raises(TypeError):
        nset(data, ["gen", 0], 3)


def test_nset_with_bytes():
    data = b"hello"
    with pytest.raises(TypeError):
        nset(data, [5], ord("!"))


def test_nset_with_memoryview():
    data = memoryview(bytearray(b"hello"))
    with pytest.raises(TypeError):
        nset(data, [5], ord("!"))


def test_nset_with_circular_reference():
    data = {}
    data["self"] = data
    nset(data, ["self", "new_key"], "value")
    assert data["self"]["new_key"] == "value"
    assert data["self"]["self"]["new_key"] == "value"


def test_nset_with_complex_keys():
    data = {}
    complex_key = complex(1, 2)
    nset(data, [complex_key, "nested"], "value")
    assert data == {complex_key: {"nested": "value"}}


# File: tests/test_nset.py
