"""
This module provides a function to filter elements in a nested structure
(dictionary or list) based on a given condition.

Functions:
- nfilter: Filter elements in a nested structure (dict or list) based on a
  condition.
- _filter_dict: Filter elements in a dictionary based on a condition.
- _filter_list: Filter elements in a list based on a condition.
"""

from typing import Any, Callable, Union


def nfilter(
    nested_structure: Union[dict, list], /, condition: Callable[[Any], bool]
) -> Union[dict, list]:
    """
    Filter elements in a nested structure (dict or list) based on a condition.

    Args:
        nested_structure (dict | list): The nested structure to filter.
        condition (Callable[[Any], bool]): A function that returns True for
            elements to keep and False for elements to discard.

    Returns:
        dict | list: The filtered nested structure.

    Raises:
        TypeError: If nested_structure is not a dict or list.
    """
    if isinstance(nested_structure, dict):
        return _filter_dict(nested_structure, condition)
    elif isinstance(nested_structure, list):
        return _filter_list(nested_structure, condition)
    else:
        raise TypeError("The nested_structure must be either a dict or a list.")


def _filter_dict(
    dictionary: dict[Any, Any], condition: Callable[[tuple[Any, Any]], bool]
) -> dict[Any, Any]:
    """
    Filter elements in a dictionary based on a condition.

    Args:
        dictionary (dict[Any, Any]): The dictionary to filter.
        condition (Callable[[tuple[Any, Any]], bool]): A function that
            returns True for key-value pairs to keep and False for key-value
            pairs to discard.

    Returns:
        dict[Any, Any]: The filtered dictionary.
    """
    return {k: v for k, v in dictionary.items() if condition((k, v))}


def _filter_list(lst: list[Any], condition: Callable[[Any], bool]) -> list[Any]:
    """
    Filter elements in a list based on a condition.

    Args:
        lst (list[Any]): The list to filter.
        condition (Callable[[Any], bool]): A function that returns True for
            elements to keep and False for elements to discard.

    Returns:
        list[Any]: The filtered list.
    """
    return [item for item in lst if condition(item)]
