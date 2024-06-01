from ..type_conversion import to_list
from ._util import get_target_container


def nset(nested_structure: dict | list, indices: list[int | str], value) -> None:
    """
    Set a value within a nested structure at the specified path defined by indices.

    This method allows setting a value deep within a nested dictionary or list by
    specifying a path to the target location using a list of indices. Each index in
    the list represents a level in the nested structure, with integers used for
    list indices and strings for dictionary keys.

    Args:
        nested_structure (dict | list): The nested structure where the value will
            be set.
        indices (list[int | str]): The path of indices leading to where the value
            should be set.
        value (Any): The value to set at the specified location in the nested
            structure.

    Raises:
        ValueError: If the indices list is empty.
        TypeError: If the target container is not a list or dictionary, or if the
            index type is incorrect.

    Examples:
        >>> data = {'a': {'b': [10, 20]}}
        >>> nset(data, ['a', 'b', 1], 99)
        >>> assert data == {'a': {'b': [10, 99]}}

        >>> data = [0, [1, 2], 3]
        >>> nset(data, [1, 1], 99)
        >>> assert data == [0, [1, 99], 3]
    """
    if not indices:
        raise ValueError("Indices list is empty, cannot determine target container")

    _indices = to_list(indices)
    target_container = get_target_container(nested_structure, _indices[:-1])
    last_index = _indices[-1]

    if isinstance(target_container, list):
        ensure_list_index(target_container, last_index)
        target_container[last_index] = value
    elif isinstance(target_container, dict):
        target_container[last_index] = value
    else:
        raise TypeError("Cannot set value on non-list/dict element")


def ensure_list_index(lst_: list, index: int, default=None) -> None:
    """
    Extend a list to ensure it has a minimum length, appending a default value as
    needed.

    This utility method ensures that a list is extended to at least a specified
    index plus one. If the list's length is less than this target, it is appended
    with a specified default value until it reaches the required length.

    Args:
        lst_ (list): The list to extend.
        index (int): The target index that the list should reach or exceed.
        default (Any, optional): The value to append to the list for extension.
            Defaults to None.

    Note:
        Modifies the list in place, ensuring it can safely be indexed at `index`
        without raising an IndexError.
    """
    while len(lst_) <= index:
        lst_.append(default)
