# Internal Dependency = False
from typing import List, Any, Generator
from typing import Dict, Iterable, List, Any, Callable, Generator, Tuple, Union

# 1. Recursively Flatten a nested dict to a flat dict
def _flatten_dict_generator(d: Dict, parent_key: str = '', sep: str = '_') -> Generator[Tuple[str, Any], None, None]:
    """
    A generator that yields flattened key-value pairs from a nested dictionary.

    :param d: The dictionary to flatten.
    :param parent_key: The base key string for recursion.
    :param sep: Separator used between nested keys.
    :return: Generator of flattened key-value pairs.
    """
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            yield from _flatten_dict_generator(v, new_key, sep=sep)
        else:
            yield new_key, v

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flattens a nested dictionary into a single-level dictionary with keys as paths.

    :param d: The dictionary to flatten.
    :param parent_key: The base key string for recursion.
    :param sep: Separator used between nested keys.
    :return: A single-level dictionary with flattened keys.
    """
    return dict(_flatten_dict_generator(d, parent_key, sep))

# 2. Recursively flatten a nested list into a flat list
def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
    """
    A generator that yields flattened values from a nested list.

    :param l: The list to flatten.
    :param dropna: If True, None values will be dropped from the flattened list.
    :return: Generator of flattened values.
    """
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        elif i is not None or not dropna:
            yield i

def flatten_list(l: List, dropna: bool = True) -> List:
    """
    Flattens a nested list into a single-level list.

    :param l: The list to flatten.
    :param dropna: If True, None values will be dropped from the flattened list.
    :return: Flattened list.
    """
    return list(_flatten_list_generator(l, dropna))

# 3. Recursively flatten a nested structure (dict or list) into a flat dict
def _dynamic_flatten_generator(obj: Any, parent_key: str = '', sep: str = '_', max_depth: Union[int, None] = None, current_depth: int = 0) -> Generator[Tuple[str, Any], None, None]:
    """
    A generator that dynamically yields flattened key-value pairs from a nested structure.

    :param obj: The nested structure (dictionary or list) to flatten.
    :param parent_key: The base key for recursion (used internally).
    :param sep: Separator for nested keys.
    :param max_depth: The maximum depth to flatten.
    :param current_depth: The current depth in the structure (used internally).
    :return: Generator of flattened key-value pairs.
    """
    if max_depth is not None and current_depth > max_depth:
        yield parent_key, obj
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            yield from _dynamic_flatten_generator(v, new_key, sep, max_depth, current_depth + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            yield from _dynamic_flatten_generator(item, new_key, sep, max_depth, current_depth + 1)
    else:
        yield parent_key, obj

def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', max_depth: Union[int, None] = None) -> Dict:
    """
    Flattens a nested structure (dictionary or list) into a single-level dictionary with keys as paths.

    :param obj: The nested structure (dictionary or list) to flatten.
    :param parent_key: The base key for nested items.
    :param sep: Separator for nested keys.
    :param max_depth: The maximum depth to flatten.
    :return: Flattened dictionary.
    """
    return dict(_dynamic_flatten_generator(obj, parent_key, sep, max_depth))

# 4. dynamic unflatten a flat dict into a nested dict
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

    def _insert(sub_obj: Union[Dict, List], parts: List[Union[str, int]], value: Any, current_depth: int = 0):
        for part in parts[:-1]:
            # Stop nesting further if max_depth is reached
            if max_depth is not None and current_depth >= max_depth:
                sub_obj[part] = {parts[-1]: value}
                return

            part = int(part) if part.isdigit() else part
            if isinstance(part, int):
                while len(sub_obj) <= part:
                    sub_obj.append(None)
                if sub_obj[part] is None:
                    sub_obj[part] = [] if (max_depth is None or current_depth < max_depth - 1) and isinstance(parts[parts.index(part) + 1], int) else {}
                sub_obj = sub_obj[part]
            else:
                sub_obj[part] = sub_obj.get(part, {})
                sub_obj = sub_obj[part]
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
            parts = [int(part) if part.isdigit() else part for part in parts]
        _insert(unflattened, parts, value)

    if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
        max_index = max(unflattened.keys(), default=-1)
        return [unflattened.get(i) for i in range(max_index + 1)]
    if not unflattened:
        return {}
    return unflattened

# 5. dynamic unflatten a flat dictionary to a nested list
def _insert_with_dict_handling(result_list: Union[Dict, List], indices: List[Union[int, str]], value: Any, current_depth: int = 0):
    """ Helper function to insert value into result_list based on indices. """
    for index in indices[:-1]:
        if isinstance(result_list, list):
            while len(result_list) <= index:
                result_list.append({})
            result_list = result_list[index]
        elif isinstance(result_list, dict):
            result_list = result_list.setdefault(index, {})
        current_depth += 1
    last_index = indices[-1]
    if isinstance(result_list, list):
        while len(result_list) <= last_index:
            result_list.append(None)
        result_list[last_index] = value
    else:
        result_list[last_index] = value

def unflatten_to_list(flat_dict: Dict[str, Any], sep: str = '_') -> List:
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.lstrip('-').isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
    return result_list

# 6. flatten most iteralbes to a flat list
def flatten_iterable(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    
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
    return list(flatten_iterable(iterable, max_depth))

def to_list(input_: Any, flatten: bool = True, dropna: bool = False) -> List[Any]:
    
    if isinstance(input_, list) and flatten:
        input_ = flatten_list(input_)
        if dropna:
            input_ = [i for i in input_ if i is not None]
    elif isinstance(input_, Iterable) and not isinstance(input_, (str, dict)):
        try:
            input_ = list(input_)
        except:
            raise ValueError("Input cannot be converted to a list.")
    else:
        input_ = [input_]
    return input_








# # def dynamic_unflatten(flat_dict, sep='_', custom_logic=None, max_depth=None):
# #     """
# #     Unflattens a dictionary with flat keys into a nested dictionary or list.

