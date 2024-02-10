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

import pandas as pd
from typing import Any, List, Dict, Union


def as_dict(input_: Any) -> Dict[Any, Any]:
    """
    Convert a JSON string or a dictionary into a dictionary.

    Args:
        input_ (Any): The input to be converted to a dictionary. This can be a JSON string or a dictionary.

    Returns:
        Dict[Any, Any]: The input converted into a dictionary.

    Raises:
        ValueError: If the input is a string but cannot be parsed as JSON.
        TypeError: If the input is neither a string nor a dictionary.
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

def clear_dir(dir_path: str) -> None:
    """
    Clear all files within the specified directory.

    Args:
        dir_path (str): The path to the directory to be cleared.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
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

def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
    """
    Change a key in a dictionary to a new key.

    Args:
        dict_ (Dict[Any, Any]): The dictionary whose key needs to be changed.
        old_key (str): The old key that needs to be replaced.
        new_key (str): The new key to replace the old key.

    Returns:
        None: The function modifies the dictionary in place and returns None.
    """
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)
        
def create_copy(input: Any, n: int = 1) -> Any:
    """
    Create a deep copy of the input. If n > 1, returns a list of deep copies of the input.

    Args:
        input (Any): The input to be copied.
        n (int, optional): The number of copies to make. Defaults to 1.

    Returns:
        Any: A deep copy of the input, or a list of deep copies if n > 1.

    Raises:
        ValueError: If 'n' is not a positive integer.
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n: int = 32) -> str:
    """
    Generate a unique ID using the current time and random bytes, hashed with SHA-256.

    Args:
        n (int, optional): The length of the ID to be returned. Defaults to 32.

    Returns:
        str: A unique ID of the specified length.
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(32)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def create_path(
    dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, 
    time_prefix: bool = False
) -> str:
    """
    Create a file path with optional timestamp inclusion and directory creation.

    Args:
        dir_path (str): The directory path where the file will be located.
        filename (str): The name of the file.
        timestamp (bool, optional): Flag to include a timestamp in the filename. Defaults to True.
        dir_exist_ok (bool, optional): Flag to allow existing directories. Defaults to True.
        time_prefix (bool, optional): Flag to place the timestamp as a prefix or suffix. Defaults to False.

    Returns:
        str: The constructed file path including the directory, filename, and optional timestamp.

    Notes:
        If the directory does not exist, it will be created unless dir_exist_ok is False.
        The timestamp format is YYYYMMDD_HHMMSS.
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

def get_bins(input: List[str], upper: int) -> List[List[int]]:
    """
    Organize indices of the input list into bins where the cumulative length of strings does not exceed the upper limit.

    Args:
        input (List[str]): The input list of strings.
        upper (int): The upper limit for the cumulative length of strings in each bin.

    Returns:
        List[List[int]]: A list of bins, each bin is a list of indices from the input list.

    Notes:
        This function can be used to partition data into chunks where each chunk has a maximum cumulative length.
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

def get_cpu_architecture() -> str:
    """
    Determine the CPU architecture of the system.

    Returns:
        str: A string indicating the CPU architecture. Returns 'apple_silicon' for ARM architectures,
             and 'other_cpu' for all other CPU types.
    """
    arch = platform.machine()
    if 'arm' in arch or 'aarch64' in arch:
        return 'apple_silicon'
    else:
        return 'other_cpu'

def get_timestamp() -> str:
    """
    Generate a timestamp string in ISO format with colons and periods replaced by underscores.

    Returns:
        str: The current timestamp in 'YYYY-MM-DDTHH_MM_SS_SSSSSS' format.
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def split_path(path: str) -> tuple:
    """
    Split a file path into folder name and file name.

    Args:
        path (str): The full path to split.

    Returns:
        tuple: A tuple containing the folder name and file name.
    """
    folder_name = os.path.dirname(path)
    file_name = os.path.basename(path)
    return (folder_name, file_name)

def str_to_num(
    input: str, upper_bound: float = None, lower_bound: float = None, 
    num_type: type = int, precision: int = None
) -> Any:
    """
    Convert a string to a number, enforcing optional upper and lower bounds.

    Args:
        input (str): The input string containing the number to convert.
        upper_bound (float, optional): The maximum allowable value of the number.
        lower_bound (float, optional): The minimum allowable value of the number.
        num_type (type): The type of number to convert to (e.g., int, float).
        precision (int, optional): The precision for rounding if converting to a float.

    Returns:
        Any: The number extracted and converted from the string, of type specified by num_type.

    Raises:
        ValueError: If no numeric values are found, or if the converted number violates the specified bounds.
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

def strip_lower(input: Any) -> str:
    """
    Convert an input to string, strip leading and trailing spaces, and convert to lowercase.

    Args:
        input (Any): The input to be processed.

    Returns:
        str: The processed string if conversion is successful, otherwise returns 'False' as a string.
        
    Raises:
        ValueError: If the input cannot be converted to a string.
    """
    try:
        return str(input).strip().lower()
    except:
        raise ValueError(f"Could not convert input to string: {input}")

