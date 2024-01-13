import json
from typing import Dict, List, Tuple, Callable, Any

def merge_dicts(d1: Dict, d2: Dict) -> Dict:
    return {**d1, **d2}

def invert_dict(d: Dict) -> Dict:
    inverted = {}
    for key, value in d.items():
        if value not in inverted:
            inverted[value] = key
        else:
            if not isinstance(inverted[value], list):
                inverted[value] = [inverted[value]]
            inverted[value].append(key)
    return inverted

def deep_copy_dict(d: Dict) -> Dict:
    return json.loads(json.dumps(d))

def dict_to_tuples(d: Dict) -> List[Tuple]:
    return list(d.items())

def tuples_to_dict(tuples: List[Tuple]) -> Dict:
    return dict(tuples)

def filter_dict(d: Dict, condition: Callable[[Tuple[str, Any]], bool]) -> Dict:
    return {k: v for k, v in d.items() if condition((k, v))}

def update_dict(d1: Dict, d2: Dict) -> Dict:
    d = d1.copy()
    for k, v in d2.items():
        d.setdefault(k, v)
    return d

def dict_to_json_string(d: Dict) -> str:
    return json.dumps(d)

def json_string_to_dict(s: str) -> Dict:
    return json.loads(s)

def dict_keys_to_upper(d: Dict) -> Dict:
    return {k.upper(): v for k, v in d.items()}

from typing import Dict, Any, Union, Callable, List

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


from .generators import _flatten_iterable_generator
from typing import Any, List, Iterable, Set, Tuple, Iterator
from collections.abc import Iterable
from itertools import chain
import unittest
import csv
import binascii
from datetime import datetime
from dateutil import parser
import io
from typing import List, Union, Any, Optional
import unittest


def merge_sorted_lists(list1: List[int], list2: List[int]) -> List[int]:
    """Merge two sorted lists into one sorted list.

    Args:
        list1: The first sorted list.
        list2: The second sorted list.

    Returns:
        A merged and sorted list containing all elements from both input lists.

    Examples:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
        >>> merge_sorted_lists([], [2, 4, 6])
        [2, 4, 6]
    """
    merged_list = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            merged_list.append(list1[i])
            i += 1
        else:
            merged_list.append(list2[j])
            j += 1
    merged_list.extend(list1[i:])
    merged_list.extend(list2[j:])
    return merged_list

def deep_flatten(nested_list: List[Any]) -> List[Any]:
    """
    Flattens a nested list into a single list with no nested lists.

    Args:
        nested_list: A list potentially containing nested lists.

    Returns:
        A flattened list with all the nested elements in a single list.

    Examples:
        >>> deep_flatten([1, [2, [3, 4], 5]])
        [1, 2, 3, 4, 5]
        >>> deep_flatten([[1], 2, [[3, 4], 5], []])
        [1, 2, 3, 4, 5]
    """
    result = []
    stack = [list(nested_list)]
    while stack:
        current = stack.pop()
        while current:
            item = current.pop(0)
            if isinstance(item, list):
                stack.append(current)
                current = item
            else:
                result.append(item)
    return result


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

def filter_none(lst: List[Any]) -> List[Any]:
    """
    Removes None values from a list.

    Args:
        lst: The list to filter.

    Returns:
        A list with None values removed.

    Examples:
        >>> filter_none([1, None, 2, None, 3])
        [1, 2, 3]
    """
    return [item for item in lst if item is not None]

def to_set(iterable: Iterable[Any]) -> Set[Any]:
    """
    Converts an iterable to a set.

    Args:
        iterable: The iterable to convert.

    Returns:
        A set containing the elements of the iterable.

    Examples:
        >>> to_set([1, 2, 2, 3])
        {1, 2, 3}
    """
    return set(iterable)

def to_tuple(iterable: Iterable[Any]) -> Tuple[Any, ...]:
    """
    Converts an iterable to a tuple.

    Args:
        iterable: The iterable to convert.

    Returns:
        A tuple containing the elements of the iterable.

    Examples:
        >>> to_tuple([1, 2, 3])
        (1, 2, 3)
    """
    return tuple(iterable)

