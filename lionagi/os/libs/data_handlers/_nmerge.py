from collections import defaultdict
from itertools import chain
from typing import Any, Callable
from ._to_list import to_list
from ._util import is_homogeneous


def nmerge(
    nested_structure: list[dict | list],
    /,
    *,
    overwrite: bool = False,
    dict_sequence: bool = False,
    sequence_separator: str = "[^_^]",
    sort_list: bool = False,
    custom_sort: Callable[[Any], Any] | None = None,
) -> dict | list:
    """
    Merge multiple dictionaries, lists, or sequences into a unified structure.

    This method intelligently merges a nested_structure of iterable objects
    (dictionaries or lists) into a single cohesive dictionary or list. It offers
    flexibility in handling key conflicts for dictionaries and can optionally sort
    merged sequences.

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
            unique keys for duplicate dictionary keys. Defaults to "[^_^]".
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

    Examples:
        >>> nmerge([{'a': 1}, {'b': 2}], overwrite=True)
        {'a': 1, 'b': 2}

        >>> nmerge([[1, 2], [3, 4]], sort_list=True)
        [1, 2, 3, 4]
    """
    if is_homogeneous(nested_structure, dict):
        return _merge_dicts(
            nested_structure, overwrite, dict_sequence, sequence_separator
        )
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
    Deeply merge two dictionaries, combining nested dictionaries instead of
    overwriting them.

    When encountering a key in both dictionaries that has a dictionary as its
    value, this function recursively merges the nested dictionaries. For other
    types of values or unique keys, it simply updates `dict1` with the key-value
    pairs from `dict2`.

    Args:
        dict1 (dict): The target dictionary to update with values from `dict2`.
        dict2 (dict): The source dictionary providing updates and additional
            key-value pairs.

    Returns:
        dict: The updated dictionary `dict1` with deeply merged values from `dict2`.

    Note:
        Modifies `dict1` in place, reflecting merged changes from `dict2`.
    """
    for key in dict2:
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                _deep_merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        else:
            dict1[key] = dict2[key]
    return dict1


def _merge_dicts(
    iterables: list[dict[Any, Any]],
    dict_update: bool,
    dict_sequence: bool,
    sequence_separator: str,
) -> dict[Any, Any]:
    """
    Merge a list of dictionaries into a single dictionary.

    Args:
        iterables (list[dict[Any, Any]]): A list of dictionaries to be merged.
        dict_update (bool): If True, the value of a key in a later dictionary
            overwrites the previous one.
        dict_sequence (bool): If True, instead of overwriting, keys are made
            unique by appending a sequence number.
        sequence_separator (str): The separator to use when creating unique
            keys in case of dict_sequence.

    Returns:
        dict[Any, Any]: A merged dictionary containing the combined key-value
            pairs from all dictionaries in the list.
    """
    merged_dict = {}
    sequence_counters = defaultdict(int)

    for d in iterables:
        for key, value in d.items():
            if key not in merged_dict or dict_update:
                merged_dict[key] = value
            elif dict_sequence:
                sequence_counters[key] += 1
                new_key = f"{key}{sequence_separator}{sequence_counters[key]}"
                merged_dict[new_key] = value

    return merged_dict


def _merge_sequences(
    iterables: list,
    sort_list: bool,
    custom_sort: Callable[[Any], Any] | None = None,
) -> list[Any]:
    """
    Concatenate multiple sequences into a single list, with optional sorting.

    This function merges various iterable sequences into a unified list. It can
    optionally sort the resulting list either according to Python's default
    sorting mechanism or a custom sorting function provided by the user.

    Args:
        iterables (list): A collection of iterable sequences to be merged.
        sort_list (bool): Determines whether to sort the merged list.
        custom_sort (Callable[[Any], Any] | None, optional): A function defining
            custom sort criteria. Defaults to None.

    Returns:
        list[Any]: The merged (and potentially sorted) list of elements from
            all provided iterables.

    Note:
        The sorting behavior is defined by `sort_list` and `custom_sort`. If
        `sort_list` is False, `custom_sort` is ignored. If True, the list is sorted
        using Python's default sort unless `custom_sort` is provided.
    """
    merged_list = to_list(chain(*iterables))
    if sort_list:
        if custom_sort:
            return sorted(merged_list, key=custom_sort)
        else:
            return sorted(merged_list, key=lambda x: (isinstance(x, str), x))
    return merged_list
