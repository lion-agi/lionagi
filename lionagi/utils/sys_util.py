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


from typing import Any, List, Dict


def to_dict(input_: Any) -> Dict[Any, Any]:
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
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)
        
def create_copy(input: Any, n: int = 1) -> Any:
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n: int = 32) -> str:
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(32)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def create_path(
    dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, 
    time_prefix: bool = False
) -> str:
    dir = dir + '/' if not dir.endswith('/') else dir
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
    else:
        name, ext = filename, ''
    os.makedirs(dir, exist_ok=dir_exist_ok)
    timestamp_str = get_timestamp() if timestamp else ''
    filename = f"{timestamp_str}{name}" if time_prefix else f"{name}{timestamp_str}"
    return f"{dir}{filename}.{ext}" if ext != '' else f"{dir}{filename}"

def get_bins(input: List[str], upper: int) -> List[List[int]]:
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
    arch = platform.machine()
    if 'arm' in arch or 'aarch64' in arch:
        return 'apple_silicon'
    else:
        return 'other_cpu'

def get_timestamp() -> str:
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def split_path(path: str) -> tuple:
    folder_name = os.path.dirname(path)
    file_name = os.path.basename(path)
    return (folder_name, file_name)

def str_to_num(
    input: str, upper_bound: float = None, lower_bound: float = None, 
    num_type: type = int, precision: int = None
) -> Any:
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
    try:
        return str(input).strip().lower()
    except:
        raise ValueError(f"Could not convert input to string: {input}")

def install_import(package_name, module_name=None, import_name=None, pip_name=None):
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
    for key, expected_type in schema.items():
        if not isinstance(dict_[key], expected_type):
            return False
    return True

def is_package_installed(package_name: str) -> bool:
    package_spec = importlib.util.find_spec(package_name)
    return package_spec is not None

def is_same_dtype(input_: Any, dtype: type = None) -> bool:
    
    if isinstance(input_, list):
        dtype = dtype or type(input_[0])    
        return all(isinstance(i, dtype) for i in input_)
    
    elif isinstance(input_, dict):
        dtype = dtype or type(list(input_.values())[0])
        return (isinstance(v, dtype) for _, v in input_.items())

    else:
        dtype = dtype or type(input_)
        return isinstance(input_, dtype)

def timestamp_to_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp)

def _extract_first_number(inputstr: str) -> str:
    numbers = re.findall(r'-?\d+\.?\d*', inputstr)
    return numbers[0] if numbers else None

def _convert_to_num(number_str: str, num_type: type = int, precision: int = None) -> Any:
    if num_type is int:
        return int(float(number_str))
    elif num_type is float:
        return round(float(number_str), precision) if precision is not None else float(number_str)
    else:
        raise ValueError(f"Invalid number type: {num_type}")