def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    """
    Breaks a list into chunks of a specified size.

    Args:
        lst: The list to break into chunks.
        size: The size of each chunk.

    Returns:
        A list of chunks, where each chunk is a list of elements.

    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def reverse_list(lst: List[Any]) -> List[Any]:
    """
    Reverses the elements of a list.

    Args:
        lst: The list to reverse.

    Returns:
        A list with the elements in reverse order.

    Examples:
        >>> reverse_list([1, 2, 3])
        [3, 2, 1]
    """
    return lst[::-1]

def unique_elements(lst: List[Any]) -> List[Any]:
    """
    Returns a list with unique elements, preserving the order.

    Args:
        lst: The list to extract unique elements from.

    Returns:
        A list with unique elements.

    Examples:
        >>> unique_elements([1, 2, 2, 3, 1])
        [1, 2, 3]
    """
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def merge_lists(*lists: List[Any]) -> List[Any]:
    """
    Merges multiple lists into one list.

    Args:
        *lists: Variable number of lists to merge.

    Returns:
        A single list containing all elements from the input lists.

    Examples:
        >>> merge_lists([1, 2], [3, 4], [5])
        [1, 2, 3, 4, 5]
    """
    return list(chain(*lists))

def intersperse(lst: List[Any], value: Any) -> List[Any]:
    """
    Intersperses a value between elements of a list.

    Args:
        lst: The list to intersperse.
        value: The value to intersperse between elements.

    Returns:
        A new list with the value interspersed between elements.

    Examples:
        >>> intersperse([1, 2, 3], 'a')
        [1, 'a', 2, 'a', 3]
    """
    if not lst:
        return []
    return list(chain(*((item, value) for item in lst)))[:-1]

def find_depth(nested_list):
    if not isinstance(nested_list, (list, dict)):
        return 0
    max_depth = 0
    if isinstance(nested_list, list):
        for item in nested_list:
            max_depth = max(max_depth, find_depth(item))
    elif isinstance(nested_list, dict):
        for value in nested_list.values():
            max_depth = max(max_depth, find_depth(value))
    return max_depth + 1

def get_value(nested_list, indices):
    current_element = nested_list
    for index in indices:
        if isinstance(current_element, list) and isinstance(index, int) and index < len(current_element):
            current_element = current_element[index]
        elif isinstance(current_element, dict) and index in current_element:
            current_element = current_element[index]
        else:
            return None  # Index out of bounds or not found
    return current_element


def set_value(nested_list, indices, value):
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



def flatten_list(l: List, dropna: bool = True) -> List:
    stack = l[::-1]  # Reverse the list to use it as a stack
    flattened = []
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item[::-1])  # Reverse and add nested list items to stack
        elif item is not None or not dropna:
            flattened.append(item)
    return flattened

def print_nested_list(nested_list, indent=0):
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
            
            
def flatten_list(nested_list: Union[List, Dict], parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flattens a nested list or dictionary into a flat dictionary with keys representing paths.

    Args:
        nested_list: The nested list or dictionary to flatten.
        parent_key: The base key to use for the current level of depth.
        sep: The separator to use between keys.

    Returns:
        A flat dictionary with keys representing the nested paths.

    Examples:
        >>> flatten_list([["a", "b"], "c"])
        {'0_0': 'a', '0_1': 'b', '1': 'c'}
        >>> flatten_list([None, ["a", "b"], "c"])
        {'1_0': 'a', '1_1': 'b', '2': 'c'}
    """
    items = []
    if not isinstance(nested_list, (list, dict)):
        return {parent_key: nested_list}
    if isinstance(nested_list, list):
        for i, item in enumerate(nested_list):
            if item is None:
                continue  # Skip None values
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_list(item, new_key, sep=sep).items())
    elif isinstance(nested_list, dict):
        for k, item in nested_list.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_list(item, new_key, sep=sep).items())
    return dict(items)

def print_nested_list(nested_list: Union[List, Dict], indent: int = 0) -> None:
    """
    Prints a nested list or dictionary in a human-readable format.

    Args:
        nested_list: The nested list or dictionary to print.
        indent: The indentation level (number of spaces) for the current depth.

    Examples:
        >>> print_nested_list([["a", "b"], "c"])
        [
          a
          b
        ]
        c
        >>> print_nested_list([None, ["a", "b"], "c"])
        None
        [
          a
          b
        ]
        c
    """
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

def find_depth(nested_list: Union[List, Dict]) -> int:
    """
    Finds the maximum depth of a nested list or dictionary.

    Args:
        nested_list: The nested list or dictionary to find the depth of.

    Returns:
        The maximum depth of the nested structure.

    Examples:
        >>> find_depth([["a", "b"], "c"])
        2
        >>> find_depth([None, ["a", "b"], "c"])
        2
    """
    if not isinstance(nested_list, (list, dict)):
        return 0
    max_depth = 0
    if isinstance(nested_list, list):
        for item in nested_list:
            max_depth = max(max_depth, find_depth(item))
    elif isinstance(nested_list, dict):
        for value in nested_list.values():
            max_depth = max(max_depth, find_depth(value))
    return max_depth + 1

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:
    """
    Flattens a nested iterable into a flat list up to a specified max_depth.

    Args:
        iterable: An iterable that may contain nested iterables.
        max_depth: An optional integer specifying the maximum depth to flatten. If None, flattens completely.

    Returns:
        A flat list containing all the items from the nested iterable.

    Examples:
        >>> flatten_iterable_to_list([1, [2, [3, 4]], 5])
        [1, 2, 3, 4, 5]
        >>> flatten_iterable_to_list([1, [2, [3, 4]], 5], max_depth=1)
        [1, 2, [3, 4], 5]
    """
    return list(_flatten_iterable_generator(iterable, max_depth))


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


