from collections.abc import Mapping
from typing import Any, Generator, Iterable, List


def to_list(input_: Any, /, *, flatten: bool = True, dropna: bool = True) -> List[Any]:
    """
    Convert various types of input into a list.

    Args:
        input_ (Any): The input to convert to a list.
        flatten (bool, optional): If True, flattens nested lists. Defaults to
            True.
        dropna (bool, optional): If True, removes None values. Defaults to
            True.

    Returns:
        List[Any]: The converted list.
    """
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
    """
    flattened_list = list(_flatten_list_generator(lst_, dropna))
    return [i for i in flattened_list if i is not None] if dropna else flattened_list


def _flatten_list_generator(
    lst_: List[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    A generator to recursively flatten a nested list.

    Args:
        lst_ (List[Any]): The list to flatten.
        dropna (bool, optional): If True, removes None values. Defaults to
            True.

    Yields:
        Any: The next flattened element from the list.
    """
    for i in lst_:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i
