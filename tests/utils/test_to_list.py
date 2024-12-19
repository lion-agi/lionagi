from collections.abc import Mapping
from enum import Enum

import pytest
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from lionagi.utils.to_list import to_list  # Adjust import as needed
from lionagi.utils.undefined import UndefinedType  # Adjust import as needed

# Mock UNDEFINED for tests if needed, or use the one from your codebase
UNDEFINED = UndefinedType()


class SampleEnum(Enum):
    A = 1
    B = 2


class SampleModel(BaseModel):
    x: int


@pytest.mark.parametrize(
    "input_,expected",
    [
        (None, []),
        (UNDEFINED, []),
        (PydanticUndefined, []),
        ([], []),
        ([1, 2, 3], [1, 2, 3]),
        (1, [1]),
        ("string", ["string"]),
        (b"bytes", [b"bytes"]),
        (bytearray(b"abc"), [bytearray(b"abc")]),
    ],
)
def test_basic_conversions(input_, expected):
    assert to_list(input_) == expected


def test_flatten_lists():
    # Non-flatten
    assert to_list([1, [2, 3]]) == [1, [2, 3]]
    # Flatten
    assert to_list([1, [2, 3]], flatten=True) == [1, 2, 3]


def test_dropna():
    # dropna removes None and UNDEFINED
    input_ = [1, None, 2, UNDEFINED, 3, None]
    assert to_list(input_, dropna=True) == [1, 2, 3]


def test_unique_requires_flatten():
    with pytest.raises(ValueError):
        to_list([1, 2, 2], unique=True)  # unique=True requires flatten=True

    # unique with flatten
    assert to_list([1, [2, 2, 3], 1], flatten=True, unique=True) == [1, 2, 3]


def test_unique():
    # With flatten and unique
    assert to_list([[1, 1], [2, 2, 3, 3], 1], flatten=True, unique=True) == [
        1,
        2,
        3,
    ]


def test_strings_not_flattened():
    # Strings should not be flattened like lists
    assert to_list(["abc", "def"], flatten=True) == ["abc", "def"]
    # Flattening a list containing strings should leave strings as single units
    assert to_list(["abc", ["def", "ghi"]], flatten=True) == [
        "abc",
        "def",
        "ghi",
    ]


def test_bytes_not_flattened():
    # Bytes and bytearrays should be considered atomic
    assert to_list([b"bytes", bytearray(b"abc")], flatten=True) == [
        b"bytes",
        bytearray(b"abc"),
    ]


def test_enum():
    # If input_ is an Enum class and use_values=True, return enum values
    assert to_list(SampleEnum, use_values=True) == [1, 2]
    # Without use_values, return members as list
    expected_members = [member for member in SampleEnum]
    assert to_list(SampleEnum) == expected_members


def test_dict_handling():
    d = {"a": 1, "b": 2}
    # without use_values
    assert to_list(d) == [d]
    # with use_values
    assert to_list(d, use_values=True) == [1, 2]


def test_mapping_custom():
    class CustomMapping(Mapping):
        def __init__(self):
            self._data = {"key1": "val1", "key2": "val2"}

        def __getitem__(self, key):
            return self._data[key]

        def __iter__(self):
            return iter(self._data)

        def __len__(self):
            return len(self._data)

    cm = CustomMapping()
    assert to_list(cm) == [cm]
    assert to_list(cm, use_values=True) == ["val1", "val2"]


def test_iterables():
    # General iterable support
    gen = (x for x in range(3))  # generator
    assert to_list(gen) == [0, 1, 2]

    # Flatten nested iterables
    nested = [[0, 1], [2, 3], [4, [5, 6]]]
    assert to_list(nested, flatten=True) == [0, 1, 2, 3, 4, 5, 6]


def test_basemodel():
    m = SampleModel(x=10)
    assert to_list(m) == [m]


def test_complex_nested():
    data = [1, None, [2, [None, 3, [4, None]]], "string", UNDEFINED]
    # Flatten and dropna
    assert to_list(data, flatten=True, dropna=True) == [1, 2, 3, 4, "string"]
    # Flatten, dropna, unique
    data_with_dupes = [
        1,
        None,
        [2, 2, [None, 3, 3, [4, None, 4]]],
        "string",
        "string",
        UNDEFINED,
    ]
    assert to_list(
        data_with_dupes, flatten=True, dropna=True, unique=True
    ) == [1, 2, 3, 4, "string"]


def test_empty_input():
    # Empty inputs should return empty list
    assert to_list([]) == []
    # None after sanitization also returns empty
    assert to_list(None, dropna=True, flatten=True) == []


def test_mixed_types_flatten():
    # Flatten should handle mixed nested types gracefully
    mixed = [1, "abc", [b"bytes", bytearray(b"arr")], (x for x in [2, 3])]
    assert to_list(mixed, flatten=True) == [
        1,
        "abc",
        b"bytes",
        bytearray(b"arr"),
        2,
        3,
    ]


def test_no_modifications():
    # If no flatten, no dropna, no unique, input should be mostly unchanged (just listified)
    input_ = ((1, 2), "string", None, [3, 4], {"a", 1})
    result = to_list(input_)
    # since flatten=False and dropna=False, None and nested should remain
    assert result == [(1, 2), "string", None, [3, 4], {"a", 1}]


def test_flatten_behavior_nested_lists():
    nested = [[[1, 2]], 3, [4]]
    assert to_list(nested, flatten=True) == [1, 2, 3, 4]


def test_dropna_with_undefined():
    # If we had a specific UNDEFINED handling, ensure they are dropped when dropna=True
    data = [1, UNDEFINED, 2, None, 3]
    assert to_list(data, dropna=True) == [1, 2, 3]


def test_unique_without_flatten_raises():
    with pytest.raises(ValueError):
        to_list([1, 1], unique=True)


def test_unique_with_flatten():
    data = [[1], [1, 2, 2], [3, 3], [4]]
    assert to_list(data, flatten=True, unique=True) == [1, 2, 3, 4]


def test_unique_on_strings():
    data = ["abc", "abc", "def"]
    # no flatten needed for uniqueness if strings are top-level (flatten does not flatten strings)
    # but unique requires flatten=True by definition
    with pytest.raises(ValueError):
        to_list(data, unique=True)
    # With flatten=True
    assert to_list(data, flatten=True, unique=True) == ["abc", "def"]
