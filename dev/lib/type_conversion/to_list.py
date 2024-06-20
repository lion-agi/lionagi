"""
Module for converting various input types into lists.

Provides functions to convert a variety of data structures into lists,
with options for flattening nested lists and removing None values.

Functions:
    to_list: Convert various types of input into a list.
    flatten_list: Flatten a nested list.
    _flatten_list_generator: A generator to recursively flatten a nested list.
"""

from collections.abc import Mapping, Iterable
from typing import Any, Generator, List


def to_list(input_: Any, /, *, flatten: bool = True, dropna: bool = True) -> List[Any]:
    """
    Convert various types of input into a list.

    Args:
        input_: The input to convert to a list.
        flatten: If True, flattens nested lists. Defaults to True.
        dropna: If True, removes None values. Defaults to True.

    Returns:
        The converted list.

    Examples:
        >>> to_list(1)
        [1]
        >>> to_list([1, 2, [3, 4]], flatten=True)
        [1, 2, 3, 4]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
    """
    if input_ is None:
        return []

    if not isinstance(input_, Iterable) or isinstance(
        input_, (str, bytes, bytearray, Mapping)
    ):
        return [input_]

    iterable_list = list(input_) if not isinstance(input_, list) else input_

    return flatten_list(iterable_list, dropna) if flatten else iterable_list


def flatten_list(lst: List[Any], dropna: bool = True) -> List[Any]:
    """
    Flatten a nested list.

    Args:
        lst: The list to flatten.
        dropna: If True, removes None values. Defaults to True.

    Returns:
        The flattened list.

    Examples:
        >>> flatten_list([1, [2, 3], [4, [5, 6]]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten_list([1, None, 2], dropna=True)
        [1, 2]
    """
    flattened_list = list(_flatten_list_generator(lst, dropna))
    return [i for i in flattened_list if i is not None] if dropna else flattened_list


def _flatten_list_generator(
    lst: Iterable[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    A generator to recursively flatten a nested list.

    Args:
        lst: The list to flatten.
        dropna: If True, removes None values. Defaults to True.

    Yields:
        The next flattened element from the list.

    Examples:
        >>> list(_flatten_list_generator([1, [2, 3], [4, [5, 6]]]))
        [1, 2, 3, 4, 5, 6]
    """
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(
            item, (str, bytes, bytearray, Mapping)
        ):
            yield from _flatten_list_generator(item, dropna)
        else:
            yield item
            
         
import unittest
import numpy as np   
            


class TestToListFunction(unittest.TestCase):

    def test_single_non_iterable(self):
        self.assertEqual(to_list(5), [5])
        self.assertEqual(to_list("test"), ["test"])
        self.assertEqual(to_list(b"bytes"), [b"bytes"])

    def test_iterables(self):
        self.assertEqual(to_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(to_list((1, 2, 3)), [1, 2, 3])
        self.assertEqual(to_list({1, 2, 3}), [1, 2, 3])

    def test_nested_lists(self):
        self.assertEqual(to_list([1, [2, 3], [[4], 5]]), [1, 2, 3, 4, 5])
        self.assertEqual(to_list([1, [2, None], [[4], 5]], dropna=True), [1, 2, 4, 5])
        self.assertEqual(
            to_list([1, [2, None], [[4], 5]], dropna=False), [1, 2, None, 4, 5]
        )

    def test_non_flatten(self):
        self.assertEqual(
            to_list([1, [2, 3], [[4], 5]], flatten=False), [1, [2, 3], [[4], 5]]
        )

    def test_mappings(self):
        self.assertEqual(to_list({"a": 1, "b": 2}), [{"a": 1, "b": 2}])

    def test_empty_input(self):
        self.assertEqual(to_list([]), [])
        self.assertEqual(to_list(None), [])
        self.assertEqual(to_list([None]), [])

    def test_mixed_inputs(self):
        self.assertEqual(
            to_list([1, "string", [3, b"bytes"], None]), [1, "string", 3, b"bytes"]
        )

    def test_nested_tuples(self):
        self.assertEqual(to_list((1, (2, 3), ((4,), 5))), [1, 2, 3, 4, 5])

    def test_set_with_none(self):
        self.assertEqual(to_list({1, 2, None}), [1, 2])
        self.assertEqual(to_list({1, 2, None}, dropna=False), [None, 1, 2])

    def test_generator(self):
        def gen():
            yield 1
            yield 2
            yield 3

        self.assertEqual(to_list(gen()), [1, 2, 3])

    def test_deeply_nested_lists(self):
        nested_list = [1, [2, [3, [4, [5, [6, [7, [8, [9, [10]]]]]]]]]]
        self.assertEqual(to_list(nested_list), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_mixed_iterables(self):
        mixed_iterables = [1, (2, 3), {4, 5}, [[6, 7], 8]]
        self.assertEqual(to_list(mixed_iterables), [1, 2, 3, 4, 5, 6, 7, 8])

    def test_dict_with_iterable_values(self):
        dict_iterables = {"a": [1, 2], "b": (3, 4), "c": {5, 6}}
        self.assertEqual(
            to_list(dict_iterables), [{"a": [1, 2], "b": (3, 4), "c": {5, 6}}]
        )

    def test_nested_empty_lists(self):
        self.assertEqual(to_list([[], [[]], [[[]]]]), [])

    def test_edge_case_strings(self):
        self.assertEqual(to_list(""), [""])
        self.assertEqual(to_list(" "), [" "])
        self.assertEqual(to_list(["", " "]), ["", " "])

    def test_numpy_array(self):
        np_array = np.array([1, 2, 3])
        self.assertEqual(to_list(np_array), [1, 2, 3])

    def test_custom_iterable_class(self):
        class CustomIterable:
            def __iter__(self):
                yield 1
                yield 2
                yield 3

        self.assertEqual(to_list(CustomIterable()), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()