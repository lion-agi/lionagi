from collections.abc import Iterable
from copy import deepcopy
from itertools import chain
from typing import Any, Callable, Dict, Generator, List, Tuple, Union


# operations
def get_value(nested_list: Union[List, Dict], indices: List[Union[int, str]]) -> Any:
    """
    Retrieves a value from a nested list or dictionary based on a list of indices.

    Args:
        nested_list: The nested list or dictionary to retrieve the value from.
        indices: A list of indices specifying the path to the value.

    Returns:
        The value at the specified path or None if the path is invalid.

    Examples:
        >>> get_value([["a", "b"], "c"], [0, 1])
        'b'
        >>> get_value([None, ["a", "b"], "c"], [1, 0])
        'a'
    """
    current_element = nested_list
    for index in indices:
        if isinstance(current_element, list) and isinstance(index, int) and index < len(current_element):
            current_element = current_element[index]
        elif isinstance(current_element, dict) and index in current_element:
            current_element = current_element[index]
        else:
            return None  # Index out of bounds or not found
    return current_element

def set_value(nested_list: Union[List, Dict], indices: List[Union[int, str]], value: Any) -> None:
    """
    Sets a value in a nested list or dictionary based on a list of indices.

    Args:
        nested_list: The nested list or dictionary to set the value in.
        indices: A list of indices specifying the path to set the value at.
        value: The value to set at the specified path.

    Raises:
        TypeError: If the path specified by indices does not lead to a list/dict element.

    Examples:
        >>> nested_list = [None, {"a": "x", "b": "y"}, "z"]
        >>> set_value(nested_list, [0], "new_value")
        >>> nested_list
        ['new_value', {'a': 'x', 'b': 'y'}, 'z']
        >>> set_value(nested_list, [1, 'c'], "new_value")
        >>> nested_list
        ['new_value', {'a': 'x', 'b': 'y', 'c': 'new_value'}, 'z']
    """
    current_element = nested_list
    for i, index in enumerate(indices):
        if i == len(indices) - 1:  # If it's the last index, set the value
            if isinstance(current_element, list) and isinstance(index, int):
                # Extend the list if necessary
                while len(current_element) <= index:
                    current_element.append(None)
                current_element[index] = value
            elif isinstance(current_element, dict):
                current_element[index] = value
            else:
                raise TypeError("Cannot set value on non-list/dict element")
        else:
            if isinstance(current_element, list) and isinstance(index, int):
                # Extend the list if necessary
                while len(current_element) <= index:
                    current_element.append({})
                if current_element[index] is None:
                    current_element[index] = {}
                current_element = current_element[index]
            elif isinstance(current_element, dict):
                if index not in current_element:
                    current_element[index] = {}
                current_element = current_element[index]
            else:
                raise TypeError("Indices do not lead to a list/dict element")

def merge(iterables: List[Union[Dict, List, Iterable]], 
          dict_update: bool = False, 
          dict_sequence: bool = False, 
          sequence_separator: str = '_', 
          sort_list: bool = False, 
          custom_sort: Callable[[Any], Any] = None) -> Union[Dict, List]:
    if all(isinstance(it, Dict) for it in iterables):
        merged_dict = {}
        for d in iterables:
            for key, value in d.items():
                if key not in merged_dict or dict_update:
                    merged_dict[key] = value
                elif dict_sequence:
                    seq = 1
                    new_key = f"{key}{sequence_separator}{seq}"
                    while new_key in merged_dict:
                        seq += 1
                        new_key = f"{key}{sequence_separator}{seq}"
                    merged_dict[new_key] = value
        return merged_dict

    elif all(isinstance(it, (List, Iterable)) and not isinstance(it, str) for it in iterables):
        merged_list = list(chain(*iterables))
        if sort_list:
            if custom_sort:
                return sorted(merged_list, key=custom_sort)
            elif all(isinstance(item, int) for item in merged_list):
                return sorted(merged_list)
            else:
                return sorted(merged_list, key=lambda x: len(str(x)))
        return merged_list
    else:
        raise TypeError("All items in the input list must be of the same type, either Dict, List, or Iterable.")

def update(original: Union[Dict, List], updates: Union[Dict, List]) -> Union[Dict, List]:
    if isinstance(original, Dict) and isinstance(updates, Dict):
        updated = original.copy()
        for key, value in updates.items():
            updated.setdefault(key, value)
        return updated
    elif isinstance(original, List) and isinstance(updates, List):
        return original + [item for item in updates if item not in original]
    else:
        raise TypeError("Both arguments must be of the same type, either Dict or List.")