from .generators import _dynamic_flatten_generator

# filename: dict_utilities.py
import json
from typing import Dict, List, Tuple, Callable, Any

def merge_dicts(d1: Dict, d2: Dict) -> Dict:
    return {**d1, **d2}

def invert_dict(d: Dict) -> Dict:
    inverted = {}
    for key, value in d.items():
        if value not in inverted:
            inverted[value] = key
        else:
            if not isinstance(inverted[value], list):
                inverted[value] = [inverted[value]]
            inverted[value].append(key)
    return inverted

def deep_copy_dict(d: Dict) -> Dict:
    return json.loads(json.dumps(d))

def dict_to_tuples(d: Dict) -> List[Tuple]:
    return list(d.items())

def tuples_to_dict(tuples: List[Tuple]) -> Dict:
    return dict(tuples)

def filter_dict(d: Dict, condition: Callable[[Tuple[str, Any]], bool]) -> Dict:
    return {k: v for k, v in d.items() if condition((k, v))}

def update_dict(d1: Dict, d2: Dict) -> Dict:
    d = d1.copy()
    for k, v in d2.items():
        d.setdefault(k, v)
    return d

def dict_to_json_string(d: Dict) -> str:
    return json.dumps(d)

def json_string_to_dict(s: str) -> Dict:
    return json.loads(s)

def dict_keys_to_upper(d: Dict) -> Dict:
    return {k.upper(): v for k, v in d.items()}

from typing import Dict, Any, Union, Callable, List

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

from typing import Any, Dict, Union, Tuple, Optional

def flatten_structure(obj: Any, parent_key: str = '', sep: str = '_',
                      max_depth: Union[int, None] = None, 
                      current_depth: int = 0) -> Dict[str, Any]:
    flattened = {}
    if max_depth is not None and current_depth > max_depth:
        return {parent_key: obj}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            flattened.update(flatten_structure(v, new_key, sep, max_depth, current_depth + 1))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            flattened.update(flatten_structure(item, new_key, sep, max_depth, current_depth + 1))
    else:
        flattened[parent_key] = obj
    return flattened

def key_exists_get_value(structure: Dict[str, Any], key: str, sep: str = '_') -> Tuple[bool, Optional[Any]]:
    flattened = flatten_structure(structure, sep=sep)
    if key in flattened:
        return True, flattened[key]
    if sep in key:
        composite_key = key.replace(sep, '_')
        if composite_key in flattened:
            return True, flattened[composite_key]
    return False, None


def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', 
                    max_depth: Union[int, None] = None) -> Dict:
    parent_key_tuple = tuple(parent_key.split(sep)) if parent_key else ()
    return dict(_dynamic_flatten_generator(obj, parent_key_tuple, sep, max_depth))


# New function to flatten only dictionaries
def flatten_dicts_only(obj: Any, parent_key: str = '', sep: str = '_') -> Dict:
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            result.update(flatten_dicts_only(v, new_key, sep))
        return result
    else:
        return {parent_key: obj} if parent_key else {}

# New function to get a list of keys from the flattened dictionary
def get_flattened_keys(obj: Any, sep: str = '_') -> List[str]:
    return list(dynamic_flatten(obj, sep=sep).keys())

import json
import unittest
from typing import Dict, List, Tuple, Callable, Any

def merge_dicts(d1: Dict, d2: Dict) -> Dict:
    """Merge two dictionaries into one.

    Args:
        d1 (Dict): The first dictionary.
        d2 (Dict): The second dictionary.

    Returns:
        Dict: The merged dictionary.

    Examples:
        >>> merge_dicts({'a': 1}, {'b': 2})
        {'a': 1, 'b': 2}
    """
    return {**d1, **d2}

