import binascii
import copy
import csv
import hashlib
import inspect
import json
import os
import re
import xml.etree.ElementTree as ET
import yaml
import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Tuple, Type, Union

from dateutil import parser

# 1. Recursively Flatten a nested dict to a flat dict
def _flatten_dict_generator(d: Dict, parent_key: str = '', sep: str = '_') -> Generator[Tuple[str, Any], None, None]:
    """
    A generator that yields flattened key-value pairs from a nested dictionary.

    :param d: The dictionary to flatten.
    :param parent_key: The base key string for recursion.
    :param sep: Separator used between nested keys.
    :return: Generator of flattened key-value pairs.
    """
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            yield from _flatten_dict_generator(v, new_key, sep=sep)
        else:
            yield new_key, v

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """
    Flattens a nested dictionary into a single-level dictionary with keys as paths.

    :param d: The dictionary to flatten.
    :param parent_key: The base key string for recursion.
    :param sep: Separator used between nested keys.
    :return: A single-level dictionary with flattened keys.
    """
    return dict(_flatten_dict_generator(d, parent_key, sep))

# 2. Recursively flatten a nested list into a flat list
def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
    """
    A generator that yields flattened values from a nested list.

    :param l: The list to flatten.
    :param dropna: If True, None values will be dropped from the flattened list.
    :return: Generator of flattened values.
    """
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        elif i is not None or not dropna:
            yield i

def flatten_list(l: List, dropna: bool = True) -> List:
    """
    Flattens a nested list into a single-level list.

    :param l: The list to flatten.
    :param dropna: If True, None values will be dropped from the flattened list.
    :return: Flattened list.
    """
    return list(_flatten_list_generator(l, dropna))

