from ..schema import Tool
from lionagi.parsers.function_parsers import _func_to_schema

def func_to_tool(func_, parser=None, docstring_style='google'):
    """
    Wraps a function into a Tool object, using the provided docstring style to parse
    the function's docstring and generate a schema.

    Args:
        func_ (Callable): The function to wrap into a Tool object.
        parser (Any): The parser associated with the Tool (not used).
        docstring_style (str): The docstring format ('google' or 'reST').

    Returns:
        Tool: A Tool object containing the wrapped function and its schema.

    Examples:
        >>> def example_function(param1: int, param2: str) -> bool:
        ...     '''Example function.
        ...
        ...     Args:
        ...         param1 (int): The first parameter.
        ...         param2 (str): The second parameter.
        ...     '''
        ...     return True
        >>> tool = func_to_tool(example_function)
        >>> isinstance(tool, Tool)
        True
    """
    schema = _func_to_schema(func_, docstring_style)
    return Tool(func=func_, parser=parser, schema_=schema)
