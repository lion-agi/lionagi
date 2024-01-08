import inspect
from ..schema.base_tool import Tool


def extract_docstring_details_google(func):
    docstring = inspect.getdoc(func)
    if not docstring:
        return "No description available.", {}
    lines = docstring.split('\n')
    func_description = lines[0].strip()

    param_start_pos = 0
    lines_len = len(lines)

    params_description = {}
    for i in range(1, lines_len):
        if lines[i].startswith('Args') or lines[i].startswith('Arguments') or lines[i].startswith('Parameters'):
            param_start_pos = i + 1
            break

    current_param = None
    for i in range(param_start_pos, lines_len):
        if lines[i] == '':
            continue
        elif lines[i].startswith(' '):
            param_desc = lines[i].split(':', 1)
            if len(param_desc) == 1:
                params_description[current_param] += ' ' + param_desc[0].strip()
                continue
            param, desc = param_desc
            param = param.split('(')[0].strip()
            params_description[param] = desc.strip()
            current_param = param
        else:
            break
    return func_description, params_description


def extract_docstring_details_rest(func):
    docstring = inspect.getdoc(func)
    if not docstring:
        return "No description available.", {}
    lines = docstring.split('\n')
    func_description = lines[0].strip()

    params_description = {}
    current_param = None
    for line in lines[1:]:
        line = line.strip()
        if line.startswith(':param'):
            param_desc = line.split(':', 2)
            _, param, desc = param_desc
            param = param.split()[-1].strip()
            params_description[param] = desc.strip()
            current_param = param
        elif line.startswith(' '):
            params_description[current_param] += ' ' + line

    return func_description, params_description


def extract_docstring_details(func, style='google'):
    if style == 'google':
        func_description, params_description = extract_docstring_details_google(func)
    elif style == 'reST':
        func_description, params_description = extract_docstring_details_rest(func)
    else:
        raise ValueError(f'{style} is not supported. Please choose either "google" or "reST".')
    return func_description, params_description


def python_to_json_type(py_type):
    if py_type == 'str':
        return 'string'
    elif py_type == 'int' or py_type == 'float':
        return 'number'
    elif py_type == 'list' or py_type == 'tuple':
        return 'array'
    elif py_type == 'bool':
        return 'boolean'
    elif py_type == 'dict':
        return 'object'
    else:
        return 'object'


def func_to_schema(func, style='google'):
    """
    Generates a schema description for a given function, using typing hints and docstrings.
    The schema includes the function's name, description, and parameters.

    Parameters:
        func (function): The function to generate a schema for.

        style (str): The docstring format.

    Returns:
        dict: A schema describing the function.
    """
    # Extracting function name and docstring details
    func_name = func.__name__
    func_description, params_description = extract_docstring_details(func, style)

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
            param_type = python_to_json_type(param.annotation.__name__)

        # Extract parameter description from docstring, if available
        param_description = params_description.get(name, "No description available.")

        # Assuming all parameters are required for simplicity
        parameters["required"].append(name)
        parameters["properties"][name] = {
            "type": param_type,
            "description": param_description,
        }

    # Constructing the schema
    schema = {
        "type": "function",
        "function": {
            "name": func_name,
            "description": func_description,
            "parameters": parameters,
        }
    }
    return schema


def func_to_tool(func_, parser=None, docstring_style='google'):
    schema = func_to_schema(func_, docstring_style)
    return Tool(func=func_, parser=parser, schema_=schema)