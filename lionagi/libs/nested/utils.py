# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lionagi.utils import UNDEFINED


def is_homogeneous(
    iterables: list[Any] | dict[Any, Any], type_check: type | tuple[type, ...]
) -> bool:
    """
    Check if all elements in a list or all values in a dict are of same type.

    Args:
        iterables: The list or dictionary to check.
        type_check: The type to check against.

    Returns:
        True if all elements/values are of the same type, False otherwise.
    """
    if isinstance(iterables, list):
        return all(isinstance(it, type_check) for it in iterables)

    elif isinstance(iterables, dict):
        return all(isinstance(val, type_check) for val in iterables.values())

    else:
        return isinstance(iterables, type_check)


def is_same_dtype(
    input_: list[Any] | dict[Any, Any],
    dtype: type | None = None,
    return_dtype: bool = False,
) -> bool | tuple[bool, type | None]:
    """
    Check if all elements in a list or dict values are of the same data type.

    Args:
        input_: The input list or dictionary to check.
        dtype: The data type to check against. If None, uses the type of the
            first element.
        return_dtype: If True, return the data type with the check result.

    Returns:
        If return_dtype is False, returns True if all elements are of the
        same type (or if the input is empty), False otherwise.
        If return_dtype is True, returns a tuple (bool, type | None).
    """
    if not input_:
        return True

    iterable = input_.values() if isinstance(input_, dict) else input_
    first_element_type = type(next(iter(iterable), None))

    dtype = dtype or first_element_type

    result = all(isinstance(element, dtype) for element in iterable)
    return (result, dtype) if return_dtype else result


def is_structure_homogeneous(
    structure: Any, return_structure_type: bool = False
) -> bool | tuple[bool, type | None]:
    """
    Check if a nested structure is homogeneous (no mix of lists and dicts).

    Args:
        structure: The nested structure to check.
        return_structure_type: If True, return the type of the homogeneous
            structure.

    Returns:
        If return_structure_type is False, returns True if the structure is
        homogeneous, False otherwise.
        If True, returns a tuple (bool, type | None).

    Examples:
        >>> is_structure_homogeneous({'a': {'b': 1}, 'c': {'d': 2}})
        True
        >>> is_structure_homogeneous({'a': {'b': 1}, 'c': [1, 2]})
        False
    """

    def _check_structure(substructure):
        structure_type = None
        if isinstance(substructure, list):
            structure_type = list
            for item in substructure:
                if not isinstance(item, structure_type) and isinstance(
                    item, list | dict
                ):
                    return False, None
                result, _ = _check_structure(item)
                if not result:
                    return False, None
        elif isinstance(substructure, dict):
            structure_type = dict
            for item in substructure.values():
                if not isinstance(item, structure_type) and isinstance(
                    item, list | dict
                ):
                    return False, None
                result, _ = _check_structure(item)
                if not result:
                    return False, None
        return True, structure_type

    is_homogeneous, structure_type = _check_structure(structure)
    return (
        (is_homogeneous, structure_type)
        if return_structure_type
        else is_homogeneous
    )


def deep_update(
    original: dict[Any, Any], update: dict[Any, Any]
) -> dict[Any, Any]:
    """
    Recursively merge two dicts, updating nested dicts instead of overwriting.

    Args:
        original: The dictionary to update.
        update: The dictionary containing updates to apply to `original`.

    Returns:
        The `original` dictionary after applying updates from `update`.

    Note:
        This method modifies the `original` dictionary in place.
    """
    for key, value in update.items():
        if isinstance(value, dict) and key in original:
            original[key] = deep_update(original.get(key, {}), value)
        else:
            original[key] = value
    return original


def get_target_container(
    nested: list[Any] | dict[Any, Any], indices: list[int | str]
) -> list[Any] | dict[Any, Any]:
    """
    Retrieve the target container in a nested structure using indices.

    Args:
        nested: The nested structure to navigate.
        indices: A list of indices to navigate through the nested structure.

    Returns:
        The target container at the specified path.

    Raises:
        IndexError: If a list index is out of range.
        KeyError: If a dictionary key is not found.
        TypeError: If the current element is neither a list nor a dictionary.
    """
    current_element = nested
    for index in indices:
        if isinstance(current_element, list):
            if isinstance(index, str) and index.isdigit():
                index = int(index)

            if isinstance(index, int) and 0 <= index < len(current_element):
                current_element = current_element[index]

            else:
                raise IndexError("List index is invalid or out of range")

        elif isinstance(current_element, dict):
            if index in current_element:
                current_element = current_element.get(index, None)
            else:
                raise KeyError("Key not found in dictionary")
        else:
            raise TypeError(
                "Current element is neither a list nor a dictionary"
            )
    return current_element


def ensure_list_index(
    lst: list[Any], index: int, default: Any = UNDEFINED
) -> None:
    while len(lst) <= index:
        lst.append(default if default is not UNDEFINED else None)
