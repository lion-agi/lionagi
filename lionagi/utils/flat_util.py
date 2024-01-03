from typing import Dict, Iterable, List, Any, Callable, Generator, Tuple


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flattens a nested dictionary by concatenating keys.

    This function recursively flattens a nested dictionary by concatenating
    the keys of nested dictionaries with a separator. The default separator
    is an underscore (_).

    Parameters:
    d (dict): The dictionary to flatten.
    
    parent_key (str, optional): The base key to use for the current level of recursion.
        Defaults to an empty string, meaning no parent key, key cannot be a number 
        
    sep (str, optional): The separator to use when concatenating keys.
        Defaults to an underscore (_).

    Returns:
    dict: A new dictionary with flattened keys and corresponding values.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def flatten_list(l: List, dropna: bool = True) -> List:
    """
    Flattens a nested list into a single list of values.

    The function iterates over each element in the provided list. If an
    element is a list itself, the function is called recursively to flatten
    it. If the element is not a list, it is appended to the result list.
    Optionally, None values can be dropped from the result list.

    Parameters:
    l (list): The list to flatten, which may contain nested lists.
    
    dropna (bool, optional): Whether to exclude None values from the result list.
        Defaults to True.

    Returns:
    list: A new flattened list with or without None values based on the dropna parameter.
    """
    flat_list = []
    for i in l:
        if isinstance(i, list):
            flat_list.extend(flatten_list(i, dropna))
        elif i is not None or not dropna:
            flat_list.append(i)
    return flat_list

def change_separator(flat_dict, current_sep, new_sep):
    """
    Changes the separator in the keys of a flat dictionary.
    
    Parameters:
    flat_dict (dict): The dictionary with keys containing the current separator.
    current_sep (str): The current separator used in the dictionary keys.
    new_sep (str): The new separator to replace the current separator in the dictionary keys.
    
    Returns:
    dict: A new dictionary with the separators in the keys replaced.
    """
    return {
        k.replace(current_sep, new_sep): v 
        for k, v in flat_dict.items()
        }

def unflatten_dict(flat_dict: Dict, sep: str = '_') -> Dict:
    """
    Unflattens a dictionary where keys are strings that represent nested dictionary paths separated by 'sep'.
    
    Args:
    flat_dict (dict): A dictionary with keys as strings that represent paths.
    sep (str): The separator used in the keys of the flat dictionary.
    
    Returns:
    dict: A nested dictionary unflattened from the keys of the input dictionary.
    
    Raises:
    ValueError: If there are conflicting keys in the path.
    
    Example:
    >>> unflatten_dict({'a_0': 1, 'a_1': 2, 'b_x': 'X', 'b_y': 'Y'})
    {'a': [1, 2], 'b': {'x': 'X', 'y': 'Y'}}
    """
    result = {}
    for flat_key, value in flat_dict.items():
        parts = flat_key.split(sep)
        d = result
        for part in parts[:-1]:
            part = int(part) if part.isdigit() else part
            if part not in d:
                if isinstance(d, list):
                    d.append({})
                    d = d[-1]
                else:
                    d[part] = {}
            d = d[part] if not isinstance(d, list) else d[-1]
        last_part = parts[-1]
        last_part = int(last_part) if last_part.isdigit() else last_part
        if isinstance(d, list):
            d.append(value)
        elif last_part in d:
            raise ValueError(f"Conflicting keys detected. Key part '{last_part}' is already present.")
        else:
            d[last_part] = value
            
    # Convert dictionaries with contiguous integer keys starting from 0 to lists
    def dict_to_list(d: dict) -> dict:
        """
        Converts dictionaries with contiguous integer keys starting from 0 into lists.
        
        Args:
        d (dict): A dictionary that may have integer keys suitable for conversion to a list.
        
        Returns:
        dict or list: The input dictionary or a list if the dictionary keys match the criteria.
        """
        if isinstance(d, dict) and all(isinstance(k, int) and k >= 0 for k in d.keys()):
            keys = sorted(d.keys())
            if keys == list(range(len(keys))):
                return [dict_to_list(d[k]) for k in keys]
        if isinstance(d, dict):
            return {k: dict_to_list(v) for k, v in d.items()}
        return d
    
    result = dict_to_list(result)
    return result

def is_flattenable(obj: Any) -> bool:
    """
    Determines if the given object contains nested dictionaries or lists, making it suitable for flattening.
    
    Args:
    obj (object): The object to check for flattenable structures.
    
    Returns:
    bool: True if the object can be flattened (contains nested dicts or lists), False otherwise.
    """
    if isinstance(obj, dict):
        return any(isinstance(v, (dict, list)) for v in obj.values())
    elif isinstance(obj, list):
        return any(isinstance(i, (dict, list)) for i in obj)
    return False