# 3. Recursively flatten a nested structure (dict or list) into a flat dict
def _dynamic_flatten_generator(obj: Any, parent_key: str = '', sep: str = '_', max_depth: Union[int, None] = None, current_depth: int = 0) -> Generator[Tuple[str, Any], None, None]:
    """
    A generator that dynamically yields flattened key-value pairs from a nested structure.

    :param obj: The nested structure (dictionary or list) to flatten.
    :param parent_key: The base key for recursion (used internally).
    :param sep: Separator for nested keys.
    :param max_depth: The maximum depth to flatten.
    :param current_depth: The current depth in the structure (used internally).
    :return: Generator of flattened key-value pairs.
    """
    if max_depth is not None and current_depth > max_depth:
        yield parent_key, obj
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            yield from _dynamic_flatten_generator(v, new_key, sep, max_depth, current_depth + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            yield from _dynamic_flatten_generator(item, new_key, sep, max_depth, current_depth + 1)
    else:
        yield parent_key, obj

def dynamic_flatten(obj: Any, parent_key: str = '', sep: str = '_', max_depth: Union[int, None] = None) -> Dict:
    """
    Flattens a nested structure (dictionary or list) into a single-level dictionary with keys as paths.

    :param obj: The nested structure (dictionary or list) to flatten.
    :param parent_key: The base key for nested items.
    :param sep: Separator for nested keys.
    :param max_depth: The maximum depth to flatten.
    :return: Flattened dictionary.
    """
    return dict(_dynamic_flatten_generator(obj, parent_key, sep, max_depth))

# 4. dynamic unflatten a flat dict into a nested dict
def dynamic_unflatten_dict(
    flat_dict: Dict[str, Any], sep: str = '_', 
    custom_logic: Union[Callable[[str], Any], None] = None, 
    max_depth: Union[int, None] = None
) -> Union[Dict, List]:
    """
    Flattens a nested iterable up to a specified maximum depth.

    Parameters:
    - iterable (Iterable): An iterable to flatten.
    - max_depth (int, optional): The maximum depth to flatten. If None, flattens completely.

    Yields:
    - Generator[Any, None, None]: The flattened elements of the original iterable.
    """
    
    def _handle_list_insert(sub_obj: Union[Dict, List], part: int, value: Any):
        # Ensure part index exists in the list, fill gaps with None
        while len(sub_obj) <= part:
            sub_obj.append(None)
        sub_obj[part] = value

    def _insert(sub_obj: Union[Dict, List], parts: List[Union[str, int]], value: Any, current_depth: int = 0):
        for part in parts[:-1]:
            # Stop nesting further if max_depth is reached
            if max_depth is not None and current_depth >= max_depth:
                sub_obj[part] = {parts[-1]: value}
                return

            part = int(part) if part.isdigit() else part
            if isinstance(part, int):
                while len(sub_obj) <= part:
                    sub_obj.append(None)
                if sub_obj[part] is None:
                    sub_obj[part] = [] if (max_depth is None or current_depth < max_depth - 1) and isinstance(parts[parts.index(part) + 1], int) else {}
                sub_obj = sub_obj[part]
            else:
                sub_obj[part] = sub_obj.get(part, {})
                sub_obj = sub_obj[part]
            current_depth += 1

        last_part = parts[-1]
        if isinstance(last_part, int) and isinstance(sub_obj, list):
            _handle_list_insert(sub_obj, last_part, value)
        else:
            sub_obj[last_part] = value

    unflattened = {}
    for composite_key, value in flat_dict.items():
        parts = composite_key.split(sep)
        if custom_logic:
            parts = [custom_logic(part) for part in parts]
        else:
            parts = [int(part) if part.isdigit() else part for part in parts]
        _insert(unflattened, parts, value)

    if isinstance(unflattened, dict) and all(isinstance(k, int) for k in unflattened.keys()):
        max_index = max(unflattened.keys(), default=-1)
        return [unflattened.get(i) for i in range(max_index + 1)]
    if not unflattened:
        return {}
    return unflattened

# 5. dynamic unflatten a flat dictionary to a nested list
def _insert_with_dict_handling(result_list: Union[Dict, List], indices: List[Union[int, str]], value: Any, current_depth: int = 0):
    """
    Converts a nested iterable into a flattened list up to a specified maximum depth.

    Parameters:
    - iterable (Iterable): An iterable to flatten.
    - max_depth (int, optional): The maximum depth to flatten. If None, flattens completely.

    Returns:
    - List[Any]: A list containing the flattened elements of the original iterable.
    """
    for index in indices[:-1]:
        if isinstance(result_list, list):
            while len(result_list) <= index:
                result_list.append({})
            result_list = result_list[index]
        elif isinstance(result_list, dict):
            result_list = result_list.setdefault(index, {})
        current_depth += 1
    last_index = indices[-1]
    if isinstance(result_list, list):
        while len(result_list) <= last_index:
            result_list.append(None)
        result_list[last_index] = value
    else:
        result_list[last_index] = value

def unflatten_to_list(flat_dict: Dict[str, Any], sep: str = '_') -> List:
    """
    Converts an input to a list, optionally flattening and dropping None values.

    Parameters:
    - input_ (Any): The input to convert to a list.
    - flatten (bool): If True, flattens the input if it is a list.
    - dropna (bool): If True, drops None values from the list.

    Returns:
    - List[Any]: The processed list.
    """
    result_list = []
    for flat_key, value in flat_dict.items():
        indices = [int(p) if p.lstrip('-').isdigit() else p for p in flat_key.split(sep)]
        _insert_with_dict_handling(result_list, indices, value)
    return result_list

# 6. flatten most iteralbes to a flat list
def _flatten_iterable_generator(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    """
    Flattens a nested iterable up to a specified maximum depth.

    Parameters:
    - iterable (Iterable): An iterable to flatten.
    - max_depth (int, optional): The maximum depth to flatten. If None, flattens completely.

    Yields:
    - Generator[Any, None, None]: The flattened elements of the original iterable.
    """
    
    def _flatten(input_iterable: Iterable, current_depth: int) -> Generator[Any, None, None]:
        if isinstance(input_iterable, Iterable) and not isinstance(input_iterable, (str, bytes)):
            if max_depth is not None and current_depth >= max_depth:
                yield input_iterable
            else:
                for item in input_iterable:
                    yield from _flatten(item, current_depth + 1)
        else:
            yield input_iterable
    yield from _flatten(iterable, 0)

def flatten_iterable_to_list(iterable: Iterable, max_depth: int = None) -> List[Any]:
    """
    Converts a nested iterable into a flattened list up to a specified maximum depth.

    Parameters:
    - iterable (Iterable): An iterable to flatten.
    - max_depth (int, optional): The maximum depth to flatten. If None, flattens completely.

    Returns:
    - List[Any]: A list containing the flattened elements of the original iterable.
    """
    return list(_flatten_iterable_generator(iterable, max_depth))

# Utility
def change_separator(flat_dict, current_sep, new_sep):
    return {k.replace(current_sep, new_sep): v for k, v in flat_dict.items()}


def create_copy(input: Any, n: int) -> Any:
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n=32) -> str:
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(2048)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def get_timestamp() -> str:
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_path(dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix=False) -> str:
    
    dir = dir + '/' if str(dir)[-1] != '/' else dir
    filename, ext = filename.split('.')
    os.makedirs(dir, exist_ok=dir_exist_ok)
    
    if timestamp:
        timestamp = get_timestamp()
        return f"{dir}{timestamp}_{filename}.{ext}" if time_prefix else f"{dir}{filename}_{timestamp}.{ext}"
    else:
        return f"{dir}{filename}"

def split_path(path: Path) -> tuple:
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    current = 0
    bins = []
    bin = []
    
    for idx, item in enumerate(input):
        if current + len(item) < upper:
            bin.append(idx)
            current += len(item)
        elif current + len(item) >= upper:
            bins.append(bin)
            bin = [idx]
            current = len(item)
        if idx == len(input) - 1 and len(bin) > 0:
            bins.append(bin)
    return bins

def change_dict_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)

