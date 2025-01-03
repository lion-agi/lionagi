import pytest

from lionagi.libs.nested.ninsert import ninsert


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": {"b": [1, 2]}}, ["a", "b", 2], 3, {"a": {"b": [1, 2, 3]}}),
        ([1, [2, 3]], [1, 2], 4, [1, [2, 3, 4]]),
        ({"a": [1, {"b": 2}]}, ["a", 1, "c"], 3, {"a": [1, {"b": 2, "c": 3}]}),
        ({}, ["a", "b", "c"], 1, {"a": {"b": {"c": 1}}}),
        ({"a": {"b": 2}}, ["a", "b"], 3, {"a": {"b": 3}}),
        (
            {"a": {"b": [1, 2]}},
            ["a", "b", 5],
            3,
            {"a": {"b": [1, 2, None, None, None, 3]}},
        ),
        ([], [0, "a"], 1, [{"a": 1}]),
        ({"a": []}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_ninsert_valid_cases(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_empty_indices():
    data = {"a": 1}
    with pytest.raises(ValueError, match="Indices list cannot be empty"):
        ninsert(data, [], 2)


@pytest.mark.parametrize(
    "data, indices, value",
    [
        ([1, 2, 3], ["a"], 4),
        ({"a": 1}, [0], 2),
        ({"a": {"b": 2}}, ["a", "b", "c"], 3),
    ],
)
def test_ninsert_type_errors(data, indices, value):
    with pytest.raises(TypeError):
        ninsert(data, indices, value)


def test_ninsert_nested_creation():
    data = {}
    ninsert(data, ["a", 0, "b", 1, "c"], 42)
    assert data == {"a": [{"b": [None, {"c": 42}]}]}


def test_ninsert_overwrite_existing():
    data = {"a": {"b": {"c": 1}}}
    ninsert(data, ["a", "b", "c"], 2)
    assert data == {"a": {"b": {"c": 2}}}


def test_ninsert_extend_list():
    data = {"a": [1, 2]}
    ninsert(data, ["a", 5], 3)
    assert data == {"a": [1, 2, None, None, None, 3]}


def test_ninsert_with_tuple():
    data = {"a": (1, 2)}
    with pytest.raises(AttributeError):
        ninsert(data, ["a", 2], 3)


def test_ninsert_with_set():
    data = {"a": {1, 2}}
    with pytest.raises(AttributeError):
        ninsert(data, ["a", 3], 3)


def test_ninsert_with_large_nested_structure():
    data = {}
    for i in range(1000):
        ninsert(data, ["level" + str(i)], i)
    assert data["level999"] == 999


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": 1}, ["b", "c"], 2, {"a": 1, "b": {"c": 2}}),
        ([1, 2], [2, "a"], 3, [1, 2, {"a": 3}]),
        ({}, ["a", 0, "b"], 1, {"a": [{"b": 1}]}),
    ],
)
def test_ninsert_create_intermediate_structures(
    data, indices, value, expected
):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_with_string_key_for_list():
    data = [1, 2, 3]
    with pytest.raises(TypeError):
        ninsert(data, ["key"], 4)


def test_ninsert_replace_primitive_with_dict():
    data = {"a": 1}
    with pytest.raises(TypeError):
        ninsert(data, ["a", "b"], 2)


def test_ninsert_replace_primitive_with_list():
    data = {"a": 1}
    with pytest.raises(TypeError):
        ninsert(data, ["a", 0], 2)


@pytest.mark.parametrize(
    "initial, indices, value, expected",
    [
        ({"a": 1}, ["b", 0, "c"], 2, {"a": 1, "b": [{"c": 2}]}),
        ([], [0, "a", 0, "b"], 1, [{"a": [{"b": 1}]}]),
        ({}, ["a", 0, "b", 0, "c"], 1, {"a": [{"b": [{"c": 1}]}]}),
    ],
)
def test_ninsert_deep_nested_creation(initial, indices, value, expected):
    ninsert(initial, indices, value)
    assert initial == expected


def test_ninsert_with_duplicate_indices():
    data = {}
    ninsert(data, ["a", "a", "a"], "value")
    assert data == {"a": {"a": {"a": "value"}}}


def test_ninsert_replace_existing_structure():
    data = {"a": {"b": {"c": 1}}}
    ninsert(data, ["a", "b"], "new_value")
    assert data == {"a": {"b": "new_value"}}


def test_ninsert_with_empty_string_key():
    data = {}
    ninsert(data, ["", ""], "value")
    assert data == {"": {"": "value"}}


@pytest.mark.parametrize(
    "indices",
    [
        ["a", None, "b"],
        ["a", [], "b"],
        ["a", {}, "b"],
    ],
)
def test_ninsert_with_invalid_index_types(indices):
    data = {}
    with pytest.raises(TypeError):
        ninsert(data, indices, "value")


def test_ninsert_with_boolean_indices():
    data = {}
    with pytest.raises(TypeError):
        ninsert(data, [True, False], "value")


def test_ninsert_with_float_indices():
    data = {}
    with pytest.raises(expected_exception=TypeError):
        ninsert(data, [1.5], "value")


def test_ninsert_with_property():
    class PropTest:
        @property
        def prop(self):
            return {}

    data = {"obj": PropTest()}
    with pytest.raises(TypeError):
        ninsert(data, ["obj", "prop", "new_key"], "value")


def test_ninsert_with_defaultdict():
    from collections import defaultdict

    data = defaultdict(list)
    ninsert(data, ["key", 0], "value")
    assert data == {"key": ["value"]}


def test_ninsert_with_ordered_dict():
    from collections import OrderedDict

    data = OrderedDict()
    ninsert(data, ["a", "b", "c"], "value")
    assert list(data.keys()) == ["a"]
    assert data["a"]["b"]["c"] == "value"


@pytest.mark.parametrize(
    "data, indices, value, expected",
    [
        ({"a": []}, ["a", 0, "b", "c"], 2, {"a": [{"b": {"c": 2}}]}),
        ({}, ["a", 0, "b", 0, "c"], 2, {"a": [{"b": [{"c": 2}]}]}),
    ],
)
def test_ninsert_create_nested_structures(data, indices, value, expected):
    ninsert(data, indices, value)
    assert data == expected


def test_ninsert_with_generator():
    def gen():
        yield 1
        yield 2

    data = {"gen": gen()}
    with pytest.raises(TypeError):
        ninsert(data, ["gen", 0], 3)


def test_ninsert_with_memoryview():
    data = memoryview(bytearray(b"hello"))
    with pytest.raises(AttributeError):
        ninsert(data, [5], ord("!"))


def test_ninsert_with_circular_reference():
    data = {}
    data["self"] = data
    ninsert(data, ["self", "new_key"], "value")
    assert data["self"]["new_key"] == "value"
    assert data["self"]["self"]["new_key"] == "value"


# File: tests/test_ninsert.py