def filter_collection(collection: Union[Dict, List], condition: Callable[[Any], bool]) -> Union[Dict, List]:
    if isinstance(collection, Dict):
        return {k: v for k, v in collection.items() if condition((k, v))}
    elif isinstance(collection, List):
        return [item for item in collection if condition(item)]
    else:
        raise TypeError("The collection must be either a Dict or a List.")

# flatten
def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', 
                    max_depth: Union[int, None] = None, inplace: bool = False,
                    dict_only: bool = False) -> Dict:
    parent_key_tuple = tuple(parent_key.split(sep)) if parent_key else ()
    if inplace:
        _dynamic_flatten_in_place(obj, parent_key, sep, max_depth, dict_only=dict_only)
        return obj
    return dict(_dynamic_flatten_generator(obj, parent_key_tuple, sep, max_depth, dict_only=dict_only))

def _dynamic_flatten_in_place(obj: Any, parent_key: str = '', sep: str = '_', 
                             max_depth: Union[int, None] = None, 
                             current_depth: int = 0, dict_only: bool = False) -> None:
    if isinstance(obj, dict):
        keys_to_delete = []
        items = list(obj.items())  # Create a copy of the dictionary items

        for k, v in items:
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict) and (max_depth is None or current_depth < max_depth):
                _dynamic_flatten_in_place(v, new_key, sep, max_depth, current_depth + 1, dict_only)
                keys_to_delete.append(k)
                obj.update(v)
            elif not dict_only and (isinstance(v, list) or not isinstance(v, (dict, list))):
                obj[new_key] = v
                if parent_key:
                    keys_to_delete.append(k)

        for k in keys_to_delete:
            del obj[k]

def _dynamic_flatten_generator(obj: Any, parent_key: Tuple[str, ...], 
                               sep: str = '_', max_depth: Union[int, None] = None, 
                               current_depth: int = 0, dict_only: bool = False
                               ) -> Generator[Tuple[str, Any], None, None]:
    if max_depth is not None and current_depth > max_depth:
        yield sep.join(parent_key), obj
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = parent_key + (k,)
            yield from _dynamic_flatten_generator(v, new_key, sep, 
                                                  max_depth, current_depth + 1, dict_only)
    elif isinstance(obj, list) and not dict_only:
        for i, item in enumerate(obj):
            new_key = parent_key + (str(i),)
            yield from _dynamic_flatten_generator(item, new_key, sep, 
                                                  max_depth, current_depth + 1, dict_only)
    else:
        yield sep.join(parent_key), obj

def get_flattened_keys(obj: Any, sep: str = '_', max_depth: Union[int, None] = None, 
                       dict_only: bool = False, inplace: bool = False) -> List[str]:
    if inplace:
        # Work on a copy of the object to preserve the original
        obj_copy = deepcopy(obj)
        dynamic_flatten(obj_copy, sep=sep, max_depth=max_depth, inplace=True, dict_only=dict_only)
        return list(obj_copy.keys())
    else:
        return list(dynamic_flatten(obj, sep=sep, max_depth=max_depth, dict_only=dict_only).keys())

def flatten_list(l: List, dropna: bool = True) -> List:
    return list(_flatten_list_generator(l, dropna))

def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        elif i is not None or not dropna:
            yield i

# print    
def print_nested_list(nested_list: Union[List, Dict], indent: int = 0) -> None:
    for item in nested_list:
        if isinstance(item, list):
            print(" " * indent + "[")
            print_nested_list(item, indent + 2)
            print(" " * indent + "]")
        elif isinstance(item, dict):
            print(" " * indent + "{")
            for key, value in item.items():
                print(f"{' ' * (indent + 2)}{key}: {value}")
            print(" " * indent + "}")
        else:
            print(" " * indent + str(item))

# lists
def unique_elements(lst: List[Any]) -> List[Any]:
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def intersperse(lst: List[Any], value: Any) -> List[Any]:
    if not lst:
        return []
    return list(chain(*((item, value) for item in lst)))[:-1]

