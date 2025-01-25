# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections import defaultdict
from collections.abc import Callable, Sequence
from itertools import chain
from typing import Any

from .utils import is_homogeneous


def nmerge(
    nested_structure: Sequence[dict[str, Any] | list[Any]],
    /,
    *,
    overwrite: bool = False,
    dict_sequence: bool = False,
    sort_list: bool = False,
    custom_sort: Callable[[Any], Any] | None = None,
) -> dict[str, Any] | list[Any]:
    """
    Merge multiple dictionaries, lists, or sequences into a unified structure.

    Args:
        nested_structure: A sequence containing dictionaries, lists, or other
            iterable objects to merge.
        overwrite: If True, overwrite existing keys in dictionaries with
            those from subsequent dictionaries.
        dict_sequence: Enables unique key generation for duplicate keys by
            appending a sequence number. Applicable only if `overwrite` is
            False.
        sort_list: When True, sort the resulting list after merging. It does
            not affect dictionaries.
        custom_sort: An optional callable that defines custom sorting logic
            for the merged list.

    Returns:
        A merged dictionary or list, depending on the types present in
        `nested_structure`.

    Raises:
        TypeError: If `nested_structure` contains objects of incompatible
            types that cannot be merged.
    """
    if not isinstance(nested_structure, list):
        raise TypeError("Please input a list")
    if is_homogeneous(nested_structure, dict):
        return _merge_dicts(nested_structure, overwrite, dict_sequence)
    elif is_homogeneous(nested_structure, list):
        return _merge_sequences(nested_structure, sort_list, custom_sort)
    else:
        raise TypeError(
            "All items in the input list must be of the same type, "
            "either dict, list, or Iterable."
        )


def _deep_merge_dicts(
    dict1: dict[str, Any], dict2: dict[str, Any]
) -> dict[str, Any]:
    """
    Recursively merges two dictionaries, combining values where keys overlap.

    Args:
        dict1: The first dictionary.
        dict2: The second dictionary.

    Returns:
        The merged dictionary.
    """
    for key in dict2:
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                _deep_merge_dicts(dict1[key], dict2[key])
            else:
                if not isinstance(dict1[key], list):
                    dict1[key] = [dict1[key]]
                dict1[key].append(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


def _merge_dicts(
    iterables: list[dict[str, Any]],
    dict_update: bool,
    dict_sequence: bool,
) -> dict[str, Any]:
    """
    Merges a list of dictionaries into a single dictionary, with options for
    handling duplicate keys and sequences.

    Args:
        iterables: A list of dictionaries to merge.
        dict_update: If True, overwrite existing keys in dictionaries
            with those from subsequent dictionaries.
        dict_sequence: Enables unique key generation for duplicate keys
            by appending a sequence number

    Returns:
        The merged dictionary.
    """
    merged_dict = {}  # {'a': [1, 2]}
    sequence_counters = defaultdict(int)
    list_values = {}

    for d in iterables:  # [{'a': [1, 2]}, {'a': [3, 4]}]
        for key, value in d.items():  # {'a': [3, 4]}
            if key not in merged_dict or dict_update:
                if (
                    key in merged_dict
                    and isinstance(merged_dict[key], dict)
                    and isinstance(value, dict)
                ):
                    _deep_merge_dicts(merged_dict[key], value)
                else:
                    merged_dict[key] = value  # {'a': [1, 2]}
                    if isinstance(value, list):
                        list_values[key] = True
            elif dict_sequence:
                sequence_counters[key] += 1
                new_key = f"{key}{sequence_counters[key]}"
                merged_dict[new_key] = value
            else:
                if not isinstance(merged_dict[key], list) or list_values.get(
                    key, False
                ):
                    merged_dict[key] = [merged_dict[key]]
                merged_dict[key].append(value)

    return merged_dict


def _merge_sequences(
    iterables: list[list[Any]],
    sort_list: bool,
    custom_sort: Callable[[Any], Any] | None = None,
) -> list[Any]:
    """
    Merges a list of lists into a single list, with options for sorting and
    custom sorting logic.

    Args:
        iterables: A list of lists to merge.
        sort_list: When True, sort the resulting list after merging.
        custom_sort: An optional callable that defines custom sorting logic
            for the merged list.

    Returns:
        The merged list.
    """
    merged_list = list(chain(*iterables))
    if sort_list:
        if custom_sort:
            return sorted(merged_list, key=custom_sort)
        else:
            return sorted(merged_list, key=lambda x: (isinstance(x, str), x))
    return merged_list