# #     :param flat_dict: A dictionary with flat keys that need to be nested.
# #     :param sep: The separator used in the flat keys (default is '_').
# #     :param custom_logic: A function that customizes the processing of keys.
# #                          It takes a key part as input and returns the transformed key part.
# #     :param max_depth: The maximum depth to which the dictionary should be nested.
# #                       If None, there is no maximum depth.
# #     :return: A nested dictionary or list based on the flat input dictionary.

# #     The function dynamically unflattens a dictionary with keys that represent nested paths.
# #     For example, the flat dictionary {'a_b_c': 1, 'a_b_d': 2} would be unflattened to
# #     {'a': {'b': {'c': 1, 'd': 2}}}. If the keys can be converted to integers and suggest list indices,
# #     the function produces lists instead of dictionaries. For example,
# #     {'0_a': 'foo', '1_b': 'bar'} becomes [{'a': 'foo'}, {'b': 'bar'}].
# #     """
    
# #     def handle_list_insert(sub_obj, part, value):
# #         # Ensure part index exists in the list, fill gaps with None
# #         while len(sub_obj) <= part:
# #             sub_obj.append(None)
        
# #         sub_obj[part] = value

# #     def insert(sub_obj, parts, value, max_depth, current_depth=0):
# #         for part in parts[:-1]:
# #             # Stop nesting further if max_depth is reached
# #             if max_depth is not None and current_depth >= max_depth:
# #                 sub_obj[part] = {parts[-1]: value}
# #                 return
# #             # Handle integer parts for list insertion
# #             if isinstance(part, int):
# #                 # Ensure part index exists in the list or dict, fill gaps with None
# #                 while len(sub_obj) <= part:
# #                     sub_obj.append(None)
# #                 if sub_obj[part] is None:
# #                     if current_depth < max_depth - 1 if max_depth else True:
# #                         sub_obj[part] = [] if isinstance(parts[parts.index(part) + 1], int) else {}
# #                 sub_obj = sub_obj[part]
# #             else:
# #                 # Handle string parts for dictionary insertion
# #                 if part not in sub_obj:
# #                     sub_obj[part] = {}
# #                 sub_obj = sub_obj[part]
# #             current_depth += 1
# #         # Insert the value at the last part
# #         last_part = parts[-1]
# #         if isinstance(last_part, int) and isinstance(sub_obj, list):
# #             handle_list_insert(sub_obj, last_part, value, max_depth, current_depth)
# #         else:
# #             sub_obj[last_part] = value

# #     unflattened = {}
# #     for composite_key, value in flat_dict.items():
# #         parts = composite_key.split(sep)
# #         if custom_logic:
# #             parts = [custom_logic(part) for part in parts]
# #         else:
# #             parts = [int(part) if (isinstance(part, int) or part.isdigit()) else part for part in parts]
# #         insert(unflattened, parts, value, max_depth)

# #     # Convert top-level dictionary to a list if all keys are integers
# #     if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
# #         max_index = max(unflattened.keys(), default=-1)
# #         return [unflattened.get(i) for i in range(max_index + 1)]
# #     # Return an empty dictionary instead of converting to a list if unflattened is empty
# #     if (unflattened == []) or (not unflattened):
# #         return {}
# #     return unflattened



# def change_separator(flat_dict, current_sep, new_sep):
#     return {
#         k.replace(current_sep, new_sep): v 
#         for k, v in flat_dict.items()
#         }