# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from typing import Any, Literal

from lionagi.libs.base import PY_TYPE_TO_JSON, FunctionSchema


def extract_docstring(
    func: Callable, style: Literal["google", "rest"] = "google"
) -> tuple[str | None, dict[str, str]]:
    """
    Extract the function description and parameter descriptions from the docstring.

    Supports Google-style or reST-style docstrings.

    Args:
        func: The function from which to extract docstring details.
        style: The docstring style ("google" or "rest").

    Returns:
        A tuple `(description, params)` where:
            - `description` is a string containing the function description or None if no docstring.
            - `params` is a dict mapping parameter names to their descriptions.

    Raises:
        ValueError: If an unsupported style is provided.

    Examples:
        >>> def example_function(param1: int, param2: str):
        ...     '''Example function.
        ...
        ...     Args:
        ...         param1 (int): The first parameter.
        ...         param2 (str): The second parameter.
        ...     '''
        ...     pass
        >>> desc, params = extract_docstring(example_function, style="google")
        >>> desc
        'Example function.'
        >>> params
        {'param1': 'The first parameter.', 'param2': 'The second parameter.'}
    """
    style = style.strip().lower()
    if style == "google":
        return _extract_docstring_details_google(func)
    elif style == "rest":
        return _extract_docstring_details_rest(func)
    else:
        raise ValueError(
            f"{style} is not supported. Please choose either 'google' or 'rest'."
        )


def _get_docstring_lines(func: Callable) -> list[str]:
    """Retrieve the docstring of a function and return it as a list of lines."""
    docstring = inspect.getdoc(func)
    if not docstring:
        return []
    return docstring.split("\n")


def _extract_docstring_details_google(
    func: Callable,
) -> tuple[str | None, dict[str, str]]:
    """
    Extract description and parameter info from a Google-style docstring.

    Google style example:
        '''
        This is the function description.

        Args:
            param1 (int): Description for param1.
            param2 (str): Description for param2.
        '''

    Returns:
        (description, {param: description})
    """
    lines = _get_docstring_lines(func)
    if not lines:
        return None, {}

    # The first non-empty line is the function description
    func_description = lines[0].strip()

    params_description = {}
    # Find the line where 'Args:' or a similar heading starts
    params_section_start = None
    for i, line in enumerate(lines[1:], start=1):
        lower_line = line.strip().lower()
        if lower_line in ("args:", "parameters:", "params:", "arguments:"):
            params_section_start = i + 1
            break

    if params_section_start is None:
        # No Args section found
        return func_description, params_description

    # Parse parameter lines
    current_param = None
    for line in lines[params_section_start:]:
        if not line.strip():
            continue
        # Parameters are typically defined with indentation followed by name and desc.
        if line.startswith(" "):
            # Format: "    param (type): description"
            parts = line.split(":", 1)
            if len(parts) == 2:
                # New parameter line
                param_part, desc = parts
                param_part = param_part.strip()
                # Param_part may contain '(type)', so split by '(' if present
                param_name = param_part.split("(")[0].strip()
                params_description[param_name] = desc.strip()
                current_param = param_name
            else:
                # Continuation of the previous param description
                if current_param:
                    params_description[current_param] += " " + parts[0].strip()
        else:
            # End of parameters section if we hit a non-indented line
            break

    return func_description, params_description


def _extract_docstring_details_rest(
    func: Callable,
) -> tuple[str | None, dict[str, str]]:
    """
    Extract description and parameter info from a reST-style docstring.

    reST style example:
        '''
        This is the function description.

        :param param1: Description for param1.
        :type param1: int
        :param param2: Description for param2.
        :type param2: str
        '''

    Returns:
        (description, {param: description})
    """
    lines = _get_docstring_lines(func)
    if not lines:
        return None, {}

    func_description = lines[0].strip()
    params_description = {}
    current_param = None

    # In reST style, parameters are specified as ":param name: description"
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith(":param "):
            # New parameter definition
            # Format: ":param param_name: description"
            # Split by ":" twice: ['', 'param param_name', ' description']
            parts = stripped.split(":", 2)
            # parts[1] = "param param_name"
            param_name = parts[1].split()[1]
            param_desc = parts[2].strip()
            params_description[param_name] = param_desc
            current_param = param_name
        elif stripped.startswith(":type"):
            # We can ignore :type lines as they don't carry param desc text
            continue
        elif stripped.startswith(":"):
            # Any other directives are not parameters
            continue
        else:
            # Continuation of the last parameter description
            if current_param and stripped:
                params_description[current_param] += " " + stripped

    return func_description, params_description


def function_to_schema(
    f_: Callable,
    style: Literal["google", "rest"] = "google",
    *,
    func_description: str | None = None,
    params_description: dict[str, str] | None = None,
) -> FunctionSchema:
    """
    Generate a schema description for a given function in an OpenAI-style format.

    This function uses type hints and docstrings to produce a schema that can be
    used to describe the function's purpose, parameters, and required fields in a
    JSON-serializable format (e.g., for use with OpenAI function calling).

    Args:
        f_ (Callable): The function to generate a schema for.
        style (Literal["google", "rest"]): The docstring format. Either 'google' or 'rest'.
            Defaults to 'google'.
        func_description (str, optional): A custom description for the function. If not
            provided, the description is extracted from the function's docstring.
        params_description (dict[str, str], optional): A dictionary mapping parameter names
            to their descriptions. If not provided, descriptions are extracted from the
            function's docstring.

    Returns:
        FunctionSchema: A schema describing the function, including its name, description, and parameters.

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
    func_name = f_.__name__

    # Extract function description and parameter descriptions if not provided
    if func_description is None or params_description is None:
        doc_desc, doc_params = extract_docstring(f_, style)
        func_description = (
            func_description or doc_desc or "No description provided."
        )
        params_description = params_description or doc_params or {}

    sig = inspect.signature(f_)
    parameters_schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for name, param in sig.parameters.items():
        # Determine if param is required (no default)
        is_required = param.default is inspect.Parameter.empty

        # Determine the param type based on annotation
        # Fall back to "string" if no annotation or unknown type
        if param.annotation is not inspect.Parameter.empty:
            param_type_name = getattr(param.annotation, "__name__", None)
            param_type = PY_TYPE_TO_JSON.get(param_type_name, "string")
        else:
            param_type = "string"

        # Get parameter description from docstring or default to empty string
        param_desc = params_description.get(name, "")

        # Add parameter to schema
        parameters_schema["properties"][name] = {
            "type": param_type,
            "description": param_desc,
        }

        # Only add to required if it has no default
        if is_required:
            parameters_schema["required"].append(name)

    return FunctionSchema(
        name=func_name,
        description=func_description,
        parameters=parameters_schema,
    )
