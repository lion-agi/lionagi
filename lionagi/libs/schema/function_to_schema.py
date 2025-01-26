# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from typing import Any, Literal

from pydantic import BaseModel

from .extract_docstring import extract_docstring


class ToolSchema(BaseModel):

    function: str | None = None
    description: str | None = None
    parameters: dict[str, Any] | None = None

    @property
    def name(self):
        return self.function

    @name.setter
    def name(self, value):
        self.function = value

    def to_dict(self):
        return {
            "type": "function",
            "function": {
                "name": self.function,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


py_json_msp = {
    "str": "string",
    "int": "number",
    "float": "number",
    "list": "array",
    "tuple": "array",
    "bool": "boolean",
    "dict": "object",
}


def function_to_schema(
    f_,
    /,
    style: Literal["google", "rest"] = "google",
    *,
    name: str = None,
    func_description: str = None,
    param_description: dict[str, str] = None,
    request_options: type[BaseModel] = None,
    as_obj: bool = False,
) -> dict | ToolSchema:
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
    func_name = f_.__name__ if name is None else name

    # Extract function description and parameter descriptions
    if not func_description or not param_description:
        func_desc, params_desc = extract_docstring(f_, style)
        func_description = func_description or func_desc
        param_description = param_description or params_desc

    # Extract parameter details using typing hints
    sig = inspect.signature(f_)

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    if request_options:
        schema_ = request_options.model_json_schema()
        parameters = schema_

    else:
        for n, param in sig.parameters.items():
            # Default type to string and update if type hint is available
            param_type = "string"
            if param.annotation is not inspect.Parameter.empty:
                param_type = py_json_msp[param.annotation.__name__]

            # Extract parameter description from docstring, if available
            param_description = param_description.get(n)

            # Assuming all parameters are required for simplicity
            parameters["required"].append(n)
            parameters["properties"][n] = {
                "type": param_type,
                "description": param_description,
            }

    schema = ToolSchema(
        function=func_name,
        description=func_description,
        parameters=parameters,
    )

    if as_obj:
        return schema
    return schema.to_dict()
