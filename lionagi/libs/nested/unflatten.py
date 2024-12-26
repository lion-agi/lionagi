from typing import Any


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

    def _unflatten(data: dict) -> dict | list:
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
        if result and all(
            isinstance(key, str) and key.isdigit() for key in result
        ):
            return [result[str(i)] for i in range(len(result))]
        return result

    if inplace:
        unflattened_dict = {}
        for key, value in flat_dict.items():
            parts = key.split(sep)
            current = unflattened_dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

        unflattened_result = _unflatten(unflattened_dict)
        flat_dict.clear()
        if isinstance(unflattened_result, list):
            flat_dict.update(
                {str(i): v for i, v in enumerate(unflattened_result)}
            )
        else:
            flat_dict.update(unflattened_result)
        return flat_dict

    else:
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
