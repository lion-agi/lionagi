"""
Module for unflattening dictionaries.

Provides a function to convert a single-level (flattened) dictionary
into a nested dictionary or list.

Functions:
    unflatten: Unflatten a single-level dictionary into a nested dictionary or list.
"""

from typing import Union


def unflatten(flat_dict: dict, sep: str = "/") -> Union[dict, list]:
    """
    Unflatten a single-level dictionary into a nested dictionary or list.

    Args:
        flat_dict (dict): The flattened dictionary to unflatten.
        sep (str): The separator used for joining keys. Default: '/'.

    Returns:
        Union[dict, list]: The unflattened nested dictionary or list.

    Examples:
        >>> flat_dict = {'a/b': 1, 'a/c': 2, 'd': 3}
        >>> unflattened = unflatten(flat_dict)
        >>> unflattened == {'a': {'b': 1, 'c': 2}, 'd': 3}
        True

        >>> flat_dict = {'0/a': 1, '0/b': 2, '1/a': 3, '1/b': 4}
        >>> unflattened = unflatten(flat_dict)
        >>> unflattened == [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        True
    """

    def _unflatten(data: dict) -> Union[dict, list]:
        result = {}
        for key, value in data.items():
            parts = key.split(sep)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if isinstance(value, dict):
                current[parts[-1]] = _unflatten(value)
            else:
                current[parts[-1]] = value

        # Convert dictionary to list if keys are consecutive integers
        if all(isinstance(key, str) and key.isdigit() for key in result):
            return [result[str(i)] for i in range(len(result))] or {}
        return result

    unflattened_dict = {}
    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = unflattened_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    return _unflatten(unflattened_dict)