def invert_dict(d: Dict) -> Dict:
    """Invert a dictionary, swapping keys and values.

    Args:
        d (Dict): The dictionary to invert.

    Returns:
        Dict: The inverted dictionary.

    Examples:
        >>> invert_dict({'a': 1, 'b': 1, 'c': 2})
        {1: ['a', 'b'], 2: 'c'}
    """
    inverted = {}
    for key, value in d.items():
        if value not in inverted:
            inverted[value] = key
        else:
            if not isinstance(inverted[value], list):
                inverted[value] = [inverted[value]]
            inverted[value].append(key)
    return inverted

def deep_copy_dict(d: Dict) -> Dict:
    """Perform a deep copy of a dictionary.

    Args:
        d (Dict): The dictionary to copy.

    Returns:
        Dict: The deep copied dictionary.

    Examples:
        >>> original = {'a': {'b': 1}}
        >>> copy = deep_copy_dict(original)
        >>> copy == original and copy is not original
        True
    """
    return json.loads(json.dumps(d))

def dict_to_tuples(d: Dict) -> List[Tuple]:
    """Convert a dictionary into a list of tuples (key-value pairs).

    Args:
        d (Dict): The dictionary to convert.

    Returns:
        List[Tuple]: The list of tuples.

    Examples:
        >>> dict_to_tuples({'a': 1, 'b': 2})
        [('a', 1), ('b', 2)]
    """
    return list(d.items())

def tuples_to_dict(tuples: List[Tuple]) -> Dict:
    """Convert a list of tuples (key-value pairs) into a dictionary.

    Args:
        tuples (List[Tuple]): The list of tuples to convert.

    Returns:
        Dict: The dictionary.

    Examples:
        >>> tuples_to_dict([('a', 1), ('b', 2)])
        {'a': 1, 'b': 2}
    """
    return dict(tuples)

def filter_dict(d: Dict, condition: Callable[[Tuple[str, Any]], bool]) -> Dict:
    """Filter a dictionary based on a condition function.

    Args:
        d (Dict): The dictionary to filter.
        condition (Callable[[Tuple[str, Any]], bool]): The condition function.

    Returns:
        Dict: The filtered dictionary.

    Examples:
        >>> filter_dict({'a': 1, 'b': 2}, lambda item: item[1] > 1)
        {'b': 2}
    """
    return {k: v for k, v in d.items() if condition((k, v))}

def update_dict(d1: Dict, d2: Dict) -> Dict:
    """Update a dictionary with key-value pairs from another dictionary without overwriting existing keys.

    Args:
        d1 (Dict): The original dictionary.
        d2 (Dict): The dictionary with updates.

    Returns:
        Dict: The updated dictionary.

    Examples:
        >>> update_dict({'a': 1}, {'a': 2, 'b': 2})
        {'a': 1, 'b': 2}
    """
    d = d1.copy()
    for k, v in d2.items():
        d.setdefault(k, v)
    return d

def dict_to_json_string(d: Dict) -> str:
    """Convert a dictionary to a JSON string.

    Args:
        d (Dict): The dictionary to convert.

    Returns:
        str: The JSON string.

    Examples:
        >>> dict_to_json_string({'a': 1})
        '{"a": 1}'
    """
    return json.dumps(d)

def json_string_to_dict(s: str) -> Dict:
    """Convert a JSON string to a dictionary.

    Args:
        s (str): The JSON string to convert.

    Returns:
        Dict: The dictionary.

    Examples:
        >>> json_string_to_dict('{"a": 1}')
        {'a': 1}
    """
    return json.loads(s)

def dict_keys_to_upper(d: Dict) -> Dict:
    """Convert all keys in a dictionary to uppercase.

    Args:
        d (Dict): The dictionary with keys to convert.

    Returns:
        Dict: The dictionary with uppercase keys.

    Examples:
        >>> dict_keys_to_upper({'a': 1, 'b': 2})
        {'A': 1, 'B': 2}
    """
    return {k.upper(): v for k, v in d.items()}

def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', 
                    max_depth: Union[int, None] = None) -> Dict:
    """
    Flattens a nested dictionary or list into a flat dictionary.

    Args:
        obj: The object to flatten, which can be a dictionary, list, or any other type.
        parent_key: A string representing the initial path to the object.
        sep: The separator to use when joining keys.
        max_depth: The maximum depth to flatten. If None, flattens completely.

    Returns:
        A flat dictionary with keys representing the path to the values.

    Examples:
        >>> dynamic_flatten({'a': {'b': 'c'}})
        {'a_b': 'c'}
        >>> dynamic_flatten([1, [2, 3]], sep='/')
        {'0': 1, '1/0': 2, '1/1': 3}
    """
    parent_key_tuple = tuple(parent_key.split(sep)) if parent_key else ()
    return dict(_dynamic_flatten_generator(obj, parent_key_tuple, sep, max_depth))



