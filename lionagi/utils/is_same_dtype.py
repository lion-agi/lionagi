from collections.abc import Mapping
from typing import Any, TypeVar

T = TypeVar("T")


def is_same_dtype(
    input_: list[T] | dict[Any, T],
    dtype: type | None = None,
    return_dtype: bool = False,
) -> bool | tuple[bool, type | None]:
    """Check if all elements in the input have the same data type.

    Args:
        input_ (list|dict): The input collection (list or dict) to check.
        dtype (type|None): If provided, checks if all elements are instances of this type.
                           Otherwise, deduces the type from the first element.
        return_dtype (bool): If True, returns a tuple of (bool, type).

    Returns:
        bool or tuple[bool, type|None]: A boolean indicating if all elements have the same
        type. If return_dtype=True, also returns the determined type or None if input is empty.
    """
    if not input_:
        # If empty, trivially true. dtype is None since no elements exist.
        return (True, None) if return_dtype else True

    if isinstance(input_, Mapping):
        # For dictionaries, use values
        values_iter = iter(input_.values())
        first_val = next(values_iter, None)
        if dtype is None:
            dtype = type(first_val) if first_val is not None else None
        # Check the first element
        result = (dtype is None or isinstance(first_val, dtype)) and all(
            isinstance(v, dtype) for v in values_iter
        )
    else:
        # For lists (or list-like), directly access the first element
        first_val = input_[0]
        if dtype is None:
            dtype = type(first_val) if first_val is not None else None
        # Check all elements including the first
        result = all(isinstance(e, dtype) for e in input_)

    return (result, dtype) if return_dtype else result
