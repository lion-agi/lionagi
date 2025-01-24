# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lionagi.utils import to_list


def ninsert(
    nested_structure: dict[Any, Any] | list[Any],
    /,
    indices: list[str | int],
    value: Any,
    *,
    current_depth: int = 0,
) -> None:
    """
    Inserts a value into a nested structure at a specified path.

    Navigates a nested dictionary or list based on a sequence of indices or
    keys and inserts `value` at the final location. This method can create
    intermediate dictionaries or lists as needed.

    Args:
        nested_structure: The nested structure to modify.
        indices: The sequence of keys or indices defining the insertion path.
        value: The value to insert at the specified location.
        current_depth: Internal use only; tracks the current depth during
            recursive calls.

    Raises:
        ValueError: If the indices list is empty.
        TypeError: If an invalid key or container type is encountered.

    Examples:
        >>> subject_ = {'a': {'b': [1, 2]}}
        >>> ninsert(subject_, ['a', 'b', 2], 3)
        >>> assert subject_ == {'a': {'b': [1, 2, 3]}}

        >>> subject_ = []
        >>> ninsert(subject_, [0, 'a'], 1)
        >>> assert subject_ == [{'a': 1}]
    """
    if not indices:
        raise ValueError("Indices list cannot be empty")

    indices = to_list(indices)
    for i, part in enumerate(indices[:-1]):
        if isinstance(part, int):
            if isinstance(nested_structure, dict):
                raise TypeError(
                    f"Unsupported key type: {type(part).__name__}."
                    "Only string keys are acceptable.",
                )
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = indices[i + 1]
                nested_structure[part] = (
                    [] if isinstance(next_part, int) else {}
                )
        elif isinstance(nested_structure, dict):
            if part is None:
                raise TypeError("Cannot use NoneType as a key in a dictionary")
            if isinstance(part, (float, complex)):
                raise TypeError(
                    f"Unsupported key type: {type(part).__name__}."
                    "Only string keys are acceptable.",
                )
            if part not in nested_structure:
                next_part = indices[i + 1]
                nested_structure[part] = (
                    [] if isinstance(next_part, int) else {}
                )
        else:
            raise TypeError(
                f"Invalid container type: {type(nested_structure)} "
                "encountered during insertion"
            )

        nested_structure = nested_structure[part]
        current_depth += 1

    last_part = indices[-1]
    if isinstance(last_part, int):
        if isinstance(nested_structure, dict):
            raise TypeError(
                f"Unsupported key type: {type(last_part).__name__}."
                "Only string keys are acceptable.",
            )
        while len(nested_structure) <= last_part:
            nested_structure.append(None)
        nested_structure[last_part] = value
    elif isinstance(nested_structure, list):
        raise TypeError("Cannot use non-integer index on a list")
    else:
        if last_part is None:
            raise TypeError("Cannot use NoneType as a key in a dictionary")
        if isinstance(last_part, (float, complex)):
            raise TypeError(
                f"Unsupported key type: {type(last_part).__name__}."
                "Only string keys are acceptable.",
            )
        nested_structure[last_part] = value
