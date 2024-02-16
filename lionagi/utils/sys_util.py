import os
import subprocess
import sys
import copy
from datetime import datetime
import hashlib
import re
import importlib.util
import platform
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

from typing import Any, List, Dict


def create_copy(input: Any, n: int = 1) -> Any:
    """
    Creates a deep copy of the input. If n is greater than 1, returns a list of deep copies.

    Args:
        input (Any): The input to copy, can be of any type.
        n (int, optional): The number of copies to make. Defaults to 1.

    Raises:
        ValueError: If 'n' is not a positive integer.

    Returns:
        Any: A single deep copy of the input if n is 1, otherwise a list of deep copies.

    Examples:
        >>> create_copy([1, 2, 3], 2)
        [[1, 2, 3], [1, 2, 3]]
        >>> create_copy('Hello', 3)
        ['Hello', 'Hello', 'Hello']
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n: int = 32) -> str:
    """
    Generates a SHA256 hash based on the current time and random bytes, truncated to n characters.

    Args:
        n (int, optional): The desired length of the hash string. Defaults to 32.

    Returns:
        str: A unique hash string of length n.

    Examples:
        >>> create_id(8)  # Output will vary due to randomness
        'e3b0c442'
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(42)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def create_path(
    dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, 
    time_prefix: bool = False
) -> str:
    """
    Constructs a file path with optional timestamping and directory creation. Ensures the directory exists.

    Args:
        dir (str): The target directory for the file.
        filename (str): The name of the file, with or without extension.
        timestamp (bool, optional): Whether to add a timestamp to the filename. Defaults to True.
        dir_exist_ok (bool, optional): If False, raises an error if the directory exists. Defaults to True.
        time_prefix (bool, optional): If True, adds the timestamp as a prefix; otherwise, as a suffix.

    Returns:
        str: The fully constructed file path, including the directory and filename.

    Examples:
        >>> create_path('/tmp', 'log.txt', time_prefix=True)
        '/tmp/2023-01-01T00_00_00_log.txt'
        >>> create_path('/tmp', 'data.csv', timestamp=False)
        '/tmp/data.csv'
    """
    # Convert dir to pathlib.Path object for robust path handling
    dir_path = Path(dir)
    
    # Handle filename and extension
    name, ext = os.path.splitext(filename)
    ext = ext or ''  # Ensure ext is a string, even if empty

    # Construct the timestamp string
    timestamp_str = get_timestamp() if timestamp else ''
    filename = f"{timestamp_str}{name}" if time_prefix else f"{name}{timestamp_str}"
    full_filename = f"{filename}{ext}"  # Reattach extension

    # Use pathlib for path construction and directory creation
    full_path = dir_path / full_filename
    full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)  # Create directory if needed

    return str(full_path)

