import os
import copy
from datetime import datetime
import hashlib
import re

import json
import logging

from typing import Any, List, Dict, Union


def get_timestamp() -> str:
    """
    Generates a current timestamp in ISO format with colons and periods replaced by 
    underscores.

    Returns:
        str: The current timestamp.

    Examples:
    >>> isinstance(get_timestamp(), str)
    True
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_copy(input: Any, n: int = 1) -> Any:
    """
    Creates a deep copy of the given input. If 'n' is greater than 1, returns a 
    list of deep copies.

    Args:
        input (Any): The object to be copied.
        n (int, optional): The number of copies to create. Defaults to 1.

    Returns:
        Any: A deep copy of the input, or a list of deep copies.

    Raises:
        ValueError: If 'n' is not a positive integer.
        
    Examples:
    >>> create_copy([1, 2, 3], 2)
    [[1, 2, 3], [1, 2, 3]]
    >>> create_copy("Hello")
    'Hello'
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_path(
    dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, 
    time_prefix: bool = False
) -> str:
    """
    Creates a file path with an optional timestamp, ensuring the directory exists.

    Args:
        dir (str): The directory in which the file will be placed.
        filename (str): The name of the file.
        timestamp (bool, optional): Flag to include a timestamp in the filename. Defaults to True.
        dir_exist_ok (bool, optional): Flag to create the directory if it doesn't exist. Defaults to True.
        time_prefix (bool, optional): Flag to place the timestamp as a prefix. Defaults to False.

    Returns:
        str: The full path of the file with the optional timestamp.

    Examples:
    >>> create_path("/tmp", "log.txt", timestamp=False)
    '/tmp/log.txt'
    >>> isinstance(create_path("/tmp", "report", time_prefix=True), str)
    True
    """
    dir = dir + '/' if not dir.endswith('/') else dir
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
    else:
        name, ext = filename, ''
    os.makedirs(dir, exist_ok=dir_exist_ok)
    timestamp_str = get_timestamp() if timestamp else ''
    filename = f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
    return f"{dir}{filename}.{ext}" if ext else f"{dir}{filename}"

def split_path(path: str) -> tuple:
    """
    Splits a file path into its directory name and file name.

    Args:
        path (str): The file path to split.

    Returns:
        tuple: A tuple containing the directory name and file name.

    Examples:
    >>> split_path("/home/user/document.txt")
    ('/home/user', 'document.txt')
    >>> split_path("document.txt")
    ('', 'document.txt')
    """
    folder_name = os.path.dirname(path)
    file_name = os.path.basename(path)
    return (folder_name, file_name)

def str_to_num(
    input: str, upper_bound: float = None, lower_bound: float = None, 
    num_type: type = int, precision: int = None
) -> Any:
    """
    Converts the first number in a string to a specified numeric type and checks if it 
    falls within specified bounds.

    Args:
        input (str): The string containing the number.
        upper_bound (float, optional): The upper limit for the number. Defaults to None.
        lower_bound (float, optional): The lower limit for the number. Defaults to None.
        num_type (type): The numeric type to which the number will be converted. Default is int.
        precision (int, optional): The precision for floating point numbers. Defaults to None.

    Returns:
        Any: The converted number in the specified type.

    Raises:
        ValueError: If no numeric value is found, or the number is outside the specified bounds.

    Examples:
    >>> str_to_num("Value is 20.5", upper_bound=30, num_type=float)
    20.5
    >>> str_to_num("Temperature -5 degrees", lower_bound=0)
    ValueError: Number -5 is less than the lower bound of 0.
    """
    number_str = _extract_first_number(input)
    if number_str is None:
        raise ValueError(f"No numeric values found in the string: {input}")
    
    number = _convert_to_num(number_str, num_type, precision)

    if upper_bound is not None and number > upper_bound:
        raise ValueError(f"Number {number} is greater than the upper bound of {upper_bound}.")
    if lower_bound is not None and number < lower_bound:
        raise ValueError(f"Number {number} is less than the lower bound of {lower_bound}.")

    return number

