"""
Module for inserting values into nested structures.

Provides functionality to insert values into nested dictionaries or lists at
specified paths, with support for creating intermediate structures as needed.

Functions:
    ninsert: Inserts a value into a nested structure at a specified path.
    handle_list_insert: Ensures a specified index in a list is occupied by a
                        given value, extending the list if necessary.
"""

from lionagi.os.libs.data_handlers._to_list import to_list
from typing import Any, Union


def ninsert(
    nested_structure: Union[dict, list],
    indices: list[Union[str, int]],
    value: Any,
    *,
    sep: str = "|",
    max_depth: Union[int, None] = None,
    current_depth: int = 0,
) -> None:
    """
    Inserts a value into a nested structure at a specified path.

    Navigates a nested dictionary or list based on a sequence of indices or keys
    (`indices`) and inserts `value` at the final location. This method can create
    intermediate dictionaries or lists as needed.

    Args:
        nested_structure (dict | list): The nested structure to modify.
        indices (list[str | int]): The sequence of keys (str for dicts) or
            indices (int for lists) defining the path to the insertion point.
        value (Any): The value to insert at the specified location within
            `nested_structure`.
        sep (str): A separator used when concatenating indices to form
            composite keys in case of ambiguity. Defaults to "|".
        max_depth (int | None): Limits the depth of insertion. If `None`,
            no limit is applied.
        current_depth (int): Internal use only; tracks the current depth
            during recursive calls.

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

    if isinstance(indices, str):
        indices = indices.split(sep)
    indices = to_list(indices)
    for i, part in enumerate(indices[:-1]):
        if max_depth is not None and current_depth >= max_depth:
            break

        if isinstance(part, int):
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = indices[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
        elif isinstance(nested_structure, dict):
            if part not in nested_structure:
                next_part = indices[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
        else:
            raise TypeError("Invalid container type encountered during insertion")

        nested_structure = nested_structure[part]
        current_depth += 1

    last_part = indices[-1]
    if max_depth is not None and current_depth >= max_depth:
        if isinstance(last_part, int):
            handle_list_insert(nested_structure, last_part, value)
        elif isinstance(nested_structure, list):
            raise TypeError("Cannot use non-integer index on a list")
        else:
            nested_structure[last_part] = value
    else:
        if isinstance(last_part, int):
            handle_list_insert(nested_structure, last_part, value)
        elif isinstance(nested_structure, list):
            raise TypeError("Cannot use non-integer index on a list")
        else:
            nested_structure[last_part] = value


def handle_list_insert(nested_structure: list, part: int, value: Any) -> None:
    """
    Ensures a specified index in a list is occupied by a given value, extending the
    list if necessary.

    This method modifies a list by inserting or replacing an element at a specified
    index. If the index is beyond the current list size, the list is extended with
    `None` values up to the index, then the specified value is inserted.

    Args:
        nested_structure: The list to modify.
        part: The target index for inserting or replacing the value.
        value: The value to be inserted or to replace an existing value in the list.

    Note:
        This function directly modifies the input list in place.
    """
    while len(nested_structure) <= part:
        nested_structure.append(None)
    nested_structure[part] = value