def timestamp_to_datetime(timestamp: int) -> str:
    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except:
            return timestamp
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def is_schema(dict_: Dict, schema: Dict):
    for key, expected_type in schema.items():
        if not isinstance(dict_[key], expected_type):
            return False
    return True

def create_hash(data: str, algorithm: str = 'sha256') -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode())
    return hasher.hexdigest()

def task_id_generator() -> Generator[int, None, None]:
    task_id = 0
    while True:
        yield task_id
        task_id += 1

def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: Type[Union[int, float]] = int, 
               precision: Optional[int] = None) -> Union[int, float]:
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
    root = ET.Element(root_tag)
    _build_xml(root, data)
    return ET.tostring(root, encoding='unicode')

def _build_xml(element: ET.Element, data: Any):
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

def json_to_yaml(json_data: str) -> str:
    """
    Converts JSON data to its YAML representation.

    Args:
        json_data (str): JSON formatted string.

    Returns:
        str: YAML formatted string.
    """
    parsed_json = json.loads(json_data)
    return yaml.dump(parsed_json, sort_keys=False)

def csv_to_json(csv_data: str) -> List[dict]:
    """
    Parses CSV data and converts it to JSON format.

    Args:
        csv_data (str): CSV formatted string.

    Returns:
        List[dict]: JSON representation of the CSV data.
    """
    reader = csv.DictReader(csv_data.splitlines())
    return [row for row in reader]

# Base64 Encoding and Decoding
def encode_base64(data: str) -> str:
    """
    Encodes a string to Base64 format.

    Args:
        data (str): The data to be encoded.

    Returns:
        str: The encoded data in Base64 format.
    """
    return base64.b64encode(data.encode()).decode()

def decode_base64(data: str) -> str:
    """
    Decodes a Base64 encoded string.

    Args:
        data (str): The Base64 encoded data to be decoded.

    Returns:
        str: The decoded data.
    """
    return base64.b64decode(data).decode()

# Datetime String to Python Datetime Object
def str_to_datetime(datetime_str: str, fmt: str = None) -> datetime:
    """
    Converts a datetime string to a Python datetime object.

    Args:
        datetime_str (str): Datetime string.
        fmt (str, optional): Format of the datetime string. If None, auto-detection is attempted.

    Returns:
        datetime: Python datetime object.
    """
    if fmt:
        return datetime.strptime(datetime_str, fmt)
    else:
        return parser.parse(datetime_str)