def dynamic_flatten_iterative(obj: Any, parent_key: str = '', sep: str = '_', 
                              max_depth: Union[int, None] = None) -> Dict:
    queue = deque([(obj, parent_key, 0)])
    result = {}

    while queue:
        obj, parent_key, current_depth = queue.popleft()

        if max_depth is not None and current_depth > max_depth:
            result[parent_key] = obj
            continue

        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                queue.append((v, new_key, current_depth + 1))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                queue.append((item, new_key, current_depth + 1))
        else:
            result[parent_key] = obj

    return result

def dynamic_flatten_in_place(obj: Any, parent_key: str = '', sep: str = '_', 
                             max_depth: Union[int, None] = None) -> None:
    keys_to_delete = []

    for k, v in list(obj.items()):  # Create a copy of the dictionary items
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict) and (max_depth is None or max_depth > 0):
            dynamic_flatten_in_place(v, new_key, sep, 
                                     None if max_depth is None else max_depth - 1)
            keys_to_delete.append(k)
        else:
            obj[new_key] = v

    for k in keys_to_delete:
        del obj[k]

def dynamic_unflatten(obj: Dict, sep: str = '_') -> Any:
    result = {}

    for k, v in obj.items():
        keys = k.split(sep)
        current_dict = result

        for key in keys[:-1]:
            current_dict = current_dict.setdefault(key, {})

        current_dict[keys[-1]] = v

    return result


from typing import (Any, Callable, Dict, Generator, Iterable, 
                    List, Optional, Tuple, Type, Union)

from dateutil import parser

def _task_id_generator() -> Generator[int, None, None]:
    """Generate an incremental sequence of integers starting from 0.

    Yields:
        The next integer in the sequence.

    Examples:
        gen = _task_id_generator()
        next(gen)  # Yields 0
        next(gen)  # Yields 1
    """
    task_id = 0
    while True:
        yield task_id
        task_id += 1
        
def _flatten_dict_generator(d: Dict, parent_key: str = '', sep: str = '_'
                            ) -> Generator[Tuple[str, Any], None, None]:
    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            yield from _flatten_dict_generator(v, new_key, sep=sep)
        else:
            yield new_key, v
            
def _flatten_iterable_generator(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    """
    A generator function that flattens a nested iterable up to a specified max_depth.

    Args:
        iterable: An iterable that may contain nested iterables.
        max_depth: An optional integer specifying the maximum depth to flatten. If None, flattens completely.

    Yields:
        The next flattened item from the iterable.

    Examples:
        >>> list(_flatten_iterable_generator([1, [2, [3, 4]], 5]))
        [1, 2, 3, 4, 5]
        >>> list(_flatten_iterable_generator([1, [2, [3, 4]], 5], max_depth=1))
        [1, 2, [3, 4], 5]
    """
    stack = [(iter(iterable), 0)]
    while stack:
        iterator, current_depth = stack.pop()
        for item in iterator:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                if max_depth is None or current_depth < max_depth:
                    # Process nested iterables by adding them to the stack
                    stack.append((iter(item), current_depth + 1))
                else:
                    yield item
            else:
                yield item
            

def _dynamic_flatten_generator(obj: Any, parent_key: Tuple[str, ...] = (), 
                               sep: str = '_', max_depth: Union[int, None] = None, 
                               current_depth: int = 0
                               ) -> Generator[Tuple[str, Any], None, None]:
    """
    A generator function that recursively flattens a nested dictionary or list.

    Args:
        obj: The object to flatten, which can be a dictionary, list, or any other type.
        parent_key: A tuple representing the path to the current object.
        sep: The separator to use when joining keys.
        max_depth: The maximum depth to flatten. If None, flattens completely.
        current_depth: The current depth in the recursive call stack.

    Yields:
        Tuples of (key, value) where key is a string representing the path to the value.

    Examples:
        >>> list(_dynamic_flatten_generator({'a': {'b': 'c'}}))
        [('a_b', 'c')]
        >>> list(_dynamic_flatten_generator([1, [2, 3]], sep='/'))
        [('0', 1), ('1/0', 2), ('1/1', 3)]
    """
    if max_depth is not None and current_depth > max_depth:
        yield sep.join(parent_key), obj
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = parent_key + (k,)
            yield from _dynamic_flatten_generator(v, new_key, sep, 
                                                  max_depth, current_depth + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = parent_key + (str(i),)
            yield from _dynamic_flatten_generator(item, new_key, sep, 
                                                  max_depth, current_depth + 1)
    else:
        yield sep.join(parent_key), obj
        
def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        elif i is not None or not dropna:
            yield i