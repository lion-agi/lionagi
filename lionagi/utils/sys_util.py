import os
import hashlib
import re
import copy
import json
from pathlib import Path
from datetime import datetime
from dateutil import parser
from typing import Any, Dict, List, Optional, Type, Union


def get_timestamp() -> str:
    """
    Generates a current timestamp in a file-safe string format.

    Returns:
        The current timestamp in a file-safe string format.

    Examples:
        >>> get_timestamp()  # Doctest: +ELLIPSIS
        '...'
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_copy(input: Any, n: int = 1) -> Any:
    """
    Creates a deep copy of the input object a specified number of times.

    Args:
        input: The object to be copied.
        n: The number of deep copies to create.

    Raises:
        ValueError: If 'n' is not a positive integer.

    Returns:
        A deep copy of 'input' or a list of deep copies if 'n' > 1.

    Examples:
        >>> sample_dict = {'key': 'value'}
        >>> create_copy(sample_dict, 2)
        [{'key': 'value'}, {'key': 'value'}]
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_path(dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix=False) -> str:
    """
    Creates a file path by optionally appending a timestamp to the filename.

    Args:
        dir: The directory in which the file is to be located.
        filename: The name of the file.
        timestamp: If True, appends a timestamp to the filename. Defaults to True.
        dir_exist_ok: If True, creates the directory if it doesn't exist. Defaults to True.
        time_prefix: If True, the timestamp is added as a prefix; otherwise, it's appended. Defaults to False.

    Returns:
        The full path to the file.

    Examples:
        >>> create_path('/tmp/', 'log.txt', timestamp=False)
        '/tmp/log.txt'
    """
    
    dir = dir + '/' if str(dir)[-1] != '/' else dir
    filename, ext = filename.split('.')
    os.makedirs(dir, exist_ok=dir_exist_ok)
    
    if timestamp:
        timestamp = get_timestamp()
        return f"{dir}{timestamp}_{filename}.{ext}" if time_prefix else f"{dir}{filename}_{timestamp}.{ext}"
    else:
        return f"{dir}{filename}"

def split_path(path: Path) -> tuple:
    """
    Splits a given path into folder name and file name.

    Args:
        path: The path to split.

    Returns:
        A tuple containing the folder name and file name.
    """
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    """
    Get index of elements in a list based on their consecutive cumulative sum of length.

    Args:
        input: List of items to be binned.
        upper: Upper threshold for the cumulative sum of the length of items in a bin.

    Returns:
        List of lists, where each inner list contains the indices of the items that form a bin.

    Examples:
        >>> items = ['apple', 'a', 'b', 'banana', 'cheery', 'c', 'd', 'e']
        >>> upper = 10
        >>> get_bins(items, upper)
        [[0, 1, 2], [3], [4, 5, 6, 7]]
    """
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
    """
    Changes a key in a dictionary to a new key.

    Args:
        dict_: The dictionary to change the key in.
        old_key: The old key to be changed.
        new_key: The new key to change to.
    """
    dict_[new_key] = dict_.pop(old_key)

def create_id(n=32) -> str:
    """
    Generates a unique ID based on the current time and random bytes.

    Args:
        n: Length of the unique identifier to return. Defaults to 32.

    Returns:
        A unique identifier.

    Examples:
        >>> create_id()  # Doctest: +ELLIPSIS
        '...'
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(32)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def str_to_datetime(datetime_str: str, fmt: Optional[str] = None) -> datetime:
    """
    Convert a string representation of a date and time to a datetime object.

    Args:
        datetime_str: A string representing a date and time.
        fmt: An optional format string.

    Returns:
        A datetime object corresponding to the given string.

    Examples:
        >>> str_to_datetime("2023-01-01 12:00:00")
        datetime.datetime(2023, 1, 1, 12, 0)
        >>> str_to_datetime("January 1, 2023, 12:00 PM", "%B %d, %Y, %I:%M %p")
        datetime.datetime(2023, 1, 1, 12, 0)
    """
    if fmt:
        return datetime.strptime(datetime_str, fmt)
    else:
        return parser.parse(datetime_str)
    
def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: Type[Union[int, float]] = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    """
    Convert the first numeric value in the input string to the specified number type.

    Args:
        input_: The input string containing the numeric value.
        upper_bound: The upper bound for the numeric value (optional).
        lower_bound: The lower bound for the numeric value (optional).
        num_type: The type of number to return (int or float).
        precision: The number of decimal places to round to if num_type is float (optional).

    Returns:
        The numeric value converted to the specified type.

    Raises:
        ValueError: If no numeric values are found or if the number type is invalid.

    Examples:
        >>> str_to_num('Value is -123.456', num_type=float, precision=2)
        -123.46
        >>> str_to_num('Value is 100', upper_bound=99)
        ValueError: Number 100 is greater than the upper bound of 99.
    """
    numbers = re.findall(r'-?\d+\.?\d*', input_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {input_}")
    
    number = numbers[0]
    if num_type is int:
        number = int(float(number))
    elif num_type is float:
        number = round(float(number), precision) if precision is not None else float(number)
    else:
        raise ValueError(f"Invalid number type: {num_type}")

    if upper_bound is not None and number > upper_bound:
        raise ValueError(f"Number {number} is greater than the upper bound of {upper_bound}.")
    if lower_bound is not None and number < lower_bound:
        raise ValueError(f"Number {number} is less than the lower bound of {lower_bound}.")

    return number

def find_depth(nested_obj, depth_strategy='uniform', ignore_non_iterable=False):
    """
    Calculates the maximum depth of a nested list, dictionary, or a combination of both.

    Args:
        nested_obj: The nested object to find the depth of.
        depth_strategy: Strategy to calculate depth ('uniform' or 'mixed').
        ignore_non_iterable: If True, non-iterable elements do not count towards depth.

    Returns:
        The maximum depth of the nested structure.

    Raises:
        ValueError: If an unsupported depth strategy is specified.
    """

    def _uniform_depth(obj, current_depth=0):
        """Calculates depth assuming uniform data types in nested_obj."""
        if isinstance(obj, (list, tuple)):
            return max((_uniform_depth(item, current_depth + 1) for item in obj), default=current_depth)
        elif isinstance(obj, dict):
            return max((_uniform_depth(value, current_depth + 1) for value in obj.values()), default=current_depth)
        else:
            return current_depth if ignore_non_iterable else 1

    def _mixed_depth(obj, current_depth=0):
        """Calculates depth allowing for mixed data types in nested_obj."""
        if isinstance(obj, (list, tuple, dict)):
            if isinstance(obj, dict):
                obj = obj.values()
            return max((_mixed_depth(item, current_depth + 1) for item in obj), default=current_depth)
        else:
            return current_depth if ignore_non_iterable else 1

    if depth_strategy == 'uniform':
        return _uniform_depth(nested_obj)
    elif depth_strategy == 'mixed':
        return _mixed_depth(nested_obj)
    else:
        raise ValueError("Unsupported depth strategy. Choose 'uniform' or 'mixed'.")

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

def strip_lower(input_: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Strips and converts a string or each string in a list to lowercase.

    Args:
        input_: A string or list of strings to process.

    Returns:
        The processed string or list of strings, or False on failure.
    """
    try:
        return str(input_).strip().lower()
    except:
        return False

def as_dict(input_):
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
