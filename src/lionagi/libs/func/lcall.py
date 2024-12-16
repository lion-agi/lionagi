from collections.abc import Callable
from typing import Any, TypeVar

from ..parse import to_list

T = TypeVar("T")


def lcall(
    input_: list[Any],
    func: Callable[..., T],
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    **kwargs,
) -> list[Any]:
    """Apply a function to each element of a list synchronously.

    Args:
        input_: List of inputs to be processed.
        func: Function to apply to each input element.
        flatten: If True, flatten the resulting list.
        dropna: If True, remove None values from the result.
        unique: If True, return only unique values (requires flatten=True).
        **kwargs: Additional keyword arguments passed to func.

    Returns:
        list[Any]: List of results after applying func to each input element.

    Raises:
        ValueError: If more than one function is provided.

    Examples:
        >>> lcall([1, 2, 3], lambda x: x * 2)
        [2, 4, 6]
        >>> lcall([[1, 2], [3, 4]], sum, flatten=True)
        [3, 7]
        >>> lcall([1, 2, 2, 3], lambda x: x, unique=True, flatten=True)
        [1, 2, 3]

    Note:
        The function uses to_list internally, which allows for flexible input
        types beyond just lists.
    """
    lst = to_list(input_)
    if len(to_list(func, flatten=True, dropna=True)) != 1:
        raise ValueError(
            "There must be one and only one function for list calling."
        )
    return to_list(
        [func(i, **kwargs) for i in lst],
        flatten=flatten,
        dropna=dropna,
        unique=unique,
    )
