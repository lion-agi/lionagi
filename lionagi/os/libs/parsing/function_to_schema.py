import inspect
from .extract_docstring import extract_docstring_details
from .util import py_json_msp


def function_to_schema(
    func, style="google", func_description=None, params_description=None
):
    """
    Generates a schema description for a given function, using typing hints and
    docstrings. The schema includes the function's name, description, and parameters.

    Args:
            func (Callable): The function to generate a schema for.
            style (str): The docstring format ('google' or 'reST').

    Returns:
            Dict[str, Any]: A schema describing the function.

    Examples:
            >>> def example_function(param1: int, param2: str) -> bool:
            ...     '''Example function.
            ...
            ...     Args:
            ...         param1 (int): The first parameter.
            ...         param2 (str): The second parameter.
            ...     '''
            ...     return True
            >>> schema = _func_to_schema(example_function)
            >>> schema['function']['name']
            'example_function'
    """
    # Extracting function name and docstring details
    func_name = func.__name__

    if not func_description:
        func_description, _ = extract_docstring_details(func, style)
    if not params_description:
        _, params_description = extract_docstring_details(func, style)

    # Extracting parameters with typing hints
    sig = inspect.signature(func)
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for name, param in sig.parameters.items():
        # Default type to string and update if type hint is available
        param_type = "string"
        if param.annotation is not inspect.Parameter.empty:
            param_type = py_json_msp[param.annotation.__name__]

        # Extract parameter description from docstring, if available
        param_description = params_description.get(name, "No description available.")

        # Assuming all parameters are required for simplicity
        parameters["required"].append(name)
        parameters["properties"][name] = {
            "type": param_type,
            "description": param_description,
        }

    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": func_description,
            "parameters": parameters,
        },
    }