# unflatten
def _insert_with_dict_handling(result_list: Union[Dict, List], 
                               indices: List[Union[int, str]], 
                               value: Any, 
                               current_depth: int = 0):
    """
    Inserts a value into a nested list at the specified indices. If the index does not exist, 
    it creates the necessary structure (list) to accommodate the value at the specified index.

    Args:
        result_list (Union[Dict, List]): The list or dictionary to insert the value into.
        indices (List[Union[int, str]]): The indices where the value should be inserted.
        value (Any): The value to insert.
        current_depth (int, optional): The current depth in the nested list or dictionary. Defaults to 0.

    Examples:
        >>> _insert_with_dict_handling([[], []], [1, 0], 'a')
        >>> _insert_with_dict_handling([['a'], []], [1, 1], 'b')
    """
    for index in indices[:-1]:
        if isinstance(result_list, list):
            if len(result_list) <= index:
                result_list += [[]] * (index - len(result_list) + 1)
            result_list = result_list[index]
        elif isinstance(result_list, dict):
            result_list = result_list.setdefault(index, {})
        current_depth += 1
    last_index = indices[-1]
    if isinstance(result_list, list):
        if len(result_list) <= last_index:
            result_list += [None] * (last_index - len(result_list) + 1)
        result_list[last_index] = value
    else:
        result_list[last_index] = value

def unflatten_to_list(flat_dict: Dict[str, Any], sep: str = '_') -> List:
    """
    Converts a flat dictionary into a nested list structure. The keys of the dictionary are split 
    by the separator to get the indices for the nested list. The function then uses 
    _insert_with_dict_handling to insert the values from the dictionary into the nested list at 
    the appropriate indices.

    Args:
        flat_dict (Dict[str, Any]): The flat dictionary to convert.
        sep (str, optional): The separator to use when splitting the keys of the dictionary. Defaults to '_'.

    Returns:
        List: The nested list structure.

    Examples:
        >>> unflatten_to_list({'0': 'a', '1': 'b', '2': 'c'})
        ['a', 'b', 'c']
        >>> unflatten_to_list({'0_0': 'a', '0_1': 'b', '1_0': 'c', '1_1': 'd'})
        [['a', 'b'], ['c', 'd']]
    """
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.lstrip('-').isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
        
    return result_list

def dynamic_unflatten_dict(
    flat_dict: Dict[str, Any], sep: str = '_', 
    custom_logic: Union[Callable[[str], Any], None] = None, 
    max_depth: Union[int, None] = None
) -> Union[Dict, List]:
    
    def _handle_list_insert(sub_obj: Union[Dict, List], part: int, value: Any):
        # Ensure part index exists in the list, fill gaps with None
        while len(sub_obj) <= part:
            sub_obj.append(None)
        sub_obj[part] = value

    def _insert(sub_obj: Union[Dict, List], parts: List[Union[str, int]], 
                value: Any, current_depth: int = 0):
        for part in parts[:-1]:
            # Stop nesting further if max_depth is reached
            if max_depth is not None and current_depth >= max_depth:
                if isinstance(sub_obj, list):
                    _handle_list_insert(sub_obj, part, {parts[-1]: value})
                else:
                    sub_obj[part] = {parts[-1]: value}
                return

            if isinstance(part, str) and part.isdigit():
                part = int(part)
            if isinstance(part, int):
                # Ensure sub_obj is a list when part is an integer
                if not isinstance(sub_obj, list):
                    sub_obj = sub_obj.setdefault(part, [])
                while len(sub_obj) <= part:
                    sub_obj.append(None)
                if sub_obj[part] is None:
                    next_part = parts[parts.index(part) + 1]
                    is_next_part_digit = isinstance(next_part, str) and next_part.isdigit()
                    sub_obj[part] = [] if (max_depth is None or current_depth < max_depth - 1) and is_next_part_digit else {}
                sub_obj = sub_obj[part]
            else:
                sub_obj = sub_obj.setdefault(part, {})
            current_depth += 1

        last_part = parts[-1]
        if isinstance(last_part, int) and isinstance(sub_obj, list):
            _handle_list_insert(sub_obj, last_part, value)
        else:
            sub_obj[last_part] = value

    unflattened = {}
    for composite_key, value in flat_dict.items():
        parts = composite_key.split(sep)
        if custom_logic:
            parts = [custom_logic(part) for part in parts]
        else:
            parts = [int(part) if isinstance(part, str) and part.isdigit() else part for part in parts]
        _insert(unflattened, parts, value)

    if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
        max_index = max(unflattened.keys(), default=-1)
        return [unflattened.get(i) for i in range(max_index + 1)]
    if not unflattened:
        return {}
    return unflattened

# utility 
def is_iterable(obj: Any) -> bool:
    """
    Checks if the object is an iterable but not a string, bytes, or dictionary.

    Args:
        obj: The object to check.

    Returns:
        True if the object is an iterable, False otherwise.

    Examples:
        >>> is_iterable([1, 2, 3])
        True
        >>> is_iterable("string")
        False
    """
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, dict))