# Python Object to CSV
def python_obj_to_csv(data: list) -> str:
    """
    Serializes Python objects (like a list of dictionaries) into CSV format.

    Args:
        data (list): A list of dictionaries to be serialized into CSV.

    Returns:
        str: CSV formatted string representing the input data.
    """
    if not data:
        return ""

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Input must be a list of dictionaries.")

    output = csv.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    return output.getvalue()

# Binary Data to Hexadecimal
def binary_to_hex(data: bytes) -> str:
    """
    Converts binary data to its hexadecimal representation.

    Args:
        data (bytes): Binary data to be converted.

    Returns:
        str: Hexadecimal representation of the binary data.
    """
    return binascii.hexlify(data).decode()

# Type Inference from String
def infer_type_from_string(input_str: str):
    """
    Infers the most likely Python data type of a string and converts accordingly.

    Args:
        input_str (str): The string to infer the type from.

    Returns:
        The converted value in its inferred data type.
    """
    # Attempt to interpret as integer
    try:
        return int(input_str)
    except ValueError:
        pass

    # Attempt to interpret as float
    try:
        return float(input_str)
    except ValueError:
        pass

    # Attempt to interpret as boolean
    if input_str.lower() in ['true', 'false']:
        return input_str.lower() == 'true'

    # Default to string
    return input_str

def to_csv(input: List[Dict[str, Any]]=None,
           filepath: str=None,
           file_exist_ok: bool = False) -> None:
    """
    Writes a list of dictionaries to a CSV file, with dictionary keys as headers.

    This function writes a list of dictionaries to a CSV file. It checks if the file exists 
    and handles file creation based on the 'file_exist_ok' flag.

    Parameters:
        input (List[Dict[str, Any]]): Data to write to the CSV file.

        filepath (str): Path of the output CSV file.

        file_exist_ok (bool, optional): Create the file if it doesn't exist. Defaults to False.

    Raises:
        FileExistsError: If the file already exists and 'file_exist_ok' is False.

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> to_csv(data, 'people.csv')
    """

    if not os.path.exists(os.path.dirname(filepath)) and os.path.dirname(filepath) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filepath)} does not exist.")

    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input[0].keys())
        writer.writeheader()
        writer.writerows(input)

def append_to_jsonl(data: Any, filepath: str) -> None:
    """
    Appends data to a JSON lines (jsonl) file.

    Serializes given data to a JSON-formatted string and appends it to a jsonl file. 
    Useful for logging or data collection where entries are added incrementally.

    Parameters:
        data (Any): Data to be serialized and appended.

        filepath (str): Path to the jsonl file.

    Example:
        >>> append_to_jsonl({"key": "value"}, "data.jsonl")
        # Appends {"key": "value"} to 'data.jsonl'
    """
    json_string = json.dumps(data)
    with open(filepath, "a") as f:
        f.write(json_string + "\n")


def handle_error(value, config):
    if isinstance(value, Exception):
        if config.get('log', True):
            print(f"Error: {value}")  # Replace with appropriate logging mechanism
        return config.get('default', None)
    return value

def validate_type(value, expected_type):
    if not isinstance(value, expected_type):
        raise TypeError(f"Invalid type: expected {expected_type}, got {type(value)}")
    return value

def convert_type(value, target_type):
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        print(f"Conversion error: {e}")  # Replace with appropriate logging mechanism
        return None

def special_return(value, **config):
    processing_functions = {
        'handle_error': handle_error,
        'validate_type': validate_type,
        'convert_type': convert_type
    }

    for key, func in processing_functions.items():
        if key in config:
            value = func(value, config[key])
    return value

def to_list(input_: Any, flatten: bool = True, dropna: bool = False) -> List[Any]:

    if isinstance(input_, list) and flatten:
        input_ = flatten_list(input_)
        if dropna:
            input_ = [i for i in input_ if i is not None]
    elif isinstance(input_, Iterable) and not isinstance(input_, (str, dict)):
        try:
            input_ = list(input_)
        except:
            raise ValueError("Input cannot be converted to a list.")
    else:
        input_ = [input_]
    return input_