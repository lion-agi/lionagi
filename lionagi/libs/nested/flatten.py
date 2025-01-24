# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections import deque
from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypeVar, overload

T = TypeVar("T")


@overload
def flatten(
    nested_structure: T,
    /,
    *,
    parent_key: tuple = (),
    sep: str = "|",
    coerce_keys: Literal[True] = True,
    dynamic: bool = True,
    coerce_sequence: Literal["dict", None] = None,
    max_depth: int | None = None,
) -> dict[str, Any] | None: ...


@overload
def flatten(
    nested_structure: T,
    /,
    *,
    parent_key: tuple = (),
    sep: str = "|",
    coerce_keys: Literal[False],
    dynamic: bool = True,
    coerce_sequence: Literal["dict", "list", None] = None,
    max_depth: int | None = None,
) -> dict[tuple, Any] | None: ...


def flatten(
    nested_structure: Any,
    /,
    *,
    parent_key: tuple = (),
    sep: str = "|",
    coerce_keys: bool = True,
    dynamic: bool = True,
    coerce_sequence: Literal["dict", "list"] | None = None,
    max_depth: int | None = None,
) -> dict[tuple | str, Any] | None:
    """Flatten a nested structure into a single-level dictionary.

    Recursively traverses the input, creating keys that represent the path
    to each value in the flattened result.

    Args:
        nested_structure: The nested structure to flatten.
        parent_key: Base key for the current recursion level. Default: ().
        sep: Separator for joining keys. Default: "|".
        coerce_keys: Join keys into strings if True, keep as tuples if False.
            Default: True.
        dynamic: Handle sequences (except strings) dynamically if True.
            Default: True.
        coerce_sequence: Force sequences to be treated as dicts or lists.
            Options: "dict", "list", or None. Default: None.
        max_depth: Maximum depth to flatten. None for complete flattening.
            Default: None.

    Returns:
        A flattened dictionary with keys as tuples or strings (based on
        coerce_keys) representing the path to each value.

    Raises:
        ValueError: If coerce_sequence is "list" and coerce_keys is True.

    Example:
        >>> nested = {"a": 1, "b": {"c": 2, "d": [3, 4]}}
        >>> flatten(nested)
        {'a': 1, 'b|c': 2, 'b|d|0': 3, 'b|d|1': 4}

    Note:
        - Preserves order of keys in dicts and indices in sequences.
        - With dynamic=True, treats sequences (except strings) as nestable.
        - coerce_sequence allows forcing sequence handling for homogeneity.
    """

    if coerce_keys and coerce_sequence == "list":
        raise ValueError(
            "coerce_sequence cannot be 'list' when coerce_keys is True"
        )

    coerce_sequence_to_list = None
    coerce_sequence_to_dict = None

    if dynamic and coerce_sequence:
        if coerce_sequence == "dict":
            coerce_sequence_to_dict = True
        elif coerce_sequence == "list":
            coerce_sequence_to_list = True

    return _flatten_iterative(
        obj=nested_structure,
        parent_key=parent_key,
        sep=sep,
        coerce_keys=coerce_keys,
        dynamic=dynamic,
        coerce_sequence_to_list=coerce_sequence_to_list,
        coerce_sequence_to_dict=coerce_sequence_to_dict,
        max_depth=max_depth,
    )


def _flatten_iterative(
    obj: Any,
    parent_key: tuple,
    sep: str,
    coerce_keys: bool,
    dynamic: bool,
    coerce_sequence_to_list: bool = False,
    coerce_sequence_to_dict: bool = False,
    max_depth: int | None = None,
) -> dict[tuple | str, Any]:
    stack = deque([(obj, parent_key, 0)])
    result = {}

    while stack:
        current_obj, current_key, depth = stack.pop()

        if max_depth is not None and depth >= max_depth:
            result[_format_key(current_key, sep, coerce_keys)] = current_obj
            continue

        if isinstance(current_obj, Mapping):
            for k, v in current_obj.items():
                new_key = current_key + (k,)
                if (
                    v
                    and isinstance(v, (Mapping, Sequence))
                    and not isinstance(v, (str, bytes, bytearray))
                ):
                    stack.appendleft((v, new_key, depth + 1))
                else:
                    result[_format_key(new_key, sep, coerce_keys)] = v

        elif (
            dynamic
            and isinstance(current_obj, Sequence)
            and not isinstance(current_obj, (str, bytes, bytearray))
        ):
            if coerce_sequence_to_dict:
                dict_obj = {str(i): v for i, v in enumerate(current_obj)}
                for k, v in dict_obj.items():
                    new_key = current_key + (k,)
                    stack.appendleft((v, new_key, depth + 1))
            elif coerce_sequence_to_list:
                for i, v in enumerate(current_obj):
                    new_key = current_key + (i,)
                    stack.appendleft((v, new_key, depth + 1))
            else:
                for i, v in enumerate(current_obj):
                    new_key = current_key + (str(i),)
                    stack.appendleft((v, new_key, depth + 1))
        else:
            result[_format_key(current_key, sep, coerce_keys)] = current_obj

    return result


def _format_key(key: tuple, sep: str, coerce_keys: bool, /) -> tuple | str:
    if not key:
        return key
    return sep.join(map(str, key)) if coerce_keys else key
