"""
Retrieve a value from a nested structure using a list of indices.

This function navigates through a nested dictionary or list based on the 
provided indices and returns the value found at the target location. If the 
target value is not found, a default value can be returned, or a LookupError 
can be raised.

Args:
    nested_structure (dict | list): The nested structure to retrieve the 
        value from.
    indices (list[int | str]): A list of indices to navigate through the 
        nested structure.
    default (Any, optional): The default value to return if the target 
        value is not found. If not provided, a LookupError is raised.

Returns:
    Any: The value retrieved from the nested structure, or the default 
        value if provided.

Raises:
    LookupError: If the target value is not found and no default value 
        is provided.
"""

from lionagi.os.libs.data_handlers._util import get_target_container
from typing import Any, Union


def nget(
    nested_structure: Union[dict, list],
    indices: list[Union[int, str]],
    default: Any = ...,
) -> Any:
    """
    Retrieve a value from a nested structure using a list of indices.

    Args:
        nested_structure (dict | list): The nested structure to retrieve the
            value from.
        indices (list[int | str]): A list of indices to navigate through the
            nested structure.
        default (Any, optional): The default value to return if the target
            value is not found. If not provided, a LookupError is raised.

    Returns:
        Any: The value retrieved from the nested structure, or the default
            value if provided.

    Raises:
        LookupError: If the target value is not found and no default value
            is provided.
    """
    try:
        target_container = get_target_container(nested_structure, indices[:-1])
        last_index = indices[-1]

        if (
            isinstance(target_container, list)
            and isinstance(last_index, int)
            and last_index < len(target_container)
        ):
            return target_container[last_index]
        elif isinstance(target_container, dict) and last_index in target_container:
            return target_container[last_index]
        elif default is not ...:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")
    except (IndexError, KeyError, TypeError):
        if default is not ...:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")
