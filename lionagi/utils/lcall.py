from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from .to_list import to_list

T = TypeVar("T")
R = TypeVar("R")


def lcall(
    input_: Iterable[T] | T,
    func: Callable[[T], R] | Iterable[Callable[[T], R]],
    /,
    *args: Any,
    sanitize_input: bool = False,
    unique_input: bool = False,
    flatten: bool = False,
    dropna: bool = False,
    unique_output: bool = False,
    flatten_tuple_set: bool = False,
    **kwargs: Any,
) -> list[R]:
    """Apply function to each element in input list with optional processing.

    Maps a function over input elements and processes results. Can sanitize input
    and output using various filtering options.

    Args:
        input_: Single item or iterable to process.
        func: Function to apply or single-item iterable containing function.
        *args: Additional positional arguments passed to func.
        sanitize_input: If True, sanitize input using to_list.
        unique_input: If True with sanitize_input, remove input duplicates.
        flatten: If True, flatten output nested structures.
        dropna: If True, remove None values from output.
        unique_output: If True with flatten/dropna, remove output duplicates.
        flatten_tuple_set: If True, flatten tuples and sets.
        **kwargs: Additional keyword arguments passed to func.

    Returns:
        list: Results of applying func to each input element.

    Raises:
        ValueError: If func is not callable or unique_output used incorrectly.
        TypeError: If func or input processing fails.

    Examples:
        >>> lcall([1, 2, 3], str)
        ['1', '2', '3']
        >>> lcall([1, [2, 3]], str, flatten=True)
        ['1', '2', '3']
    """
    # Validate and extract callable function
    if not callable(func):
        try:
            func_list = list(func)
            if len(func_list) != 1 or not callable(func_list[0]):
                raise ValueError(
                    "func must contain exactly one callable function."
                )
            func = func_list[0]
        except TypeError as e:
            raise ValueError(
                "func must be callable or iterable with one callable."
            ) from e

    # Process input based on sanitization flag
    if sanitize_input:
        input_ = to_list(
            input_,
            flatten=True,
            dropna=True,
            unique=unique_input,
            flatten_tuple_set=flatten_tuple_set,
        )
    else:
        if not isinstance(input_, list):
            try:
                input_ = list(input_)
            except TypeError:
                input_ = [input_]

    # Validate output processing options
    if unique_output and not (flatten or dropna):
        raise ValueError(
            "unique_output requires flatten or dropna for post-processing."
        )

    # Process elements and collect results
    out = []
    append = out.append

    for item in input_:
        try:
            result = func(item, *args, **kwargs)
            append(result)
        except InterruptedError:
            return out
        except Exception:
            raise

    # Apply output processing if requested
    if flatten or dropna:
        out = to_list(
            out,
            flatten=flatten,
            dropna=dropna,
            unique=unique_output,
            flatten_tuple_set=flatten_tuple_set,
        )

    return out