def flatten_with_custom_logic(obj, logic_func=None, parent_key='', sep='_'):
    """
    Recursively flattens a nested dictionary or list and applies custom logic to the keys and values.

    Parameters:
    obj (dict | list): The dictionary or list to flatten.
    logic_func (callable, optional): A function that takes four arguments (parent_key, key, value, sep)
        and returns a tuple (new_key, new_value) after applying custom logic.
    parent_key (str): The base key to use for creating new keys.
    sep (str): The separator to use when joining nested keys.

    Returns:
    dict: A flattened dictionary with keys representing the nested paths and values from the original object.

    Example Usage:
    >>> sample_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    >>> flatten_with_custom_logic(sample_dict)
    {'a': 1, 'b_c': 2, 'b_d_e': 3}

    >>> sample_list = [1, 2, [3, 4]]
    >>> flatten_with_custom_logic(sample_list)
    {'0': 1, '1': 2, '2_0': 3, '2_1': 4}

    >>> def custom_logic(parent_key, key, value, sep='_'):
    ...     new_key = f"{parent_key}{sep}{key}".upper() if parent_key else key.upper()
    ...     return new_key, value * 2 if isinstance(value, int) else value
    >>> flatten_with_custom_logic(sample_dict, custom_logic)
    {'A': 2, 'B_C': 4, 'B_D_E': 6}
    """
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                if v:  # Check if the dictionary or list is not empty
                    items.update(flatten_with_custom_logic(v, logic_func, new_key, sep))
                else:  # Handle empty dictionaries and lists
                    items[new_key] = None
            else:
                if logic_func:
                    new_key, new_value = logic_func(parent_key, k, v, sep=sep)
                else:
                    new_value = v
                items[new_key] = new_value
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{str(i)}" if parent_key else str(i)  # Cast index to string
            if isinstance(item, (dict, list)):
                if item:  # Check if the dictionary or list is not empty
                    items.update(flatten_with_custom_logic(item, logic_func, new_key, sep))
                else:  # Handle empty lists
                    items[new_key] = None
            else:
                if logic_func:
                    new_key, new_value = logic_func(parent_key, str(i), item, sep=sep)
                else:
                    new_value = item
                items[new_key] = new_value
    return items

