"""
Module for merging nested structures.

Provides functionality to merge multiple dictionaries, lists, or sequences
into a unified structure with options for handling duplicate keys, sorting,
and custom sorting logic.

Functions:
    nmerge: Merge multiple dictionaries, lists, or sequences into a unified 
            structure.

    _deep_merge_dicts: Recursively merges two dictionaries, combining values
                       where keys overlap.

    _merge_dicts: Merges a list of dictionaries into a single dictionary,
                  with options for handling duplicate keys and sequences.

    _merge_sequences: Merges a list of lists into a single list, with options
                      for sorting and custom sorting logic.
"""

from collections import defaultdict
from itertools import chain
from typing import Any, Callable, Union, List
from lionagi.os.libs.data_handlers._util import is_homogeneous


def nmerge(
    nested_structure: List[Union[dict, list]],
    /,
    *,
    overwrite: bool = False,
    dict_sequence: bool = False,
    sep: str = "|",
    sort_list: bool = False,
    custom_sort: Callable[[Any], Any] | None = None,
) -> Union[dict, list]:
    """
    Merge multiple dictionaries, lists, or sequences into a unified structure.

    Args:
        nested_structure (list[dict | list]): A list containing dictionaries,
            lists, or other iterable objects to merge.
        overwrite (bool, optional): If True, overwrite existing keys in
            dictionaries with those from subsequent dictionaries. Defaults to
            False.
        dict_sequence (bool, optional): Enables unique key generation for
            duplicate keys by appending a sequence number, using `sequence_separator`
            as the delimiter. Applicable only if `overwrite` is False.
        sequence_separator (str, optional): The separator used when generating
            unique keys for duplicate dictionary keys. Defaults to "|".
        sort_list (bool, optional): When True, sort the resulting list after
            merging. It does not affect dictionaries. Defaults to False.
        custom_sort (Callable[[Any], Any] | None, optional): An optional callable
            that defines custom sorting logic for the merged list. Defaults to None.

    Returns:
        dict | list: A merged dictionary or list, depending on the types present
            in `nested_structure`.

    Raises:
        TypeError: If `nested_structure` contains objects of incompatible types
            that cannot be merged.
    """
    if is_homogeneous(nested_structure, dict):
        return _merge_dicts(nested_structure, overwrite, dict_sequence, sep)
    elif is_homogeneous(nested_structure, list) and not any(
        isinstance(it, (dict, str)) for it in nested_structure
    ):
        return _merge_sequences(nested_structure, sort_list, custom_sort)
    else:
        raise TypeError(
            "All items in the input list must be of the same type, "
            "either dict, list, or Iterable."
        )


def _deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merges two dictionaries, combining values where keys overlap.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        dict: The merged dictionary.
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
    iterables: List[dict[Any, Any]],
    dict_update: bool,
    dict_sequence: bool,
    sequence_separator: str,
) -> dict[Any, Any]:
    """
    Merges a list of dictionaries into a single dictionary, with options for
    handling duplicate keys and sequences.

    Args:
        iterables (list[dict[Any, Any]]): A list of dictionaries to merge.
        dict_update (bool): If True, overwrite existing keys in dictionaries
            with those from subsequent dictionaries.
        dict_sequence (bool): Enables unique key generation for duplicate keys
            by appending a sequence number, using `sequence_separator` as the
            delimiter.
        sequence_separator (str): The separator used when generating unique keys
            for duplicate dictionary keys.

    Returns:
        dict[Any, Any]: The merged dictionary.
    """
    merged_dict = {}
    sequence_counters = defaultdict(int)

    for d in iterables:
        for key, value in d.items():
            if key not in merged_dict or dict_update:
                if (
                    key in merged_dict
                    and isinstance(merged_dict[key], dict)
                    and isinstance(value, dict)
                ):
                    _deep_merge_dicts(merged_dict[key], value)
                else:
                    merged_dict[key] = value
            elif dict_sequence:
                sequence_counters[key] += 1
                new_key = f"{key}{sequence_separator}{sequence_counters[key]}"
                merged_dict[new_key] = value
            else:
                if not isinstance(merged_dict[key], list):
                    merged_dict[key] = [merged_dict[key]]
                merged_dict[key].append(value)

    return merged_dict


def _merge_sequences(
    iterables: list,
    sort_list: bool,
    custom_sort: Callable[[Any], Any] | None = None,
) -> list[Any]:
    """
    Merges a list of lists into a single list, with options for sorting and
    custom sorting logic.

    Args:
        iterables (list[list[Any]]): A list of lists to merge.
        sort_list (bool): When True, sort the resulting list after merging.
            It does not affect dictionaries.
        custom_sort (Callable[[Any], Any] | None, optional): An optional callable
            that defines custom sorting logic for the merged list.

    Returns:
        list[Any]: The merged list.
    """
    merged_list = list(chain(*iterables))
    if sort_list:
        if custom_sort:
            return sorted(merged_list, key=custom_sort)
        else:
            return sorted(merged_list, key=lambda x: (isinstance(x, str), x))
    return merged_list
