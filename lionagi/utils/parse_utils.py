import json
from typing import Tuple, Dict

def parse_function_call(response: str) -> Tuple[str, Dict]:
    out = json.loads(response)
    func = out.get('function', '').lstrip('call_')
    args = json.loads(out.get('arguments', '{}'))
    return func, args

def change_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)