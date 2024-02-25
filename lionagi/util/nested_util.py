from collections import defaultdict
from itertools import chain
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Tuple,
    Union,
    Iterable,
    Optional,
)

from .sys_util import SysUtil
from .convert_util import ConvertUtil


def nset(nested_structure: Dict | List, indices: List[int | str], value: Any) -> None:
    """
    sets a value within a nested structure at the specified path defined by indices.

    this method allows setting a value deep within a nested dictionary or list by
    specifying a path to the target location using a list of indices. each index in
    the list represents a level in the nested structure, with integers used for
    list indices and strings for dictionary keys.

    Args: nested_structure (Dict | List): The nested structure where the value will
    be set. indices (List[int | str]): The path of indices leading to where the
    value should be set. value (Any): The value to set at the specified location in
    the nested structure.

    Raises: ValueError: Raised if the indices list is empty. TypeError: Raised if
    the target container is not a list or dictionary, or if the index type is
    incorrect.

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

    target_container = _get_target_container(nested_structure, indices[:-1])
    last_index = indices[-1]

    if isinstance(target_container, list):
        _ensure_list_index(target_container, last_index)
        target_container[last_index] = value
    elif isinstance(target_container, dict):
        target_container[last_index] = value
    else:
        raise TypeError("Cannot set value on non-list/dict element")


def nget(
    nested_structure: Dict | List,
    indices: List[int | str],
    default: Optional[Any] = None,
) -> Any:
    """
    retrieves a value from a nested list or dictionary structure, with an option to
    specify a default value.

    navigates through the nested structure using the specified indices and
    retrieves the value at the target location. the indices can be integers for
    lists and strings for dictionaries. if the target cannot be reached or does not
    exist, it returns the specified default value or raises an error if no default
    is provided.

    Args: nested_structure (Dict | List): The nested list or dictionary structure.
    indices (List[int | str]): A list of indices to navigate through the structure.
    default (Optional[Any]): The default value to return if the target cannot be
    reached. if `default` is not provided and the target cannot be reached,
    a LookupError is raised.

    Returns: Any: The value at the target location, the default value if provided
    and the target cannot be reached, or raises an error.

    Raises: LookupError: If the target location cannot be reached or does not exist
    and no default value is provided.

    Examples:
        >>> data = {'a': {'b': [10, 20]}}
        >>> assert nget(data, ['a', 'b', 1]) == 20
        >>> nget(data, ['a', 'b', 2])
        Traceback (most recent call last):
        ...
        LookupError: Target not found and no default value provided.
    """

    try:
        target_container = _get_target_container(nested_structure, indices[:-1])
        last_index = indices[-1]

        if (
            isinstance(target_container, list)
            and isinstance(last_index, int)
            and last_index < len(target_container)
        ):

            return target_container[last_index]
        elif isinstance(target_container, dict) and last_index in target_container:
            return target_container[last_index]
        elif default is not None:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")
    except (IndexError, KeyError, TypeError):
        if default is not None:
            return default
        else:
            raise LookupError("Target not found and no default value provided.")


# nested merge
def nmerge(
    nested_structure: List[Dict | List | Iterable],
    dict_update: bool = False,
    dict_sequence: bool = False,
    sequence_separator: str = "_",
    sort_list: bool = False,
    custom_sort: Optional[Callable[[Any], Any]] = None,
) -> Dict | List:
    """
    merges multiple dictionaries, lists, or sequences into a unified structure.

    this method intelligently merges a nested_structure of iterable objects (
    dictionaries or lists) into a single cohesive dictionary or list. it offers
    flexibility in handling key conflicts for dictionaries and can optionally sort
    merged sequences.

    Args: nested_structure: A list containing dictionaries, lists, or other
    iterable objects to merge. dict_update: Determines whether to overwrite
    existing keys in dictionaries with those from subsequent dictionaries. defaults
    to False, preserving original keys. dict_sequence: Enables unique key
    generation for duplicate keys by appending a sequence number,
    using `sequence_separator` as the delimiter. applicable only if `dict_update`
    is False. sequence_separator: The separator used when generating unique keys
    for duplicate dictionary keys. sort_list: When true, sort the resulting list
    after merging. it Does not affect dictionaries. custom_sort: An optional callable
    that defines custom sorting logic for the merged list.

    Returns:
        A merged dictionary or list,
        depending on the types present in `iterables`.

    Raises:
        TypeError:
        If `iterables`
        contains objects of incompatible types that cannot be merged.

    examples:
        >>> nmerge([{'a': 1}, {'b': 2}], dict_update=True)
        {'a': 1, 'b': 2}

        >>> nmerge([[1, 2], [3, 4]], sort_list=True)
        [1, 2, 3, 4]
    """
    if ConvertUtil.is_homogeneous(nested_structure, Dict):
        return _merge_dicts(
            nested_structure, dict_update, dict_sequence, sequence_separator
        )
    elif ConvertUtil.is_homogeneous(nested_structure, List) and not any(
        isinstance(it, (Dict, str)) for it in nested_structure
    ):
        return _merge_sequences(nested_structure, sort_list, custom_sort)
    else:
        raise TypeError(
            "All items in the input_ list must be of the same type, "
            "either Dict, List, or Iterable."
        )


# flatten dictionary
def flatten(
    nested_structure: Any,
    parent_key: str = "",
    sep: str = "_",
    max_depth: int | None = None,
    inplace: bool = False,
    dict_only: bool = False,
) -> Dict | None:
    """
    flattens a nested structure into a dictionary with composite keys.

    this method transforms a nested dictionary or list into a single-level
    dictionary with keys representing the path to each value. it is configurable
    with respect to depth, in-place modification, and handling of lists.

    Args: nested_structure: The nested dictionary or list to flatten. parent_key: A
    prefix for all keys in the flattened dictionary, useful for nested calls. sep:
    The separator used between levels in composite keys. max_depth: The maximum
    depth to flatten; if None, flattens completely. inplace: If True, modifies
    `nested_structure` in place; otherwise, returns a new dictionary. dict_only: If
    True, only flattens nested dictionaries, leaving lists intact.

    Returns:
        A flattened dictionary, or None if `inplace` is True.

    Raises:
        ValueError: If `inplace` is True but `nested_structure` is not a dictionary.

    examples:
        >>> nested_dict = {'a': {'b': {'c': 1}}}
        >>> flatten(nested_dict)
        {'a_b_c': 1}

        >>> nested_list = [{'a': 1}, {'b': 2}]
        >>> flatten(nested_list, dict_only=True)
        {'0_a': 1, '1_b': 2}
    """
    if inplace:
        if not isinstance(nested_structure, dict):
            raise ValueError("Object must be a dictionary when 'inplace' is True.")
        _dynamic_flatten_in_place(
            nested_structure, parent_key, sep, max_depth, dict_only=dict_only
        )
    else:
        parent_key_tuple = tuple(parent_key.split(sep)) if parent_key else ()
        return dict(
            _dynamic_flatten_generator(
                nested_structure, parent_key_tuple, sep, max_depth, dict_only=dict_only
            )
        )


# unflatten dictionary
def unflatten(
    flat_dict: Dict[str, Any],
    sep: str = "_",
    custom_logic: Callable[[str], Any] | None = None,
    max_depth: int | None = None,
) -> Dict | List:
    """
    reconstructs a nested structure from a flat dictionary with composite keys.

    given a flat dictionary with keys representing paths, this method rebuilds the
    original nested dictionary or list.it supports custom logic for interpreting
    keys and can limit the reconstruction depth.

    Args:
        flat_dict: A flat dictionary with composite keys to unflatten.
        sep: The separator used in composite keys, indicating nested levels.
        custom_logic: An optional function to process each part of the composite keys.
        max_depth: The maximum depth for nesting during reconstruction.

    Returns:
        The reconstructed nested dictionary or list.

    examples:
        >>> flat_dict_ = {'a_b_c': 1}
        >>> unflatten(flat_dict)
        {'a': {'b': {'c': 1}}}

        >>> flat_dict_ = {'0_a': 1, '1_b': 2}
        >>> unflatten(flat_dict)
        [{'a': 1}, {'b': 2}]
    """
    unflattened = {}
    for composite_key, value in flat_dict.items():
        parts = composite_key.split(sep)
        if custom_logic:
            parts = [custom_logic(part) for part in parts]
        else:
            parts = [int(part) if part.isdigit() else part for part in parts]

        if not unflattened and all(isinstance(part, int) for part in parts):
            unflattened = []

        ninsert(unflattened, parts, value, sep, max_depth)

    if isinstance(unflattened, dict) and all(
        isinstance(k, int) for k in unflattened.keys()
    ):
        max_index = max(unflattened.keys(), default=-1)
        return [unflattened.get(i) for i in range(max_index + 1)]
    if not unflattened:
        return {}
    return unflattened


def nfilter(
    nested_structure: Dict | List, condition: Callable[[Any], bool]
) -> Dict | List:
    """
    filters items in a dictionary or list based on a specified condition.

    iterates through the given collection, applying a condition to each element.
    for dictionaries, the condition receives key-value pairs as tuples. for lists,
    it directly receives the elements. only items for which the condition returns
    True are included in the resulting collection.

    Args: nested_structure (Dict | List): The collection to filter, either a
    dictionary or a list. condition (Callable[[Any], bool]): A function that
    evaluates each item (or key-value pair in the case of dictionaries) against a
    condition. returns True to include the item in the result, False otherwise.

    Returns: Dict | List: A new collection of the same types as `collection`,
    containing only items that meet the condition.

    Raises:
        TypeError: Raised if `collection` is not a dictionary or a list.

    Examples:
        >>> nfilter({'a': 1, 'b': 2, 'c': 3}, lambda x: x[1] > 1)
        {'b': 2, 'c': 3}
        >>> nfilter([1, 2, 3, 4], lambda x: x % 2 == 0)
        [2, 4]
    """
    if isinstance(nested_structure, Dict):
        return _filter_dict(nested_structure, condition)
    elif isinstance(nested_structure, List):
        return _filter_list(nested_structure, condition)
    else:
        raise TypeError("The nested_structure must be either a Dict or a List.")


def ninsert(
    nested_structure: Dict | List,
    parts: List[str | int],
    value: Any,
    sep: str = "_",
    max_depth: int | None = None,
    current_depth: int = 0,
) -> None:
    """
    inserts a value into a nested structure at a specified path.

    navigates a nested dictionary or list based on a sequence of indices or keys (
    `parts`) and inserts `value` at the final location. this method can create
    intermediate dictionaries or lists as needed.

    Args: nested_structure (Dict | List): The nested structure to modify. parts (
    List[str | int]): The sequence of keys (str for dicts) or indices (int for
    lists) defining the path to the insertion point. value (Any): The value to
    insert at the specified location within `subject`. sep (str): A separator used
    when concatenating parts to form composite keys in case of ambiguity. defaults
    to '_'. max_depth (int | None): Limits the depth of insertion. if `None`,
    no limit is applied. current_depth (int): Internal use only; tracks the current
    depth during recursive calls.

    Examples:
        >>> subject_ = {'a': {'b': [1, 2]}}
        >>> ninsert(subject_, ['a', 'b', 2], 3)
        >>> assert subject_ == {'a': {'b': [1, 2, 3]}}

        >>> subject_ = []
        >>> ninsert(subject_, [0, 'a'], 1)
        >>> assert subject_ == [{'a': 1}]
    """
    parts_len = len(parts)
    parts_depth = 0
    for i, part in enumerate(parts[:-1]):
        if max_depth is not None and current_depth >= max_depth:
            break

        if isinstance(part, int):
            while len(nested_structure) <= part:
                nested_structure.append(None)
            if nested_structure[part] is None or not isinstance(
                nested_structure[part], (dict, list)
            ):
                next_part = parts[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
            nested_structure = nested_structure[part]
        else:
            if part not in nested_structure:
                next_part = parts[i + 1]
                nested_structure[part] = [] if isinstance(next_part, int) else {}
            nested_structure = nested_structure[part]
        current_depth += 1
        parts_depth += 1

    if parts_depth < parts_len - 1:
        last_part = sep.join([str(part) for part in parts[parts_depth:]])
    else:
        last_part = parts[-1]
    if isinstance(last_part, int):
        _handle_list_insert(nested_structure, last_part, value)
    else:
        if isinstance(nested_structure, list):
            nested_structure.append({last_part: value})
        else:
            nested_structure[last_part] = value


# noinspection PyDecorator
def get_flattened_keys(
    nested_structure: Any,
    sep: str = "_",
    max_depth: int | None = None,
    dict_only: bool = False,
    inplace: bool = False,
) -> List[str]:
    """
    retrieves keys from a nested structure after flattening.

    this method generates a list of all keys that would exist in a flattened
    representation of the given nested structure. it supports custom depth,
    in-place modifications, and can be limited to processing dictionaries only.

    Args: nested_structure: The nested dictionary or list to process. sep: The
    separator used between nested keys in the flattened keys. defaults to '_'.
    max_depth: The maximum depth to flatten. if None, flattens the structure
    completely. dict_only: If True, only processes nested dictionaries, leaving
    lists as values. inplace: If True, flattens `nested_structure` in place,
    modifying the original object.

    Returns:
        A list of strings representing the keys in the flattened structure.

    Raises:
        ValueError: If `inplace` is True but `nested_structure` is not a dictionary.

    Examples:
        >>> nested_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        >>> keys = get_flattened_keys(nested_dict)
        >>> assert keys == ['a', 'b_c', 'b_d_e']

        >>> nested_list = [{'a': 1}, {'b': 2}]
        >>> keys = get_flattened_keys(nested_list, dict_only=True)
        >>> assert keys == ['0_a', '1_b']
    """
    if inplace:
        obj_copy = SysUtil.create_copy(nested_structure, num=1)
        flatten(
            obj_copy, sep=sep, max_depth=max_depth, inplace=True, dict_only=dict_only
        )
        return list(obj_copy.keys())
    else:
        return list(
            flatten(
                nested_structure, sep=sep, max_depth=max_depth, dict_only=dict_only
            ).keys()
        )


def _dynamic_flatten_in_place(
    nested_structure: Any,
    parent_key: str = "",
    sep: str = "_",
    max_depth: int | None = None,
    current_depth: int = 0,
    dict_only: bool = False,
) -> None:
    """
    Flattens a nested structure in place up to a specified depth.

    This internal helper function recursively flattens a nested dictionary or list,
    modifying the original structure. It can be limited to processing only
    dictionaries and to a certain depth.

    Args:
        nested_structure: The structure to flatten.
        parent_key: Initial key prefix for all keys in the flattened structure.
        sep: Separator for nested keys.
        max_depth: Limits the flattening to a specific depth.
        current_depth: Tracks the current depth in the recursion.
        dict_only: Limits the flattening to dictionaries only, ignoring lists.

    Note:
        This function modifies `nested_structure` in place.

    Examples:
        Given a nested dictionary `nested_dict` with the appropriate structure,
        `_dynamic_flatten_in_place(nested_dict)` will modify it to a flattened form.
    """
    if isinstance(nested_structure, dict):
        keys_to_delete = []
        items = list(nested_structure.items())  # Create a copy of the dictionary
        # items

        for k, v in items:
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict) and (max_depth is None or current_depth < max_depth):
                _dynamic_flatten_in_place(
                    v, new_key, sep, max_depth, current_depth + 1, dict_only
                )
                keys_to_delete.append(k)
                nested_structure.update(v)
            elif not dict_only and (
                isinstance(v, list) or not isinstance(v, (dict, list))
            ):
                nested_structure[new_key] = v
                if parent_key:
                    keys_to_delete.append(k)

        for k in keys_to_delete:
            del nested_structure[k]


def _handle_list_insert(nested_structure: List, part: int, value: Any) -> None:
    """
    Ensures a specified index in a list is occupied by a given value, extending the
    list if necessary.

    This method modifies a list by inserting or replacing an element at a specified
    index. If the index is beyond the current list size, the list is extended with
    `None` values up to the index, then the specified value is inserted.

    Args:
        nested_structure: The list to modify.
        part: The target index for inserting or replacing the value.
        value: The value to be inserted or to replace an existing value in the list.

    Note:
        This function directly modifies the input list in place.
    """
    while len(nested_structure) <= part:
        nested_structure.append(None)
    nested_structure[part] = value


def _ensure_list_index(lst_: List, index: int, default: Any = None) -> None:
    """
    Extends a list to ensure it has a minimum length, appending a default value as
    needed.

    This utility method ensures that a list is extended to at least a specified
    index plus one. If the list's length is less than this target, it is appended
    with a specified default value until it reaches the required length.

    Args:
        lst_: The list to extend.
        index: The target index that the list should reach or exceed.
        default: The value to append to the list for extension. Defaults to None.

    Note: Modifies the list in place, ensuring it can safely be indexed at `index`
    without raising an IndexError.
    """
    while len(lst_) <= index:
        lst_.append(default)


def _deep_update(original: Dict, update: Dict) -> Dict:
    """
    Recursively merges two dictionaries, updating nested dictionaries instead of
    overwriting them.

    For each key in the `update` dictionary, if the corresponding value is a
    dictionary and the same key exists in `original` with a dictionary value,
    this method recursively updates the dictionary. Otherwise, it updates or adds
    the key-value pair to `original`.

    Args:
        original: The dictionary to update.
        update: The dictionary containing updates to apply to `original`.

    Returns:
        The `original` dictionary after applying updates from `update`.

    Note:
        This method modifies the `original` dictionary in place.
    """
    for key, value in update.items():
        if isinstance(value, dict) and key in original:
            original[key] = _deep_update(original.get(key, {}), value)
        else:
            original[key] = value
    return original


def _dynamic_flatten_generator(
    nested_structure: Any,
    parent_key: Tuple[str, ...],
    sep: str = "_",
    max_depth: int | None = None,
    current_depth: int = 0,
    dict_only: bool = False,
) -> Generator[Tuple[str, Any], None, None]:
    """
    Generates flattened key-value pairs from a nested structure.

    Recursively traverses a nested dictionary or list, yielding key-value pairs
    with keys representing the path to each value. This method allows for selective
    flattening of dictionaries within mixed structures and can be limited to a
    certain depth.

    Args: nested_structure: The nested object to flatten, which can be either a
    dictionary or a list. parent_key: A tuple of keys representing the path to the
    current position within the nested structure. sep: The separator to use between
    keys in the flattened keys. Defaults to '_'. max_depth: The maximum depth to
    traverse. If None, no limit is applied. Defaults to None. current_depth:
    Current depth in the nested structure, used internally for recursive depth
    tracking. dict_only: If True, flattens only nested dictionaries, leaving lists
    intact.

    Yields: Flattened key-value pairs, where the key is a string representing the
    path to the value in the nested structure, and the value is the corresponding
    value in that path.
    """
    if max_depth is not None and current_depth > max_depth:
        yield sep.join(parent_key), nested_structure
        return

    if isinstance(nested_structure, dict):
        for k, v in nested_structure.items():
            new_key = parent_key + (k,)
            yield from _dynamic_flatten_generator(
                v, new_key, sep, max_depth, current_depth + 1, dict_only
            )
    elif isinstance(nested_structure, list) and not dict_only:
        for i, item in enumerate(nested_structure):
            new_key = parent_key + (str(i),)
            yield from _dynamic_flatten_generator(
                item, new_key, sep, max_depth, current_depth + 1, dict_only
            )
    else:
        yield sep.join(parent_key), nested_structure


def _deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deeply merges two dictionaries, combining nested dictionaries instead of
    overwriting them.

    When encountering a key in both dictionaries that has a dictionary as its
    value, this function recursively merges the nested dictionaries. For other
    types of values or unique keys, it simply updates `dict1` with the key-value
    pairs from `dict2`.

    Args:
        dict1: The target dictionary to update with values from `dict2`.
        dict2: The source dictionary providing updates and additional key-value pairs.

    Returns:
        The updated dictionary `dict1` with deeply merged values from `dict2`.

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
    iterables: List[Dict[Any, Any]],
    dict_update: bool,
    dict_sequence: bool,
    sequence_separator: str,
) -> Dict[Any, Any]:
    """
    Merges a list of dictionaries into a single dictionary.

    Args: iterables: A list of dictionaries to be merged.dict_update: If True,
    the value of a key in a later dictionary overwrites the previous one.
    dict_sequence: If True, instead of overwriting, keys are made unique by
    appending a sequence number. sequence_separator: The separator to use when
    creating unique keys in case of dict_sequence.

    Returns: A merged dictionary containing the combined key-value pairs from all
    dictionaries in the list.
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
    iterables: List[Iterable[Any]],
    sort_list: bool,
    custom_sort: Callable[[Any], Any] | None = None,
) -> List[Any]:
    """
    Concatenates multiple sequences into a single list, with optional sorting.

    This function merges various iterable sequences into a unified list. It can
    optionally sort the resulting list either according to Python's default sorting
    mechanism or a custom sorting function provided by the user.

    Args:
        iterables: A collection of iterable sequences to be merged.
        sort_list: Determines whether to sort the merged list.
        custom_sort: Optional. A function defining custom sort criteria.

    Returns: List[Any]: The merged (and potentially sorted) list of elements from
    all provided iterables.

    Note: The sorting behavior is defined by `sort_list` and `custom_sort`. If
    `sort_list` is False, `custom_sort` is ignored. If True, the list is sorted
    using Python's default sort unless `custom_sort` is provided.
    """
    merged_list = list(chain(*iterables))
    if sort_list:
        if custom_sort:
            return sorted(merged_list, key=custom_sort)

        else:
            return sorted(merged_list, key=lambda x: (isinstance(x, str), x))
    return merged_list