def dynamic_flatten(obj, parent_key='', sep='_', max_depth=None, current_depth=0):
    """
    Recursively flattens a nested dictionary or list, while allowing a maximum depth and custom separators.

    Parameters:
    obj (dict | list): The dictionary or list to flatten.
    parent_key (str): The base key to use for creating new keys.
    sep (str): The separator to use when joining nested keys.
    max_depth (int, optional): The maximum depth to flatten.
    current_depth (int): The current depth in the recursive call (used internally).

    Returns:
    dict: A flattened dictionary with keys representing the nested paths and values from the original object.

    Raises:
    TypeError: If the input object is neither a dictionary nor a list.

    Example Usage:
    >>> sample_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    >>> dynamic_flatten(sample_dict)
    {'a': 1, 'b_c': 2, 'b_d_e': 3}

    >>> sample_list = [1, 2, [3, 4]]
    >>> dynamic_flatten(sample_list)
    {'0': 1, '1': 2, '2_0': 3, '2_1': 4}

    >>> dynamic_flatten(sample_dict, max_depth=1)
    {'a': 1, 'b_c': 2, 'b_d': {'e': 3}}

    >>> dynamic_flatten(sample_dict, sep='.')
    {'a': 1, 'b.c': 2, 'b.d.e': 3}
    """
    items = []
    if isinstance(obj, dict):
        if not obj and parent_key:
            items.append((parent_key, obj))
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)) and (max_depth is None or current_depth < max_depth):
                items.extend(dynamic_flatten(v, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        if not obj and parent_key:
            items.append((parent_key, obj))
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(item, (dict, list)) and (max_depth is None or current_depth < max_depth):
                items.extend(dynamic_flatten(item, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, item))
    else:
        raise TypeError('Input object must be a dictionary or a list')
    
    return dict(items)

# def dynamic_unflatten_dict(flat_dict, sep='_', custom_logic=None, max_depth=None):
#     """
#     Unflattens a dictionary with flat keys into a nested dictionary or list.

#     :param flat_dict: A dictionary with flat keys that need to be nested.
#     :param sep: The separator used in the flat keys (default is '_').
#     :param custom_logic: A function that customizes the processing of keys.
#                          It takes a key part as input and returns the transformed key part.
#     :param max_depth: The maximum depth to which the dictionary should be nested.
#                       If None, there is no maximum depth.
#     :return: A nested dictionary or list based on the flat input dictionary.

#     The function dynamically unflattens a dictionary with keys that represent nested paths.
#     For example, the flat dictionary {'a_b_c': 1, 'a_b_d': 2} would be unflattened to
#     {'a': {'b': {'c': 1, 'd': 2}}}. If the keys can be converted to integers and suggest list indices,
#     the function produces lists instead of dictionaries. For example,
#     {'0_a': 'foo', '1_b': 'bar'} becomes [{'a': 'foo'}, {'b': 'bar'}].
#     """
    
#     def handle_list_insert(sub_obj, part, value):
#         # Ensure part index exists in the list, fill gaps with None
#         while len(sub_obj) <= part:
#             sub_obj.append(None)
        
#         sub_obj[part] = value

#     def insert(sub_obj, parts, value, max_depth, current_depth=0):
#         for part in parts[:-1]:
#             # Stop nesting further if max_depth is reached
#             if max_depth is not None and current_depth >= max_depth:
#                 sub_obj[part] = {parts[-1]: value}
#                 return
#             # Handle integer parts for list insertion
#             if isinstance(part, int):
#                 # Ensure part index exists in the list or dict, fill gaps with None
#                 while len(sub_obj) <= part:
#                     sub_obj.append(None)
#                 if sub_obj[part] is None:
#                     if current_depth < max_depth - 1 if max_depth else True:
#                         sub_obj[part] = [] if isinstance(parts[parts.index(part) + 1], int) else {}
#                 sub_obj = sub_obj[part]
#             else:
#                 # Handle string parts for dictionary insertion
#                 if part not in sub_obj:
#                     sub_obj[part] = {}
#                 sub_obj = sub_obj[part]
#             current_depth += 1
#         # Insert the value at the last part
#         last_part = parts[-1]
#         if isinstance(last_part, int) and isinstance(sub_obj, list):
#             handle_list_insert(sub_obj, last_part, value, max_depth, current_depth)
#         else:
#             sub_obj[last_part] = value

#     unflattened = {}
#     for composite_key, value in flat_dict.items():
#         parts = composite_key.split(sep)
#         if custom_logic:
#             parts = [custom_logic(part) for part in parts]
#         else:
#             parts = [int(part) if (isinstance(part, int) or part.isdigit()) else part for part in parts]
#         insert(unflattened, parts, value, max_depth)

#     # Convert top-level dictionary to a list if all keys are integers
#     if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
#         max_index = max(unflattened.keys(), default=-1)
#         return [unflattened.get(i) for i in range(max_index + 1)]
#     # Return an empty dictionary instead of converting to a list if unflattened is empty
#     if (unflattened == []) or (not unflattened):
#         return {}
#     return unflattened

def _insert_with_dict_handling(container, indices, value):
    """
    Helper function to insert a value into a nested container based on a list of indices.

    :param container: The container (list or dict) to insert the value into.
    :param indices: A list of indices indicating the path to the insertion point.
    :param value: The value to be inserted.
    """
    for i, index in enumerate(indices[:-1]):
        # Check if index is an integer and ensure the list is long enough
        if isinstance(index, int):
            # Extend the list if necessary
            while len(container) <= index:
                container.append(None)
            
            # Create a nested container if the current position is None
            if container[index] is None:
                next_index = indices[i + 1]
                
                # Determine the type of the next container based on the next index
                container[index] = {} if isinstance(next_index, str) else []
            
            # Update the reference to point to the nested container
            container = container[index]
            
        # If index is a string, work with dictionaries
        else:
            if index not in container:
                container[index] = {}
            container = container[index]
    
    # Insert value at the last index
    last_index = indices[-1]
    if isinstance(last_index, int):
      
      # Negative indices are not allowed in this context
        if last_index < 0:
            raise ValueError("Negative index is not allowed for list unflattening.")
          
        while len(container) <= last_index:
            container.append(None)
        container[last_index] = value
        
    else:
        if last_index in container and isinstance(container[last_index], list):
            raise ValueError("Overlapping keys are not allowed.")
        container[last_index] = value

def unflatten_to_list(flat_dict: Dict[str, Any], sep: str = '_') -> List:
    """
    Unflattens a dictionary with keys as string paths into a nested list structure.

    :param flat_dict: The flat dictionary to unflatten.
    :param sep: The separator used in the flat dictionary keys to indicate nesting.
    :return: A nested list that represents the unflattened structure.
    """
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.lstrip('-').isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
    return result_list

def flatten_iterable(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    """
    Flattens a nested iterable up to a specified maximum depth.

    Args:
    iterable: An iterable to flatten.
    max_depth: The maximum depth to flatten. If None, flattens completely.

    Yields:
    The flattened elements of the original iterable.
    """
    def _flatten(input_iterable: Iterable, current_depth: int) -> Generator[Any, None, None]:
        if isinstance(input_iterable, Iterable) and not isinstance(input_iterable, (str, bytes)):
            if max_depth is not None and current_depth >= max_depth:
                yield input_iterable
            else:
                for item in input_iterable:
                    yield from _flatten(item, current_depth + 1)
        else:
            yield input_iterable

    yield from _flatten(iterable, 0)

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:
    """
    Converts a nested iterable into a flattened list up to a specified maximum depth.

    Args:
    iterable: An iterable to flatten.
    max_depth: The maximum depth to flatten. If None, flattens completely.

    Returns:
    A list containing the flattened elements of the original iterable.
    """
    return list(flatten_iterable(iterable, max_depth))

def unflatten_dict_with_custom_logic(
    flat_dict: Dict[str, Any],
    logic_func: Callable[[str, Any], Tuple[str, Any]],
    sep: str = '_'
) -> Dict[str, Any]:
    """
    Unflattens a dictionary with keys as string paths into a nested dictionary structure
    while applying custom logic to each key and value.

    Args:
    flat_dict: The flat dictionary to unflatten.
    logic_func: A function that takes a key and a value and returns a tuple of modified key and value.
    sep: The separator used in the flat dictionary keys to indicate nesting.

    Returns:
    A nested dictionary that represents the unflattened structure with modified keys and values.
    """
    reconstructed = {}
    for flat_key, value in flat_dict.items():
        parts = flat_key.split(sep)
        d = reconstructed
        for part in parts[:-1]:
            modified_part, _ = logic_func(part, None)  # Modify only the key
            d = d.setdefault(modified_part, {})
        last_part = parts[-1]
        modified_last_part, modified_value = logic_func(last_part, value)
        d[modified_last_part] = modified_value
    return reconstructed

# def dynamic_unflatten(flat_dict, sep='_', custom_logic=None, max_depth=None):
#     """
#     Unflattens a dictionary with flat keys into a nested dictionary or list.

#     :param flat_dict: A dictionary with flat keys that need to be nested.
#     :param sep: The separator used in the flat keys (default is '_').
#     :param custom_logic: A function that customizes the processing of keys.
#                          It takes a key part as input and returns the transformed key part.
#     :param max_depth: The maximum depth to which the dictionary should be nested.
#                       If None, there is no maximum depth.
#     :return: A nested dictionary or list based on the flat input dictionary.

#     The function dynamically unflattens a dictionary with keys that represent nested paths.
#     For example, the flat dictionary {'a_b_c': 1, 'a_b_d': 2} would be unflattened to
#     {'a': {'b': {'c': 1, 'd': 2}}}. If the keys can be converted to integers and suggest list indices,
#     the function produces lists instead of dictionaries. For example,
#     {'0_a': 'foo', '1_b': 'bar'} becomes [{'a': 'foo'}, {'b': 'bar'}].
#     """
    
#     def handle_list_insert(sub_obj, part, value):
#         # Ensure part index exists in the list, fill gaps with None
#         while len(sub_obj) <= part:
#             sub_obj.append(None)
        
#         sub_obj[part] = value

#     def insert(sub_obj, parts, value, max_depth, current_depth=0):
#         for part in parts[:-1]:
#             # Stop nesting further if max_depth is reached
#             if max_depth is not None and current_depth >= max_depth:
#                 sub_obj[part] = {parts[-1]: value}
#                 return
#             # Handle integer parts for list insertion
#             if isinstance(part, int):
#                 # Ensure part index exists in the list or dict, fill gaps with None
#                 while len(sub_obj) <= part:
#                     sub_obj.append(None)
#                 if sub_obj[part] is None:
#                     if current_depth < max_depth - 1 if max_depth else True:
#                         sub_obj[part] = [] if isinstance(parts[parts.index(part) + 1], int) else {}
#                 sub_obj = sub_obj[part]
#             else:
#                 # Handle string parts for dictionary insertion
#                 if part not in sub_obj:
#                     sub_obj[part] = {}
#                 sub_obj = sub_obj[part]
#             current_depth += 1
#         # Insert the value at the last part
#         last_part = parts[-1]
#         if isinstance(last_part, int) and isinstance(sub_obj, list):
#             handle_list_insert(sub_obj, last_part, value, max_depth, current_depth)
#         else:
#             sub_obj[last_part] = value

#     unflattened = {}
#     for composite_key, value in flat_dict.items():
#         parts = composite_key.split(sep)
#         if custom_logic:
#             parts = [custom_logic(part) for part in parts]
#         else:
#             parts = [int(part) if (isinstance(part, int) or part.isdigit()) else part for part in parts]
#         insert(unflattened, parts, value, max_depth)

#     # Convert top-level dictionary to a list if all keys are integers
#     if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
#         max_index = max(unflattened.keys(), default=-1)
#         return [unflattened.get(i) for i in range(max_index + 1)]
#     # Return an empty dictionary instead of converting to a list if unflattened is empty
#     if (unflattened == []) or (not unflattened):
#         return {}
#     return unflattened

