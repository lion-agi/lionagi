"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import os
import copy
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Generator, List

def create_copy(input: Any, n: int) -> Any:
    """
    Creates a deep copy of the input object a specified number of times.

    This function makes deep copies of the provided input. If the number of copies ('n') 
    is greater than 1, a list of deep copies is returned. For a single copy, it returns 
    the copy directly.

    Parameters:
        input (Any): The object to be copied.

        n (int): The number of deep copies to create.

    Raises:
        ValueError: If 'n' is not a positive integer.

    Returns:
        Any: A deep copy of 'input' or a list of deep copies if 'n' > 1.

    Example:
        >>> sample_dict = {'key': 'value'}
        >>> make_copy(sample_dict, 2)
        [{'key': 'value'}, {'key': 'value'}]
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n=32) -> str:
    """
    Generates a unique ID based on the current time and random bytes.

    This function combines the current time in ISO 8601 format with 16 random bytes
    to create a unique identifier. The result is hashed using SHA-256 and the first
    16 characters of the hexadecimal digest are returned.

    Returns:
        str: A 16-character unique identifier.

    Example:
        >>> create_id()  # Doctest: +ELLIPSIS
        '...'
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(2048)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def get_timestamp() -> str:
    """
    Generates a current timestamp in a file-safe string format.

    This function creates a timestamp from the current time, formatted in ISO 8601 format, 
    and replaces characters that are typically problematic in filenames (like colons and periods) 
    with underscores.

    Returns:
        str: The current timestamp in a file-safe string format.

    Example:
        >>> get_timestamp()  # Doctest: +ELLIPSIS
        '...'
    """
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_path(dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix=False) -> str:
    """
    Creates a file path by optionally appending a timestamp to the filename.

    This function constructs a file path by combining a directory, an optional timestamp,
    and a filename. It also ensures the existence of the directory.

    Parameters:
        dir (str): The directory in which the file is to be located.

        filename (str): The name of the file.

        timestamp (bool, optional): If True, appends a timestamp to the filename. Defaults to True.

        dir_exist_ok (bool, optional): If True, creates the directory if it doesn't exist. Defaults to True.

        time_prefix (bool, optional): If True, the timestamp is added as a prefix; otherwise, it's appended. Defaults to False.

    Returns:
        str: The full path to the file.

    Example:
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
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    """
    Get index of elements in a list based on their consecutive cumulative sum of length,
    according to some upper threshold. Return lists of indices as bins.
    
    Parameters:
        input (List[str]): List of items to be binned.

        upper (int, optional): Upper threshold for the cumulative sum of the length of items in a bin. Default is 7500.
    
    Returns:
        List[List[int]]: List of lists, where each inner list contains the indices of the items that form a bin.
    
    Example:
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

def task_id_generator() -> Generator[int, None, None]:
    """
    A generator function that yields a sequential series of task IDs.

    Yields:
        int: The next task ID in the sequence, starting from 0.

    Examples:
        task_id_gen = task_id_generator()
        next(task_id_gen) # Yields 0
        next(task_id_gen) # Yields 1
    """
    task_id = 0
    while True:
        yield task_id
        task_id += 1

def change_dict_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)

# def parse_function_call(response: str) -> Tuple[str, Dict]:
#     out = json.loads(response)
#     func = out.get('function', '').lstrip('call_')
#     args = json.loads(out.get('arguments', '{}'))
#     return func, args
