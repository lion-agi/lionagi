# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any


def nfilter(
    nested_structure: dict[Any, Any] | list[Any],
    /,
    condition: Callable[[Any], bool],
) -> dict[Any, Any] | list[Any]:
    """Filter elements in a nested structure based on a condition.

    Args:
        nested_structure: The nested structure (dict or list) to filter.
        condition: Function returning True for elements to keep, False to
            discard.

    Returns:
        The filtered nested structure.
    """
    if isinstance(nested_structure, dict):
        return _filter_dict(nested_structure, condition)
    elif isinstance(nested_structure, list):
        return _filter_list(nested_structure, condition)
    else:
        raise TypeError(
            "The nested_structure must be either a dict or a list."
        )


def _filter_dict(
    dictionary: dict[Any, Any], condition: Callable[[tuple[Any, Any]], bool]
) -> dict[Any, Any]:
    return {
        k: nfilter(v, condition) if isinstance(v, dict | list) else v
        for k, v in dictionary.items()
        if condition(v) or isinstance(v, dict | list)
    }


def _filter_list(
    lst: list[Any], condition: Callable[[Any], bool]
) -> list[Any]:
    return [
        nfilter(item, condition) if isinstance(item, dict | list) else item
        for item in lst
        if condition(item) or isinstance(item, dict | list)
    ]
