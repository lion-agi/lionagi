
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