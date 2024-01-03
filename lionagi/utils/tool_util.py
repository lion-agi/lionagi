import inspect
from ..schema.base_tool import Tool


def extract_docstring_details(func):
    """
    Extracts detailed descriptions for each parameter and the function from the docstring.

    Args:
    - func (function): The function to extract details from.

    Returns:
    - Tuple[str, dict]: Function description and a dictionary of parameter descriptions.
    """
    docstring = inspect.getdoc(func)
    if not docstring:
        return "No description available.", {}

    # Splitting the docstring into lines
    lines = docstring.split('\n')

    # Extracting the function description
    func_description = lines[0].strip()

    # Extracting parameter descriptions
    param_descriptions = {}
    current_param = None
    for line in lines[1:]:
        line = line.strip()
        if line.startswith(':param'):
            _, param, desc = line.split(' ', 2)
            current_param = param.strip(':')
            param_descriptions[current_param] = desc
        elif current_param and line:
            # Continue the description of the current parameter
            param_descriptions[current_param] += ' ' + line

    return func_description, param_descriptions

def func_to_schema(func):
    """
    Generates a schema description for a given function, using typing hints and docstrings.
    The schema includes the function's name, description, and parameters.

    Args:
    - func (function): The function to generate a schema for.

    Returns:
    - dict: A schema describing the function.
    """
    # Extracting function name and docstring details
    func_name = func.__name__
    func_description, param_descriptions = extract_docstring_details(func)
    
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
            param_type = param.annotation.__name__

        # Extract parameter description from docstring, if available
        param_description = param_descriptions.get(name, "No description available.")

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

def func_to_tool(func_, schema, parser=None):
    # schema = func_to_schema(func_)
    return Tool(func=func_, parser=parser, schema_=schema)
