import inspect
from typing import Any, Literal

from lionagi.libs.constants import py_json_msp

from .docstring import extract_docstring


def function_to_schema(
    f_,
    style: Literal["google", "rest"] = "google",
    *,
    f_description=None,
    p_description=None,
) -> dict:
    """
    Generate a schema description for a given function. in openai format

    This function generates a schema description for the given function
    using typing hints and docstrings. The schema includes the function's
    name, description, and parameter details.

    Args:
        func (Callable): The function to generate a schema for.
        style (str): The docstring format. Can be 'google' (default) or
            'reST'.
        func_description (str, optional): A custom description for the
            function. If not provided, the description will be extracted
            from the function's docstring.
        params_description (dict, optional): A dictionary mapping
            parameter names to their descriptions. If not provided, the
            parameter descriptions will be extracted from the function's
            docstring.

    Returns:
        dict: A schema describing the function, including its name,
        description, and parameter details.

    Example:
        >>> def example_func(param1: int, param2: str) -> bool:
        ...     '''Example function.
        ...
        ...     Args:
        ...         param1 (int): The first parameter.
        ...         param2 (str): The second parameter.
        ...     '''
        ...     return True
        >>> schema = function_to_schema(example_func)
        >>> schema['function']['name']
        'example_func'
    """
    # Extract function name
    func_name = f_.__name__

    # Extract function description and parameter descriptions
    if not f_description or not p_description:
        func_desc, params_desc = extract_docstring(f_, style)
        f_description = f_description or func_desc
        p_description = p_description or params_desc

    # Extract parameter details using typing hints
    sig = inspect.signature(f_)
    parameters: dict[str, Any] = {
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
        param_description = p_description.get(name)

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
            "description": f_description,
            "parameters": parameters,
        },
    }