def get_bins(input: List[str], upper: int) -> List[List[int]]:
    """
    Distributes a list of strings into bins based on a specified character length limit per bin.

    This function iterates through a list of strings, grouping them into 'bins' where the total
    length of the strings in each bin does not exceed the specified 'upper' limit. The function
    returns a list of bins, with each bin containing the indices of the strings in the original list.

    Args:
        input (List[str]): The list of strings to be distributed into bins.
        upper (int): The maximum allowed total character length for each bin.

    Returns:
        List[List[int]]: A list where each element is a bin (list of indices from 'input') that meets the length criteria.

    Examples:
        >>> get_bins(["hello", "world", "this", "is", "a", "test"], 10)
        [[0, 1], [2, 3], [4, 5]]
        >>> get_bins(["one", "two", "three", "four", "five"], 8)
        [[0, 1], [2], [3], [4]]
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


def get_timestamp() -> str:
    """
    Generates a current timestamp in a file-friendly string format.

    This function creates a timestamp string using the current date and time, formatted to be safe for use 
    in filenames across different operating systems by avoiding characters that are generally not allowed in filenames.

    Returns:
        str: A string representation of the current timestamp, formatted for filename compatibility.

    Examples:
        >>> get_timestamp()
        '2023-03-25T12_00_00'
        >>> get_timestamp()
        '2024-01-01T00_00_00'
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def str_to_num(
    input_: str, upper_bound: float = None, lower_bound: float = None, 
    num_type: type = int, precision: int = None) -> Any:
    """
    Extracts the first number from a string and converts it to a specified numeric type, with optional bounds and precision.

    Args:
        input (str): The string containing the number to convert.
        upper_bound (float, optional): The upper bound for the number. If specified, the number must be less than this value.
        lower_bound (float, optional): The lower bound for the number. If specified, the number must be greater than this value.
        num_type (type, optional): The type of number to convert to (int or float). Defaults to int.
        precision (int, optional): The number of decimal places for float conversion. Only applies if num_type is float.

    Raises:
        ValueError: If no numeric values found in the string or if the number does not meet the specified bounds.

    Returns:
        Any: The converted number, as an int or float, depending on num_type.

    Examples:
        >>> str_to_num("The room number is 42.", upper_bound=100)
        42
        >>> str_to_num("Approximately 3.14159.", num_type=float, precision=2)
        3.14
    """
    number_str = _extract_first_number(input_)
    if number_str is None:
        raise ValueError(f"No numeric values found in the string: {input_}")
    
    number = _convert_to_num(number_str, num_type, precision)

    if upper_bound is not None and number > upper_bound:
        raise ValueError(f"Number {number} is greater than the upper bound of {upper_bound}.")
    
    if lower_bound is not None and number < lower_bound:
        raise ValueError(f"Number {number} is less than the lower bound of {lower_bound}.")

    return number

def strip_lower(input_: Any) -> str:
    """Converts an input to a stripped, lowercase string.

    Args:
        input (Any): The input to convert.

    Raises:
        ValueError: If the input cannot be converted to a string.

    Returns:
        str: The converted, stripped, and lowercase string.

    Examples:
        >>> strip_lower("  Hello WORLD  ")
        'hello world'
    """

    try:
        return str(input_).strip().lower()
    
    except:
        raise ValueError(f"Could not convert input to string: {input_}")

def to_dict(input_: Any) -> Dict[Any, Any]:
    """
    Converts a JSON string to a dictionary, or returns the input if it is already a dictionary.

    Args:
        input_ (Any): The input JSON string or dictionary.

    Raises:
        ValueError: If the input cannot be converted to a dictionary.
        TypeError: If the input type is not supported for conversion.

    Returns:
        Dict[Any, Any]: The input converted to a dictionary.

    Examples:
        >>> to_dict('{"key": "value"}')
        {'key': 'value'}
        >>> to_dict({'already': 'a dict'})
        {'already': 'a dict'}
    """
    if isinstance(input_, str):
        try:
            return json.loads(input_)
        
        except Exception as e:
            raise ValueError(f"Could not convert input to dict: {e}") from e
        
    elif isinstance(input_, dict):
        return input_
    
    else:
        raise TypeError(f"Could not convert input to dict: {type(input_).__name__} given.")