def _filter_dict(
    dictionary: Dict[Any, Any], condition: Callable[[Tuple[Any, Any]], bool]
) -> Dict[Any, Any]:
    """
    Filters the entries in a dictionary based on a specified condition.

    Evaluates each key-value pair in the dictionary with the provided condition.
    If the condition returns True, the key-value pair is retained in the resulting
    dictionary.

    Args: dictionary: The dictionary to be filtered. condition: A function that
    accepts a key-value pair (as a tuple) and returns a boolean. Key-value pairs
    for which the function returns True are included in the output dictionary.

    Returns: Dict[Any, Any]: A new dictionary containing only the entries that
    satisfy the condition.
    """
    return {k: v for k, v in dictionary.items() if condition((k, v))}


def _filter_list(lst: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    """
    Filters elements in a list based on a specified condition.

    Applies the provided condition to each element in the list. Elements for which
    the condition returns True are included in the resulting list.

    Args: lst: The list to be filtered. condition: A function that evaluates each
    element in the list. If the function returns True, the element is included in
    the filtered list.

    Returns:
        List[Any]: A new list comprising elements that meet the condition.
    """
    return [item for item in lst if condition(item)]


def _get_target_container(
    nested_list: Union[List, Dict], indices: List[Union[int, str]]
) -> Union[List, Dict]:
    current_element = nested_list
    for index in indices:
        if isinstance(current_element, list):
            if isinstance(index, int) and 0 <= index < len(current_element):
                current_element = current_element[index]
            else:
                raise IndexError("List index out of range")
        elif isinstance(current_element, dict):
            if index in current_element:
                current_element = current_element[index]
            else:
                raise KeyError("Key not found in dictionary")
        else:
            raise TypeError("Current element is neither a list nor a dictionary")
    return current_element


def _is_structure_homogeneous(
    structure: Any, return_structure_type: bool = False
) -> Union[bool, Tuple[bool, Optional[type]]]:
    """
    checks if a nested structure is homogeneous, meaning it doesn't contain a mix
    of lists and dictionaries.

    Args: structure: The nested structure to check. return_structure_type: Flag to
    indicate whether to return the type of homogeneous structure.

    Returns: If return_structure_type is False, returns a boolean indicating
    whether the structure is homogeneous. if return_structure_type is True,
    returns a tuple containing a boolean indicating whether the structure is
    homogeneous, and the type of the homogeneous structure if it is homogeneous (
    either list, dict, or None).

    examples:
        >>> _is_structure_homogeneous({'a': {'b': 1}, 'c': {'d': 2}})
        True

        >>> _is_structure_homogeneous({'a': {'b': 1}, 'c': [1, 2]})
        False
    """

    # noinspection PyShadowingNames
    def _check_structure(substructure):
        structure_type = None
        if isinstance(substructure, list):
            structure_type = list
            for item in substructure:
                if not isinstance(item, structure_type) and isinstance(
                    item, (list, Dict)
                ):
                    return False, None
                result, _ = _check_structure(item)
                if not result:
                    return False, None
        elif isinstance(substructure, dict):
            structure_type = dict
            for item in substructure.values():
                if not isinstance(item, structure_type) and isinstance(
                    item, (list, dict)
                ):
                    return False, None
                result, _ = _check_structure(item)
                if not result:
                    return False, None
        return True, structure_type

    is_, structure_type = _check_structure(structure)
    if return_structure_type:
        return is_, structure_type
    else:
        return is_
