import re
import json
from typing import Callable, Tuple, Dict, List, Any, Optional


def basic_func_grammar(func_call: str) -> Callable[[str], Optional[Tuple[List[Any], Dict[str, Any]]]]:
    """
    Defines a basic function grammar for parsing string function calls into callable format.
    Parses the string to extract function arguments and keyword arguments.

    Parameters:
    - tools: The name of the function to match in the call string.

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

# def register_tool_with_grammar(self, tools: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     """Registers a tools with associated grammar for advanced parsing."""
#     if not isinstance(tools, Tool):
#         raise TypeError("Please register a Tool object.")
#     name = tools.schema_['function']['name']
#     self.registry[name] = {"tools": tools, "grammar": grammar}
#
# async def invoke_with_grammar(self, tools: str) -> Any:
#     """Invokes a registered tools using a grammar-based approach for parsing the function call."""
#     for name, data in self.registry.items():
#         tools = data["tools"]
#         grammar = data["grammar"]
#         match = grammar(tools)
#         if match:
#             args, kwargs = match
#             func = tools.func
#             try:
#                 if is_coroutine_func(func):
#                     return await func(*args, **kwargs)
#                 else:
#                     return func(*args, **kwargs)
#             except Exception as e:
#                 raise ValueError(f"Error when invoking function {name}: {e}")
#     raise ValueError("No registered tools matches the function call.")
#
# def register_tool_with_grammar(self, tools: Tool, grammar: Callable[[str], Tuple[Dict, Dict]]) -> None:
#     if not isinstance(tools, Tool):
#         raise TypeError("Expected a Tool object for registration.")
#     name = tools.schema_['function']['name']
#     # Ensures each tools is associated with its unique grammar for parsing calls
#     self.registry[name] = {"tools": tools, "grammar": grammar}
#
# async def invoke_with_grammar(self, tools: str) -> Any:
#     for name, data in self.registry.items():
#         if "grammar" in data:  # Ensure only tools with grammar are processed
#             tools, grammar = data["tools"], data["grammar"]
#             match = grammar(tools)
#             if match:
#                 args, kwargs = match
#                 func = tools.func
#                 try:
#                     # Checks if the function is asynchronous and calls it appropriately
#                     if asyncio.iscoroutinefunction(func):
#                         return await func(*args, **kwargs)
#                     else:
#                         return func(*args, **kwargs)
#                 except Exception as e:
#                     raise ValueError(f"Error invoking {name} with {args}, {kwargs}: {e}")
#     raise ValueError(f"No registered tools matches the function call: {tools}")
#