class _SysUtil:
    """
    Provides a collection of static utility methods for system operations, including CPU architecture detection,
    directory management, dictionary manipulation, dynamic module importation, package installation checks,
    data type validation, schema matching, path splitting, timestamp conversion, and XML processing.

    This class is designed to facilitate common system and data manipulation tasks that can be leveraged across
    various applications, simplifying operations such as identifying CPU architecture, clearing directories,
    renaming keys in dictionaries, dynamically importing or installing modules, checking for installed packages,
    validating data types and schemas, splitting file paths, converting timestamps to datetime objects, and
    converting XML to dictionaries.

    Methods:
        get_cpu_architecture: Determines the machine's CPU architecture.
        clear_dir: Deletes all files in a specified directory, handling exceptions and logging.
        change_dict_key: Renames a key in a dictionary if the old key exists.
        install_import: Dynamically imports a module or specific name from a module, installing the package via pip if necessary.
        is_package_installed: Checks if a Python package is installed.
        is_same_dtype: Validates if all elements in a container are of the same specified data type.
        is_schema: Validates if a dictionary matches a specified schema.
        split_path: Separates a file path into its directory and filename components.
        timestamp_to_datetime: Converts a UNIX timestamp to a `datetime` object.
        xml_to_dict: Converts an XML ElementTree Element to a dictionary.
    """

    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Determines the current machine's CPU architecture, categorizing as 'apple_silicon' or 'other_cpu'.

        This function checks the platform's CPU architecture to identify if it is Apple Silicon 
        (ARM-based architecture) or another CPU type, facilitating architecture-specific logic or optimizations.

        Returns:
            str: 'apple_silicon' if the CPU is ARM-based, otherwise 'other_cpu'.

        Examples:
            >>> get_cpu_architecture()
            'apple_silicon'  # Output may vary depending on execution environment.
            >>> get_cpu_architecture()
            'other_cpu'      # For non-ARM architectures.
        """
        arch = platform.machine()
        if 'arm' in arch or 'aarch64' in arch:
            return 'apple_silicon'
        else:
            return 'other_cpu'
        
    @staticmethod    
    def clear_dir(dir_path: str) -> None:
        """
        Deletes all files in the specified directory path. Logs actions and errors.

        Args:
            dir_path (str): The path to the directory to clear.

        Raises:
            FileNotFoundError: If the specified directory does not exist.

        Examples:
            >>> clear_dir('/path/to/dir')
            # Assumes directory '/path/to/dir' exists and contains files.

        Note:
            This function logs each file deletion and any errors encountered to the configured logging handler.
        """
        if not os.path.exists(dir_path):
            raise FileNotFoundError("The specified directory does not exist.")
        
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logging.info(f'Successfully deleted {file_path}')
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')
                raise


    @staticmethod    
    def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
        """
        Renames a key in a dictionary if the old key exists.

        Args:
            dict_ (Dict[Any, Any]): The dictionary to modify.
            old_key (str): The old key that should be renamed.
            new_key (str): The new key name.

        Raises:
            KeyError: If the old key does not exist in the dictionary.

        Examples:
            >>> my_dict = {'old_key': 'value'}
            >>> change_dict_key(my_dict, 'old_key', 'new_key')
            >>> print(my_dict)
            {'new_key': 'value'}
        """
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @staticmethod
    def install_import(package_name, module_name=None, import_name=None, pip_name=None):
        """
        Dynamically imports a module or a specific name from a module. If the import fails, attempts to install the package via pip and retries the import.

        Args:
            package_name (str): The package name to import.
            module_name (str, optional): The module name to import from the package. Defaults to None.
            import_name (str, optional): The specific name to import from the module or package. Defaults to None.
            pip_name (str, optional): The pip package name if different from package_name. Defaults to None.

        Examples:
            >>> install_import('numpy')
            Successfully imported numpy.
            # If numpy is not installed, it attempts to install it first.
        """
        # Defaults to package_name if pip_name is not explicitly provided
        if pip_name is None:
            pip_name = package_name  
        
        full_import_path = package_name if module_name is None else f"{package_name}.{module_name}"
        try:
            if import_name:
                # For importing a specific name from a module or sub-module
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
                
            else:
                # For importing the module or package itself
                __import__(full_import_path)
            print(f"Successfully imported {import_name or full_import_path}.")
            
        except ImportError:
            print(f"Module {full_import_path} or attribute {import_name} not found. Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
                
            else:
                __import__(full_import_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Checks if a Python package is installed.

        Args:
            package_name (str): The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.

        Examples:
            >>> is_package_installed('numpy')
            True
            # This will return False if numpy is not installed.
        """
        package_spec = importlib.util.find_spec(package_name)
        return package_spec is not None

    @staticmethod
    def is_same_dtype(input_: Any, dtype: type = None) -> bool:
        """
        Validates if all elements in a container (list or dict) are of the same specified data type.

        Args:
            input_ (Any): The container (list or dict) to validate.
            dtype (type, optional): The data type to validate against. If None, the type of the first element is used.

        Returns:
            bool: True if all elements match the specified data type, False otherwise.

        Examples:
            >>> is_same_dtype([1, 2, 3])
            True
            >>> is_same_dtype([1, 'two', 3], int)
            False
        """
        
        if isinstance(input_, list):
            dtype = dtype or type(input_[0])    
            return all(isinstance(i, dtype) for i in input_)
        
        elif isinstance(input_, dict):
            dtype = dtype or type(list(input_.values())[0])
            return (isinstance(v, dtype) for _, v in input_.items())

        else:
            dtype = dtype or type(input_)
            return isinstance(input_, dtype)

    @staticmethod
    def is_schema(dict_: Dict, schema: Dict) -> bool:
        """
        Validates if a dictionary matches a specified schema, checking types of its keys.

        Args:
            dict_ (Dict): The dictionary to validate.
            schema (Dict): The schema with expected types for each key.

        Returns:
            bool: True if the dictionary matches the schema, False otherwise.

        Examples:
            >>> schema = {"name": str, "age": int}
            >>> is_schema({"name": "John", "age": 30}, schema)
            True
            >>> is_schema({"name": "John", "age": "thirty"}, schema)
            False
        """
        for key, expected_type in schema.items():
            
            if not isinstance(dict_[key], expected_type):
                return False
            
        return True

    @staticmethod
    def split_path(path: str) -> tuple:
        """Separates a file path into its directory and filename components.

        Args:
            path (str): The path to split.

        Returns:
            tuple: A tuple containing the directory and filename.

        Examples:
            >>> split_path('/path/to/file.txt')
            ('/path/to', 'file.txt')
        """
        folder_name = os.path.dirname(path)
        file_name = os.path.basename(path)
        
        return (folder_name, file_name)

    @staticmethod
    def timestamp_to_datetime(timestamp: float) -> datetime:
        """Converts a UNIX timestamp to a `datetime` object.

        Args:
            timestamp (float): The UNIX timestamp to convert.

        Returns:
            datetime: The `datetime` object representing the given timestamp.

        Examples:
            >>> timestamp_to_datetime(1609459200.0)
            datetime.datetime(2021, 1, 1, 0, 0)
        """
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        """Converts an XML ElementTree Element to a dictionary.

        Args:
            root (ET.Element): The root element of the XML tree.

        Returns:
            Dict[str, Any]: A dictionary representation of the XML element and its children.

        Examples:
            >>> root = ET.fromstring('<parent><child>value</child></parent>')
            >>> xml_to_dict(root)
            {'child': 'value'}
        """
        data = {}
        for child in root:
            data[child.tag] = child.text
            
        return data        

def _extract_first_number(inputstr: str) -> str:
    """
    Extracts the first numerical value from a string.

    Args:
        inputstr (str): The string to search for numerical values.

    Returns:
        str: The first numerical value found, or None if no value is found.

    Examples:
        >>> _extract_first_number("Room 42 is open.")
        '42'
    """
    numbers = re.findall(r'-?\d+\.?\d*', inputstr)
    
    return numbers[0] if numbers else None

def _convert_to_num(number_str: str, num_type: type = int, precision: int = None) -> Any:
    """
    Converts a string representation of a number to a specified numeric type.

    Args:
        number_str (str): The number as a string.
        num_type (type): The type to convert to, either int or float.
        precision (int, optional): The precision for float conversion, ignored for int.

    Raises:
        ValueError: If `num_type` is not int or float.

    Returns:
        Any: The number converted to the specified type.

    Examples:
        >>> _convert_to_num('3.14159', float, 2)
        3.14
    """
    if num_type is int:
        return int(float(number_str))
    
    elif num_type is float:
        return round(float(number_str), precision) if precision is not None else float(number_str)
    
    else:
        raise ValueError(f"Invalid number type: {num_type}")
    