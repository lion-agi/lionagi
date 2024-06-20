"""
Module for converting various input types into string representations.

Provides functions to convert a variety of data structures into strings,
with options for custom model dumping, stripping, and converting to
lowercase.

Functions:
    to_str: Convert the input to a string representation.
    _to_str: Helper function to convert the input to a string representation.
    strip_lower: Convert the input to a stripped and lowercase string 
                 representation.
"""

import json
from typing import Any
from .to_list import to_list
from .to_dict import to_dict


def to_str(
    input_: Any,
    /,
    use_model_dump: bool = True,
    strip_lower: bool = False,
    **kwargs: Any,
) -> str:
    """
    Convert the input to a string representation.

    If the input is a list, recursively converts each element to a string
    and joins them with a comma. If the input is a dictionary, converts it
    to a JSON string. If the input is a string, optionally strips and
    converts it to lowercase.

    Args:
        input_: The input to be converted to a string.
        use_model_dump: Whether to use a custom model dump function. 
                        Defaults to True.
        strip_lower: Whether to strip and convert the string to lowercase. 
                     Defaults to False.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        The string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.

    Examples:
        >>> to_str({"key": "value"})
        '{"key": "value"}'
        >>> to_str(["a", "b", "c"])
        'a, b, c'
        >>> to_str("   Example String   ", strip_lower=True)
        'example string'
    """
    if isinstance(input_, list):
        input_ = to_list(input_)
        return ", ".join(
            [
                to_str(
                    item,
                    use_model_dump=use_model_dump,
                    strip_lower=strip_lower,
                    **kwargs,
                )
                for item in input_
            ]
        )

    return _to_str(
        input_,
        use_model_dump=use_model_dump,
        strip_lower=strip_lower,
        **kwargs
    )


def _to_str(
    input_: Any,
    /,
    use_model_dump: bool = None,
    strip_lower: bool = None,
    **kwargs: Any,
) -> str:
    """
    Helper function to convert the input to a string representation.

    Args:
        input_: The input to be converted to a string.
        use_model_dump: Whether to use a custom model dump function. 
                        Defaults to None.
        strip_lower: Whether to strip and convert the string to lowercase. 
                     Defaults to None.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        The string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.

    Examples:
        >>> _to_str({"key": "value"})
        '{"key": "value"}'
        >>> _to_str("   Example String   ", strip_lower=True)
        'example string'
    """
    if isinstance(input_, dict):
        input_ = json.dumps(input_, **kwargs)

    if isinstance(input_, str):
        return input_.strip().lower() if strip_lower else input_

    try:
        dict_ = to_dict(input_, as_list=False, use_model_dump=use_model_dump)
        return (
            json.dumps(dict_, **kwargs).strip().lower()
            if strip_lower
            else json.dumps(dict_, **kwargs)
        )
    except Exception:
        try:
            return str(input_).strip().lower() if strip_lower else str(input_)
        except Exception as e:
            raise ValueError(
                f"Could not convert input_ to string: {input_}, Error: {e}"
            )


def strip_lower(input_: str, /, **kwargs: Any) -> str:
    """
    Convert the input to a stripped and lowercase string representation.

    Args:
        input_: The input string to be processed.
        **kwargs: Additional keyword arguments to pass to to_str.

    Returns:
        The stripped and lowercase string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a string.

    Examples:
        >>> strip_lower("   Example String   ")
        'example string'
    """
    try:
        return to_str(input_, strip_lower=True, **kwargs)
    except Exception as e:
        raise ValueError(
            f"Could not convert input_ to string: {input_}, Error: {e}"
        )