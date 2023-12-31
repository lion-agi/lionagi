

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def flatten_list(l: list, dropna: bool = True) -> list:
    flat_list = []
    for i in l:
        if isinstance(i, list):
            flat_list.extend(flatten_list(i, dropna))
        elif i is not None or not dropna:
            flat_list.append(i)
    return flat_list

def flatten(obj, parent_key='', sep='_', max_depth=None, current_depth=0, logic_func=None):
    items = []
    if max_depth is not None and current_depth >= max_depth:
        return {parent_key: obj} if parent_key else obj

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)) and (logic_func is None or logic_func(k, v)):
                items.extend(flatten(v, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(item, (dict, list)) and (logic_func is None or logic_func(i, item)):
                items.extend(flatten(item, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, item))
    else:
        return {parent_key: obj}

    return dict(items)

def unflatten_dict(flat_dict, sep='_'):
    result = {}
    for flat_key, value in flat_dict.items():
        parts = flat_key.split(sep)
        d = result
        for part in parts[:-1]:
            part = int(part) if part.isdigit() else part
            if part not in d or not isinstance(d[part], (dict, list)):
                d[part] = [] if isinstance(part, int) else {}
            d = d[part]
        last_part = parts[-1]
        last_part = int(last_part) if last_part.isdigit() else last_part
        d[last_part] = value
    return result

def unflatten_to_list(flat_dict, sep='_'):
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.isdigit() else p for p in flat_key.split(sep)]
        lst = result_list
        for index in indices[:-1]:
            while len(lst) <= index:
                lst.append([])
            lst = lst[index]
        lst[indices[-1]] = value
    return result_list

def unflatten_complex_structure(flat_obj, sep='_'):
    if isinstance(flat_obj, dict):
        return unflatten_dict(flat_obj, sep)
    elif isinstance(flat_obj, list):
        return unflatten_to_list({f"{i}": v for i, v in enumerate(flat_obj)}, sep)
    else:
        raise TypeError("Object must be a flattened dictionary or list.")

def change_separator(flat_dict, current_sep, new_sep):
    return {k.replace(current_sep, new_sep): v for k, v in flat_dict.items()}







































from typing import Any, Dict, Union, Iterable, List

def flatten(data, max_depth=None, path_preservation=False, custom_logic=None):
    def _flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, MutableMapping):
                if max_depth is None or max_depth > 1:
                    items.extend(_flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            elif isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
                if max_depth is None or max_depth > 1:
                    items.extend(_flatten_list(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            else:
                items.append((new_key, v))
        return dict(items)

    def _flatten_list(lst, parent_key='', sep='.'):
        items = {}
        for i, v in enumerate(lst):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(v, MutableMapping):
                if max_depth is None or max_depth > 1:
                    items.update(_flatten_dict(v, new_key, sep=sep))
                else:
                    items[new_key] = v
            elif isinstance(v, Iterable) and not isinstance(v, (str, bytes)):
                if max_depth is None or max_depth > 1:
                    items.update(_flatten_list(v, new_key, sep=sep))
                else:
                    items[new_key] = v
            else:
                items[new_key] = v
        return items

    if isinstance(data, MutableMapping):
        return _flatten_dict(data)
    elif isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        return _flatten_list(data)
    else:
        raise TypeError('Input data must be a dictionary or an iterable')

def _unflatten_dict(d, sep='.'):
    result_dict = {}
    for k, v in d.items():
        parts = k.split(sep)
        sub_dict = result_dict
        for part in parts[:-1]:
            if part.isdigit():
                part = int(part)
                if part not in sub_dict or not isinstance(sub_dict[part], dict):
                    sub_dict[part] = {}
            else:
                if part not in sub_dict:
                    sub_dict[part] = {}
            sub_dict = sub_dict[part]
        last_part = parts[-1]
        if last_part.isdigit():
            last_part = int(last_part)
            sub_dict[last_part] = v
        else:
            sub_dict[last_part] = v
    return result_dict

def unflatten(flat_obj, sep='.'):
    if isinstance(flat_obj, dict):
        return _unflatten_dict(flat_obj, sep)
    else:
        raise TypeError("Object must be a flattened dictionary.")

def flatten_iterable_to_list(iterable, max_depth=None):
    if not isinstance(iterable, Iterable) or isinstance(iterable, (str, bytes)):
        return [iterable]
    flattened = []
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            if max_depth is None or max_depth > 1:
                flattened.extend(flatten_iterable_to_list(item, None if max_depth is None else max_depth-1))
            else:
                flattened.append(item)
        else:
            flattened.append(item)
    return flattened

def dynamic_flatten(obj, parent_key='', sep='_', max_depth=None, current_depth=0):
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)) and (max_depth is None or current_depth < max_depth):
                items.extend(dynamic_flatten(v, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(item, (dict, list)) and (max_depth is None or current_depth < max_depth):
                items.extend(dynamic_flatten(item, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, item))
    else:
        raise TypeError('Input object must be a dictionary or a list')
    return dict(items)
from typing import Any, Callable, Dict, List, Union

def dynamic_flatten(
    obj: Union[Dict, List, Any], 
    parent_key: str = '', 
    sep: str = '_', 
    max_depth: int = None, 
    current_depth: int = 0, 
    custom_logic: Callable = None
) -> Dict:
    """
    Dynamically flattens a complex, nested data structure into a single level dictionary.
    Allows for custom logic to be applied at each level of flattening.
    """
    items = []  # List to collect all the items that are being flattened

    # Base case: if max_depth is reached, or the object is not a list or dict, stop the recursion
    if max_depth is not None and current_depth >= max_depth or not isinstance(obj, (dict, list)):
        return {parent_key: obj}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if custom_logic:  # Apply custom logic if provided
                new_key, v = custom_logic(new_key, v)
            items.extend(dynamic_flatten(v, new_key, sep, max_depth, current_depth + 1, custom_logic).items())
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(dynamic_flatten(item, new_key, sep, max_depth, current_depth + 1, custom_logic).items())
    
    return dict(items)


def dynamic_unflatten(
    flat_dict: Dict[str, Any], 
    sep: str = '_', 
    custom_logic: Callable = None
) -> Union[Dict, Any]:
    """
    Dynamically reconstructs the original structure from a flattened dictionary.
    Allows for custom logic to be applied during unflattening.
    """
    reconstructed = {}
    for flat_key, value in flat_dict.items():
        parts = flat_key.split(sep)
        d = reconstructed
        for part in parts[:-1]:
            part = part if not custom_logic else custom_logic(part)
            if part.isdigit():
                part = int(part)  # Convert parts back to integers if possible (for list indices)
            d = d.setdefault(part, {})
        last_part = parts[-1]
        last_part = last_part if not custom_logic else custom_logic(last_part)
        if last_part.isdigit():
            last_part = int(last_part)
        d[last_part] = value
    return reconstructed









def flatten(obj: Union[dict, list], parent_key: str = '', sep: str = '_', max_depth: int = None, current_depth: int = 0, logic_func: Callable = None) -> Union[dict, list]:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if (isinstance(v, (dict, list)) and 
                (max_depth is None or current_depth < max_depth) and 
                (logic_func is None or logic_func(k, v))):
                items.extend(flatten(v, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if (isinstance(item, (dict, list)) and 
                (max_depth is None or current_depth < max_depth) and 
                (logic_func is None or logic_func(i, item))):
                items.extend(flatten(item, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, item))
    return dict(items) if isinstance(obj, dict) else list(dict(items).values())


def _handle_list_in_dict(d, part, next_part):
    part = int(part)  # Convert to integer index for lists
    if isinstance(d, dict):
        d = d.setdefault(part, [])
    while len(d) < next_part + 1:
        d.append({})
    return d

def _unflatten_dict_recursive(flat_dict, sep, d, parts):
    for part in parts[:-1]:
        next_part = parts[parts.index(part) + 1]
        if part.isdigit() and next_part.isdigit():
            d = _handle_list_in_dict(d, part, int(next_part))
        else:
            d = d.setdefault(part, {})
    last_key = parts[-1]
    last_key = int(last_key) if last_key.isdigit() else last_key
    d[last_key] = flat_dict[sep.join(parts)]

def unflatten_dict(flat_dict: dict, sep: str = '_') -> dict:
    result = {}
    for flat_key, value in flat_dict.items():
        _unflatten_dict_recursive(flat_dict, sep, result, flat_key.split(sep))
    return result

def _insert_with_dict_handling(lst, indices, value):
    for index in indices[:-1]:
        while len(lst) <= index:
            lst.append({} if isinstance(indices[indices.index(index) + 1], str) else [])
        lst = lst[index]
    lst[indices[-1]] = value

def unflatten_to_list(flat_dict: dict, sep: str = '_') -> list:
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
    return result_list

def unflatten_complex_structure(flat_obj: Union[dict, list], sep: str = '_') -> Union[dict, list]:
    if isinstance(flat_obj, dict):
        return unflatten_dict(flat_obj, sep)
    elif isinstance(flat_obj, list):
        return unflatten_to_list(dict(enumerate(flat_obj)), sep)
    else:
        raise TypeError("Object must be a flattened dictionary or list.")

def change_separator(flat_dict: dict, new_sep: str) -> dict:
    return {k.replace('_', new_sep): v for k, v in flat_dict.items()}

def get_keys(d: dict) -> List[str]:
    return list(d.keys())

def is_flattenable(obj: Any) -> bool:
    if isinstance(obj, dict):
        return any(isinstance(v, (dict, list)) for v in obj.values())
    elif isinstance(obj, list):
        return any(isinstance(i, (dict, list)) for i in obj)
    return False

def flatten_with_custom_logic(obj: Union[dict, list], logic_func: Callable, parent_key: str = '', sep: str = '_', **kwargs) -> Union[dict, list]:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key, new_value = logic_func(parent_key, k, v, **kwargs)
            if isinstance(v, (dict, list)):
                items.extend(flatten_with_custom_logic(v, logic_func, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, new_value))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key, new_value = logic_func(parent_key, None, item, **kwargs)
            items.append((f"{new_key}{sep}{i}", new_value))
    return dict(items)

def flatten_with_max_depth(obj: Union[dict, list], max_depth: int, current_depth: int = 0, parent_key: str = '', sep: str = '_', **kwargs) -> dict:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)) and current_depth < max_depth:
                items.extend(flatten_with_max_depth(v, max_depth, current_depth + 1, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(item, (dict, list)) and current_depth < max_depth:
                items.extend(flatten_with_max_depth(item, max_depth, current_depth + 1, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, item))
    return dict(items)

def unflatten_dict_with_custom_logic(flat_dict: dict, logic_func: Callable, sep: str = '_') -> dict:
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

def unflatten_complex_structure(flat_obj: Union[dict, list], sep: str = '_', logic_func: Callable = None) -> Union[dict, list]:
    if isinstance(flat_obj, dict):
        return unflatten_dict_with_custom_logic(flat_obj, logic_func, sep) if logic_func else unflatten_dict(flat_obj, sep)
    elif isinstance(flat_obj, list):
        # Convert list to dict for unflattening
        indexed_flat_obj = {f"{i}": v for i, v in enumerate(flat_obj)}
        return unflatten_to_list(indexed_flat_obj, sep)
    else:
        raise TypeError("Object must be a flattened dictionary or list.")

def flatten_iterable(iterable: Iterable, max_depth: int = None) -> Iterable:

    def _flatten(input_iterable, current_depth):
        if max_depth is not None and current_depth >= max_depth:
            yield input_iterable
        else:
            for item in input_iterable:
                if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                    yield from _flatten(item, current_depth + 1)
                else:
                    yield item
    return _flatten(iterable, 0)

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:

    return list(flatten_iterable(iterable, max_depth))

def flatten_iterable_generator(iterable: Iterable) -> Generator:

    return flatten_iterable(iterable)

def flatten_interface(operation: str, obj: Any, **kwargs) -> Any:

    operations = {
        'flatten': flatten,
        'unflatten': unflatten_complex_structure,
        'flatten_dict': flatten_dict,
        'flatten_list': flatten_list,
        'unflatten_dict': unflatten_dict,
        'unflatten_to_list': unflatten_to_list,
        'flatten_with_custom_logic': flatten_with_custom_logic,
        'flatten_with_path_preservation': flatten_with_path_preservation,
        'flatten_with_max_depth': flatten_with_max_depth,
        # Add other operations as needed
    }

    if operation in operations:
        return operations[operation](obj, **kwargs)
    else:
        raise ValueError(f"Unsupported operation: {operation}")



from collections.abc import Iterable
from typing import Any, Callable, Union, List, Dict

def flatten(obj: Union[Dict, List], parent_key: str = '', sep: str = '_', max_depth: int = None, current_depth: int = 0) -> Dict:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if (isinstance(v, (dict, list)) and (max_depth is None or current_depth < max_depth)):
                items.extend(flatten(v, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if (isinstance(item, (dict, list)) and (max_depth is None or current_depth < max_depth)):
                items.extend(flatten(item, new_key, sep, max_depth, current_depth + 1).items())
            else:
                items.append((new_key, item))
    return dict(items)

def unflatten(flat_dict: Dict[str, Any], sep: str = '_') -> Union[Dict, List]:
    result = {}
    for k, v in flat_dict.items():
        parts = k.split(sep)
        d = result
        for key in parts[:-1]:
            try:
                key = int(key)  # Convert to integer if possible for list indices
            except ValueError:
                pass
            d = d.setdefault(key, {})
        last_key = parts[-1]
        try:
            last_key = int(last_key)
            if not isinstance(d, list):
                d[last_key] = []  # Initialize as list if last_key is int
        except ValueError:
            pass
        d[last_key] = v
    return result if not isinstance(result, list) else result[0]

def flatten_iterable(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    def _flatten(input_iterable, current_depth):
        if max_depth is not None and current_depth >= max_depth:
            yield input_iterable
        else:
            for item in input_iterable:
                if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                    yield from _flatten(item, current_depth + 1)
                else:
                    yield item
    yield from _flatten(iterable, 0)

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:
    return list(flatten_iterable(iterable, max_depth))

def flatten_interface(operation: str, obj: Any, **kwargs) -> Any:
    operations = {
        'flatten': flatten,
        'unflatten': unflatten,
        'flatten_iterable_to_list': flatten_iterable_to_list,
        # Add other operations as needed
    }
    if operation in operations:
        return operations[operation](obj, **kwargs)
    raise ValueError(f"Unsupported operation: {operation}")

from collections.abc import Iterable
from typing import List, Any, Union, Callable, Generator, Tuple

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def flatten_list(l: list, dropna: bool = True) -> list:
    flat_list = []
    for i in l:
        if isinstance(i, list):
            flat_list.extend(flatten_list(i, dropna))
        elif i is not None or not dropna:
            flat_list.append(i)
    return flat_list

def flatten(obj: Union[dict, list], parent_key: str = '', sep: str = '_', max_depth: int = None, current_depth: int = 0, logic_func: Callable = None) -> Union[dict, list]:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if (isinstance(v, (dict, list)) and 
                (max_depth is None or current_depth < max_depth) and 
                (logic_func is None or logic_func(k, v))):
                items.extend(flatten(v, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if (isinstance(item, (dict, list)) and 
                (max_depth is None or current_depth < max_depth) and 
                (logic_func is None or logic_func(i, item))):
                items.extend(flatten(item, new_key, sep, max_depth, current_depth + 1, logic_func).items())
            else:
                items.append((new_key, item))
    return dict(items) if isinstance(obj, dict) else list(dict(items).values())

def _handle_list_in_dict(d, part, next_part):
    part = int(part)  # Convert to integer index for lists
    if isinstance(d, dict):
        d = d.setdefault(part, [])
    while len(d) < next_part + 1:
        d.append({})
    return d

def _unflatten_dict_recursive(flat_dict, sep, d, parts):
    for part in parts[:-1]:
        next_part = parts[parts.index(part) + 1]
        if part.isdigit() and next_part.isdigit():
            d = _handle_list_in_dict(d, part, int(next_part))
        else:
            d = d.setdefault(part, {})
    last_key = parts[-1]
    last_key = int(last_key) if last_key.isdigit() else last_key
    d[last_key] = flat_dict[sep.join(parts)]

def unflatten_dict(flat_dict: dict, sep: str = '_') -> dict:
    result = {}
    for flat_key, value in flat_dict.items():
        _unflatten_dict_recursive(flat_dict, sep, result, flat_key.split(sep))
    return result

def _insert_with_dict_handling(lst, indices, value):
    for index in indices[:-1]:
        while len(lst) <= index:
            lst.append({} if isinstance(indices[indices.index(index) + 1], str) else [])
        lst = lst[index]
    lst[indices[-1]] = value

def unflatten_to_list(flat_dict: dict, sep: str = '_') -> list:
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
    return result_list

def unflatten_complex_structure(flat_obj: Union[dict, list], sep: str = '_', logic_func: Callable = None) -> Union[dict, list]:
    if isinstance(flat_obj, dict):
        return unflatten_dict_with_custom_logic(flat_obj, logic_func, sep) if logic_func else unflatten_dict(flat_obj, sep)
    elif isinstance(flat_obj, list):
        indexed_flat_obj = {f"{i}": v for i, v in enumerate(flat_obj)}
        return unflatten_to_list(indexed_flat_obj, sep)
    else:
        raise TypeError("Object must be a flattened dictionary or list.")

def change_separator(flat_dict: dict, new_sep: str) -> dict:
    return {k.replace('_', new_sep): v for k, v in flat_dict.items()}

def get_keys(d: dict) -> List[str]:
    return list(d.keys())

def is_flattenable(obj: Any) -> bool:
    if isinstance(obj, dict):
        return any(isinstance(v, (dict, list)) for v in obj.values())
    elif isinstance(obj, list):
        return any(isinstance(i, (dict, list)) for i in obj)
    return False

def flatten_with_custom_logic(obj: Union[dict, list], logic_func: Callable, parent_key: str = '', sep: str = '_', **kwargs) -> Union[dict, list]:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key, new_value = logic_func(parent_key, k, v, **kwargs)
            if isinstance(v, (dict, list)):
                items.extend(flatten_with_custom_logic(v, logic_func, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, new_value))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key, new_value = logic_func(parent_key, None, item, **kwargs)
            items.append((f"{new_key}{sep}{i}", new_value))
    return dict(items)

def flatten_with_max_depth(obj: Union[dict, list], max_depth: int, current_depth: int = 0, parent_key: str = '', sep: str = '_', **kwargs) -> dict:
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)) and current_depth < max_depth:
                items.extend(flatten_with_max_depth(v, max_depth, current_depth + 1, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            if isinstance(item, (dict, list)) and current_depth < max_depth:
                items.extend(flatten_with_max_depth(item, max_depth, current_depth + 1, new_key, sep, **kwargs).items())
            else:
                items.append((new_key, item))
    return dict(items)

def unflatten_dict_with_custom_logic(flat_dict: dict, logic_func: Callable, sep: str = '_') -> dict:
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

def flatten_iterable(iterable: Iterable, max_depth: int = None) -> Iterable:
    def _flatten(input_iterable, current_depth):
        if max_depth is not None and current_depth >= max_depth:
            yield input_iterable
        else:
            for item in input_iterable:
                if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                    yield from _flatten(item, current_depth + 1)
                else:
                    yield item
    return _flatten(iterable, 0)

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:
    return list(flatten_iterable(iterable, max_depth))

def flatten_iterable_generator(iterable: Iterable) -> Generator:
    return flatten_iterable(iterable)

def flatten_with_path_preservation(obj: Union[dict, list], parent_key: str = '', sep: str = '_') -> dict:
    def logic_func(path, key, value):
        if path:
            new_key = f"{path}{sep}{key}" if key is not None else f"{path}{sep}"
        else:
            new_key = key if key is not None else ""
        return new_key, value
    return flatten_with_custom_logic(obj, logic_func, parent_key, sep)

