from typing import Any, Callable, Sequence
from lion_core import CoreLib, LN_UNDEFINED


def nset(
    nested_structure: dict[str, Any] | list[Any],
    indices: str | int | Sequence[str | int],
    value: Any,
) -> None:
    """
    Set a value within a nested structure at the specified path defined by indices.

    This method allows setting a value deep within a nested dictionary or list by
    specifying a path to the target location using a sequence of indices. Each index
    in the sequence represents a level in the nested structure, with integers used
    for list indices and strings for dictionary keys.

    Args:
        nested_structure: The nested structure where the value will be set.
        indices: The path of indices leading to where the value should be set.
        value: The value to set at the specified location in the nested structure.

    Raises:
        ValueError: If the indices sequence is empty.
        TypeError: If the target container is not a list or dictionary, or if
                   the index type is incorrect.

    Examples:
        >>> data = {'a': {'b': [10, 20]}}
        >>> nset(data, ['a', 'b', 1], 99)
        >>> assert data == {'a': {'b': [10, 99]}}

        >>> data = [0, [1, 2], 3]
        >>> nset(data, [1, 1], 99)
        >>> assert data == [0, [1, 99], 3]
    """
    return CoreLib.nset(nested_structure, indices, value)


def nget(
    nested_structure: dict[Any, Any] | list[Any],
    indices: list[int | str],
    default: Any = LN_UNDEFINED,
) -> Any:
    """
    Retrieve a value from a nested structure using a list of indices.

    Args:
        nested_structure: The nested structure to retrieve the value from.
        indices: A list of indices to navigate through the nested structure.
        default: The default value to return if the target value is not found.
            If not provided, a LookupError is raised.

    Returns:
        The value retrieved from the nested structure, or the default value
        if provided.

    Raises:
        LookupError: If the target value is not found and no default value
            is provided.
    """
    return CoreLib.nget(nested_structure, indices, default=default)


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
    return CoreLib.nmerge(
        nested_structure,
        overwrite=overwrite,
        dict_sequence=dict_sequence,
        sort_list=sort_list,
        custom_sort=custom_sort,
    )


def flatten(
    nested_structure: Any,
    /,
    *,
    parent_key: str = "",
    sep: str = "|",
    max_depth: int | None = None,
    inplace: bool = False,
    dict_only: bool = False,
) -> dict[str, Any] | None:
    """
    Flatten a nested dictionary or list into a single-level dictionary.

    Args:
        nested_structure: The nested structure to flatten.
        parent_key: The base key for flattened keys. Defaults to "".
        sep: The separator for joining keys. Defaults to "|".
        max_depth: The maximum depth to flatten. Defaults to None.
        inplace: If True, modifies the original structure. Defaults to False.
        dict_only: If True, only flattens dictionaries. Defaults to False.

    Returns:
        The flattened dictionary if inplace is False, otherwise None.

    Raises:
        TypeError: If parent_key is not a string.
        ValueError: If inplace is True and nested_structure is not a
            dictionary.
    """
    return CoreLib.flatten(
        nested_structure,
        parent_key=parent_key,
        sep=sep,
        max_depth=max_depth,
        inplace=inplace,
        dict_only=dict_only,
    )


def unflatten(
    flat_dict: dict[str, Any], sep: str = "|", inplace: bool = False
) -> dict[str, Any] | list[Any]:
    """
    Unflatten a single-level dictionary into a nested dictionary or list.

    Args:
        flat_dict: The flattened dictionary to unflatten.
        sep: The separator used for joining keys.
        inplace: Whether to modify the input dictionary in place.

    Returns:
        The unflattened nested dictionary or list.

    Examples:
        >>> unflatten({"a|b|c": 1, "a|b|d": 2})
        {'a': {'b': {'c': 1, 'd': 2}}}

        >>> unflatten({"0": "a", "1": "b", "2": "c"})
        ['a', 'b', 'c']
    """
    return CoreLib.unflatten(flat_dict, sep=sep, inplace=inplace)


def nfilter(
    nested_structure: dict[Any, Any] | list[Any], condition: Callable[[Any], bool]
) -> dict[Any, Any] | list[Any]:
    """
    Filter elements in a nested structure (dict or list) based on a condition.

    Args:
        nested_structure: The nested structure to filter.
        condition: A function that returns True for elements to keep and
            False for elements to discard.

    Returns:
        The filtered nested structure.

    Raises:
        TypeError: If nested_structure is not a dict or list.
    """
    return CoreLib.nfilter(nested_structure, condition)


def ninsert(
    nested_structure: dict[Any, Any] | list[Any],
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
    return CoreLib.ninsert(
        nested_structure, indices, value, current_depth=current_depth
    )


def get_flattened_keys(
    nested_structure: Any,
    /,
    *,
    sep: str = "|",
    max_depth: int | None = None,
    dict_only: bool = False,
    inplace: bool = False,
) -> list[str]:
    """
    Get all keys from a flattened representation of a nested structure.

    Args:
        nested_structure: The nested structure to process.
        sep: The separator for joining keys. Defaults to "|".
        max_depth: The maximum depth to flatten. Defaults to None.
        dict_only: If True, only flattens dictionaries. Defaults to False.
        inplace: If True, modifies the original structure. Defaults to False.

    Returns:
        A list of flattened keys.
    """
    return CoreLib.get_flattened_keys(
        nested_structure,
        sep=sep,
        max_depth=max_depth,
        dict_only=dict_only,
        inplace=inplace,
    )
