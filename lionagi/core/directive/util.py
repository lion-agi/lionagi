import re
import json
from typing import Callable, Tuple, Dict, List, Any, Optional


def basic_func_grammar(func_call: str) -> Callable[[str], Optional[Tuple[List[Any], Dict[str, Any]]]]:
    """
    Defines a basic function grammar for parsing string function calls into callable format.
    Parses the string to extract function arguments and keyword arguments.

    Parameters:
    - action_call: The name of the function to match in the call string.

    Returns:
    - A callable that takes a string representation of a function call and returns a tuple of positional arguments
      and keyword arguments if the string matches the specified function name; otherwise, returns None.
    """

    def parse_call(call_str: str) -> Optional[Tuple[List[Any], Dict[str, Any]]]:
        func_pattern = re.compile(rf"^{func_call}\((?P<args>.*)\)$")
        arg_split_pattern = re.compile(r",\s*")
        kwarg_pattern = re.compile(r"^(?P<key>\w+)=(?P<value>.+)$")

        match = func_pattern.match(call_str)
        if not match:
            return None  # No match found or function name does not match.

        args_str = match.group("args")
        arg_parts = arg_split_pattern.split(args_str) if args_str else []

        args, kwargs = [], {}
        for part in arg_parts:
            kwarg_match = kwarg_pattern.match(part)
            if kwarg_match:
                kwargs[kwarg_match.group("key")] = json.loads(kwarg_match.group("value"))
            else:
                args.append(json.loads(part))

        return args, kwargs

    return parse_call
