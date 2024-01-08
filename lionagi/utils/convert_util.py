# this module has no internal dependency 
import inspect
import re
import xml.etree.ElementTree as ET
from typing import Optional, Union, Any, Type, Dict


def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: Type[Union[int, float]] = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    """
    Converts the first number in the input string to the specified numeric type.

    Parameters:
        input_ (str): The input string to extract the number from.
        
        upper_bound (Optional[Union[int, float]]): The upper bound for the number. Defaults to None.
        
        lower_bound (Optional[Union[int, float]]): The lower bound for the number. Defaults to None.
        
        num_type (Type[Union[int, float]]): The type of the number to return (int or float). Defaults to int.
        
        precision (Optional[int]): The precision for the floating-point number. Defaults to None.

    Returns:
        Union[int, float]: The converted number.

    Raises:
        ValueError: If no numeric values are found in the string or if there are conversion errors.
    """
    numbers = re.findall(r'-?\d+\.?\d*', input_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {input_}")
    
    try:
        numbers = numbers[0]
        if num_type is int: 
            numbers = int(float(numbers))
        elif num_type is float:
            numbers = round(float(numbers), precision) if precision is not None else float(numbers)
        else:
            raise ValueError(f"Invalid number type: {num_type}")
        if upper_bound is not None and numbers > upper_bound:
            raise ValueError(f"Number {numbers} is greater than the upper bound of {upper_bound}.")
        if lower_bound is not None and numbers < lower_bound:
            raise ValueError(f"Number {numbers} is less than the lower bound of {lower_bound}.")
        return numbers
    
    except ValueError as e:
        raise ValueError(f"Error converting string to number: {e}")
    
def dict_to_xml(data: Dict[str, Any], root_tag: str = 'node') -> str:
    """
    Helper method to convert a dictionary to an XML string.

    Parameters:
        data (Dict[str, Any]): The dictionary to convert to XML.
        root_tag (str): The root tag name for the XML.

    Returns:
        str: An XML string representation of the dictionary.
    """
    root = ET.Element(root_tag)
    _build_xml(root, data)
    return ET.tostring(root, encoding='unicode')

def _build_xml(element: ET.Element, data: Any):
    """Recursively builds XML elements from data."""
    if isinstance(data, dict):
        for key, value in data.items():
            sub_element = ET.SubElement(element, key)
            _build_xml(sub_element, value)
    elif isinstance(data, list):
        for item in data:
            item_element = ET.SubElement(element, 'item')
            _build_xml(item_element, item)
    else:
        element.text = str(data)

def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    """
    Helper method to convert an XML element back into a dictionary.
    """
    dict_data = {}
    for child in element:
        if child.getchildren():
            dict_data[child.tag] = xml_to_dict(child)
        else:
            dict_data[child.tag] = child.text
    return dict_data

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
    """
    Converts a Python type to its JSON type equivalent.

    Parameters:
        py_type (str): The name of the Python type.

    Returns:
        str: The corresponding JSON type.
    """
    type_mapping = {
        'str': 'string',
        'int': 'number',
        'float': 'number',
        'list': 'array',
        'tuple': 'array',
        'bool': 'boolean',
        'dict': 'object'
    }
    return type_mapping.get(py_type, 'object')

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