def install_import(package_name, module_name=None, import_name=None, pip_name=None):
    """
    Dynamically import a module or package, installing it via pip if necessary.

    Args:
        package_name (str): The base name of the package.
        module_name (str, optional): The name of the module within the package, if applicable.
        import_name (str, optional): The specific name to import from the module or package.
        pip_name (str, optional): The name of the package in pip, if different from package_name.

    Returns:
        None: This function does not return a value but prints the outcome of the operation.

    Note:
        This function attempts to import the specified package or module and installs it using pip if the import fails.
    """
    if pip_name is None:
        pip_name = package_name  # Defaults to package_name if pip_name is not explicitly provided
    
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
            
def is_schema(dict_: Dict, schema: Dict) -> bool:
    """
    Validate if a dictionary matches a given schema.

    Args:
        dict_ (Dict): The dictionary to validate.
        schema (Dict): A schema with keys and their expected types.

    Returns:
        bool: True if the dictionary matches the schema, False otherwise.

    Note:
        The function checks if each key in the schema exists in the dictionary and matches the expected type.
    """
    for key, expected_type in schema.items():
        if not isinstance(dict_[key], expected_type):
            return False
    return True

def is_package_installed(package_name: str) -> bool:
    """
    Check if a package is installed in the current environment.

    Args:
        package_name (str): The name of the package to check.

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    package_spec = importlib.util.find_spec(package_name)
    return package_spec is not None

def is_same_dtype(input_: Any, dtype: type = None) -> bool:
    """
    Check if all elements in a collection have the same data type as specified or as the first element's type.

    Args:
        input_ (Any): The input collection, can be a list or a dictionary.
        dtype (type, optional): The data type to check against. If not provided, the type of the first element is used.

    Returns:
        bool: True if all elements in the collection match the specified data type, False otherwise.

    Note:
        For dictionaries, it checks the data type of the values.
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

def to_df(
    item: Any, how: str = 'all', drop_kwargs: Dict = {}, reset_index: bool = True, 
    **kwargs
) -> pd.DataFrame:
    """
    Convert various item types (list, pandas DataFrame) into a pandas DataFrame with options for cleaning and resetting the index.

    Args:
        item (Any): The item to be converted into a DataFrame. Can be a list or a DataFrame.
        how (str, optional): How to drop rows with missing values. Defaults to 'all'.
        drop_kwargs (Dict, optional): Additional keyword arguments for pd.DataFrame.dropna(). Defaults to {}.
        reset_index (bool, optional): Whether to reset the index of the final DataFrame. Defaults to True.
        **kwargs: Additional keyword arguments for pd.DataFrame.reset_index() if reset_index is True.

    Returns:
        pd.DataFrame: The resulting DataFrame after conversions and cleaning.

    Raises:
        ValueError: If there's an error during conversion or processing of the DataFrame.
    """
    try:
        dfs = ''
        
        if isinstance(item, List):
            if is_same_dtype(item, pd.DataFrame):
                dfs = pd.concat(item)
            dfs = pd.DataFrame(item)

        elif isinstance(item, pd.DataFrame):
            dfs = item

        drop_kwargs['how'] = how
        dfs = dfs.dropna(**drop_kwargs)
        
        if reset_index:
            drop = kwargs.pop('drop', True)
            inplace = kwargs.pop('inplace', True)
            dfs.reset_index(drop=drop, inplace=inplace, **kwargs)
            
        return dfs
    
    except Exception as e:
        raise ValueError(f'Error converting items to DataFrame: {e}')   
    
def timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert a timestamp into a datetime object.

    Args:
        timestamp (float): The timestamp to convert.

    Returns:
        datetime: The datetime object corresponding to the given timestamp.
    """
    return datetime.fromtimestamp(timestamp)

def _extract_first_number(inputstr: str) -> str:
    """
    Extract the first number from a string.
    
    Args:
        input (str): The input string to search for numbers.
        
    Returns:
        str: The first number found in the string, or None if no numbers are found.
    """
    numbers = re.findall(r'-?\d+\.?\d*', inputstr)
    return numbers[0] if numbers else None

def _convert_to_num(number_str: str, num_type: type = int, precision: int = None) -> Any:
    """
    Convert a string to a specified numeric type, optionally rounding to a given precision.
    
    Args:
        number_str (str): The number in string format to convert.
        num_type (type): The type of number to convert to, e.g., int or float.
        precision (int, optional): The number of decimal places to round to, for floating-point conversions.
        
    Returns:
        Any: The converted number, either as an int or float, depending on num_type.
    """
    if num_type is int:
        return int(float(number_str))
    elif num_type is float:
        return round(float(number_str), precision) if precision is not None else float(number_str)
    else:
        raise ValueError(f"Invalid number type: {num_type}")
    