def get_bins(input: List[str], upper: int) -> List[List[int]]:
    """
    Distributes a list of strings into bins where the total length of strings in each 
    bin is less than a specified upper limit.

    Args:
        input (List[str]): The list of strings to be distributed.
        upper (int): The upper limit for the total length of strings in each bin.

    Returns:
        List[List[int]]: A list of lists, where each inner list contains indices of the 
        input list that make up a bin.

    Examples:
    >>> get_bins(["one", "two", "three", "four", "five"], 10)
    [[0, 1], [2], [3, 4]]
    """
    current = 0
    bins = []
    current_bin = []
    for idx, item in enumerate(input):
        
        if current + len(item) < upper:
            current_bin.append(idx)
            current += len(item)
            
        else:
            bins.append(current_bin)
            current_bin = [idx]
            current = len(item)
            
    if current_bin:
        bins.append(current_bin)
        
    return bins

def create_id(n: int = 32) -> str:
    """
    Creates a unique identifier using a combination of the current time and random bytes.

    Args:
        n (int, optional): The length of the identifier. Defaults to 32.

    Returns:
        str: The generated unique identifier.

    Examples:
    >>> len(create_id())
    32
    >>> len(create_id(16))
    16
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(32)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def directory_cleaner(directory: str) -> None:
    """
    Deletes all files within a given directory.

    Args:
        directory (str): The path of the directory to clean.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        Exception: If a file in the directory cannot be deleted.

    Examples:
    >>> directory_cleaner("/path/to/nonexistent/directory")
    FileNotFoundError: The specified directory does not exist.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError("The specified directory does not exist.")
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                logging.info(f'Successfully deleted {file_path}')
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')
            raise

def strip_lower(input: Any) -> str:
    """
    Strips and converts a given input to lower case.

    Args:
        input (Any): The input to be processed.

    Returns:
        str: The processed string in lower case.

    Raises:
        Exception: If the input cannot be converted to a string.

    Examples:
    >>> strip_lower(" Hello WORLD ")
    'hello world'
    >>> strip_lower(123)
    '123'
    """
    try:
        return str(input).strip().lower()
    except:
        return False

def _extract_first_number(inputstr: str) -> str:
    """
    Extracts the first number from a given string.

    Args:
        inputstr (str): The string from which the number will be extracted.

    Returns:
        str: The first number found in the string, returned as a string. 
             Returns None if no number is found.

    Examples:
    >>> extract_first_number("The 2 little pigs")
    '2'
    >>> extract_first_number("No numbers")
    None
    """
    numbers = re.findall(r'-?\d+\.?\d*', inputstr)
    return numbers[0] if numbers else None

def _convert_to_num(number_str: str, num_type: type = int, precision: int = None) -> Any:
    """
    Converts a string representation of a number to a specified numeric type.

    Args:
        number_str (str): The string representation of the number.
        num_type (type): The type to which the number will be converted. Default is int.
        precision (int, optional): The precision for floating point numbers. Defaults to None.

    Returns:
        Any: The converted number in the specified type.

    Raises:
        ValueError: If an invalid number type is provided.

    Examples:
    >>> convert_to_num("3.142", float, 2)
    3.14
    >>> convert_to_num("100", int)
    100
    """
    if num_type is int:
        return int(float(number_str))
    elif num_type is float:
        return round(float(number_str), precision) if precision is not None else float(number_str)
    else:
        raise ValueError(f"Invalid number type: {num_type}")

def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
    """
    Changes a key in a dictionary to a new key.

    Args:
        dict_ (Dict[Any, Any]): The dictionary to change the key in.
        old_key (str): The old key to be changed.
        new_key (str): The new key to change to.
    """
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)

def as_dict(input_: Any) -> Dict[Any, Any]:
    """
    Converts a JSON string or a dictionary to a dictionary.

    Args:
        input_: A JSON string or dictionary to convert.

    Returns:
        The input converted to a dictionary.

    Raises:
        ValueError: If the input cannot be converted to a dictionary.
    """
    if isinstance(input_, str):
        try:
            return json.loads(input_)
        except Exception as e:
            raise f"Could not convert input to dict: {e}"
    elif isinstance(input_, dict):
        return input_
    else:
        raise f"Could not convert input to dict: {input_}"

def is_schema(dict_: Dict, schema: Dict):
    """
    Checks if a dictionary matches a given schema.

    Args:
        dict_: The dictionary to check.
        schema: The schema to validate against.

    Returns:
        True if the dictionary matches the schema, False otherwise.
    """
    for key, expected_type in schema.items():
        if not isinstance(dict_[key], expected_type):
            return False
    return True

def timestamp_to_datetime(timestamp):    
    return datetime.fromtimestamp(timestamp)

