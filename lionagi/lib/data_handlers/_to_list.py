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
        input_ (Any): The input to convert to a list.
        flatten (bool, optional): If True, flattens nested lists. Defaults
            to True.
        dropna (bool, optional): If True, removes None values. Defaults to
            True.

    Returns:
        List[Any]: The converted list.

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


def flatten_list(lst_: List[Any], dropna: bool = True) -> List[Any]:
    """
    Flatten a nested list.

    Args:
        lst_ (List[Any]): The list to flatten.
        dropna (bool, optional): If True, removes None values. Defaults to
            True.

    Returns:
        List[Any]: The flattened list.

    Examples:
        >>> flatten_list([1, [2, 3], [4, [5, 6]]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten_list([1, None, 2], dropna=True)
        [1, 2]
    """
    flattened_list = list(_flatten_list_generator(lst_, dropna))
    return [i for i in flattened_list if i is not None] if dropna else flattened_list


def _flatten_list_generator(
    lst_: Iterable[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    A generator to recursively flatten a nested list.

    Args:
        lst_ (Iterable[Any]): The list to flatten.
        dropna (bool, optional): If True, removes None values. Defaults to
            True.

    Yields:
        Any: The next flattened element from the list.

    Examples:
        >>> list(_flatten_list_generator([1, [2, 3], [4, [5, 6]]]))
        [1, 2, 3, 4, 5, 6]
    """
    for i in lst_:
        if isinstance(i, Iterable) and not isinstance(
            i, (str, bytes, bytearray, Mapping)
        ):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i
