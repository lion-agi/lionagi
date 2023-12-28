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

import asyncio
import copy
import csv
import json
import os
import re
import tempfile
import time
import hashlib
from datetime import datetime
from collections.abc import Generator, Iterable, MutableMapping
from typing import Any, Callable, Dict, List, Optional, Union


def _flatten_dict(input: Dict[str, Any], parent_key: str = '', 
                  sep: str = '_') -> Generator[tuple[str, Any], None, None]:
    """
    Recursively flattens a nested dictionary into a flat dictionary.

    This generator function traverses a nested dictionary, concatenating nested keys 
    into a single key using the provided separator. It handles both nested dictionaries
    and lists within the dictionary.

    Parameters:
        input (Dict[str, Any]): The dictionary to be flattened.

        parent_key (str, optional): Initial key for nested structures. Defaults to ''.

        sep (str, optional): Separator for concatenated key. Defaults to '_'.

    Yields:
        Generator[tuple[str, Any], None, None]: Tuples of flattened keys and their values.

    Examples:
        >>> example_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        >>> list(_flatten_dict(example_dict))
        [('a', 1), ('b_c', 2), ('b_d_e', 3)]

        >>> example_dict_with_list = {"a": 1, "b": [{"c": 2}, {"d": 3}]}
        >>> list(_flatten_dict(example_dict_with_list))
        [('a', 1), ('b_0_c', 2), ('b_1_d', 3)]
    """
    for key, value in input.items():
        composed_key = f'{parent_key}{sep}{key}' if parent_key else key
        if isinstance(value, MutableMapping):
            yield from _flatten_dict(value, composed_key, sep=sep)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, MutableMapping):
                    yield from _flatten_dict(item, f'{composed_key}{sep}{i}', sep=sep)
                else:
                    yield (f'{composed_key}{sep}{i}', item)
        else:
            yield (composed_key, value)

def to_flat_dict(input: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Transforms a nested dictionary into a flat dictionary.

    This function flattens a dictionary with potentially nested structures, concatenating
    nested keys using the specified separator. It leverages the '_flatten_dict' generator
    function for efficient processing.

    Parameters:
        input (Dict[str, Any]): The nested dictionary to flatten.

        parent_key (str, optional): Initial key for nested structures. Defaults to ''.

        sep (str, optional): Separator for concatenated keys. Defaults to '_'.

    Returns:
        Dict[str, Any]: The resulting flat dictionary.

    Example:
        >>> example_nested_dict = {'a': 1, 'b': {'c': 2}}
        >>> to_flat_dict(example_nested_dict)
        {'a': 1, 'b_c': 2}
    """
    return dict(_flatten_dict(input, parent_key, sep))

def _flatten_list(input: List[Any], dropna: bool = True) -> Generator[Any, None, None]:
    """
    Recursively flattens a nested list into a single-level list.

    This generator function iterates through a list, flattening nested lists into a single 
    level. It provides an option to exclude 'None' values from the output, enhancing its utility.

    Parameters:
        input (List[Any]): The list to be flattened.

        dropna (bool, optional): Flag to indicate whether 'None' values should be omitted. Defaults to True.

    Yields:
        Generator[Any, None, None]: Elements from the flattened list.

    Example:
        >>> example_nested_list = [1, [2, 3, None], 4]
        >>> list(_flatten_list(example_nested_list))
        [1, 2, 3, 4]
    """
    for element in input:
        if isinstance(element, list):
            yield from _flatten_list(element, dropna)
        elif element is not None or not dropna:
            yield element

def to_list(input: Union[Iterable, Any], flatten_dict: bool = False, flat: bool = True, 
            dropna: bool = True, parent_key: str = '', sep: str = '_') -> List[Any]:
    """
    Converts a given input into a list, optionally flattening nested structures.

    This function converts various inputs into a list, with optional handling for 
    flattening nested lists and dictionaries, and dropping 'None' values. If 'flatten_dict'
    is True and the input is a dictionary, it is flattened before conversion.

    Parameters:
        input (Union[Iterable, Any]): The input to convert.

        flatten_dict (bool, optional): Flatten dictionary input. Defaults to False.

        flat (bool, optional): Flatten the output list. Defaults to True.

        dropna (bool, optional): Drop 'None' values during flattening. Defaults to True.

        parent_key (str, optional): The parent key for flattening dictionaries. Defaults to an empty string.

        sep (str, optional): The separator for creating flattened dictionary keys. Defaults to '_'.

    Raises:
        ValueError: If input is None, callable, or unconvertible to a list.

    Returns:
        List[Any]: The resulting list after applying transformations.

    Example:
        >>> to_list({'a': 1, 'b': [2, 3]}, flatten_dict=True)
        [{'a': 1}, {'b_0': 2}, {'b_1': 3}]
    """

    if input is None:
        raise ValueError("Unsupported type: None are not convertible to a list.")
    
    try:
        if isinstance(input, dict):
            if flatten_dict:
                input = dict(_flatten_dict(input, parent_key, sep))  # Flatten and convert to dictionary first
                return [{k: v} for k, v in input.items()]
            output = [input]
        elif isinstance(input, Iterable) and not isinstance(input, str):
            output = list(input)
        else:
            output = [input]
        
        if flat:  # Flatten if necessary
            output = list(_flatten_list(output, dropna))
        return output
    
    except TypeError as e:
        raise ValueError(f"Unable to convert input to list. Error: {e}")

def str_to_num(input: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: type = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    """
    Converts found numeric value in a string to a specified type.

    This function searches a string for numeric values and converts it to an integer 
    or a float, based on the specified type. It also validates the converted value 
    against optional upper and lower bounds.

    Parameters:
        input (str): String to search for numeric values.

        upper_bound (Optional[Union[int, float]]): Upper limit for the numeric value. None for no limit.

        lower_bound (Optional[Union[int, float]]): Lower limit for the numeric value. None for no limit.

        num_type (type): Desired type for the numeric value (int or float).

        precision (Optional[int]): Decimal places for rounding if float. None for no rounding.

    Raises:
        ValueError: If no numeric values are found, for conversion errors, or if the number is out of bounds.

    Returns:
        Union[int, float]: The converted numeric value, if within specified bounds.

    Example:
        >>> str_to_num("Temperature is -5.6 degrees", num_type=float, precision=1)
        -5.6
        >>> str_to_num("Value is approximately 200", upper_bound=150)
        ValueError: Number 200 is greater than the upper bound of 150.
    """
    numbers = re.findall(r'-?\d+\.?\d*', input)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {input}")
    
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

def to_temp(input: Any, 
            flatten_dict: bool = False, 
            flat: bool = False, 
            dropna: bool = False):
    """
    Converts input to a list and writes it to a temporary file in JSON format, with flattening options.

    This function serializes data to a temporary JSON file, useful for transient storage or testing. 
    It includes options to flatten the input if it contains dictionaries or lists.

    Parameters:
        input (Any): The data to be converted and written to a file.

        flatten_dict (bool, optional): Flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Flatten lists in the input. Defaults to False.

        dropna (bool, optional): Exclude 'None' values during flattening. Defaults to False.

    Raises:
        TypeError: If the input is not JSON serializable.

    Example:
        >>> temp_file = to_temp({'a': 1, 'b': [2, 3]}, flatten_dict=True)
        >>> temp_file.name  # Doctest: +ELLIPSIS
        '/var/folders/.../tmp...'
    """
    input = to_list(input, flatten_dict, flat, dropna)
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input, temp_file)
    except TypeError as e:
        temp_file.close()  # Ensuring file closure before raising error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp_file.close()
    return temp_file

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

def hold_call(input: Any, 
              func: Callable, 
              sleep: int = 0.1, 
              message: Optional[str] = None, 
              ignore_error: bool = False, 
              **kwargs) -> Any:
    """
    Executes a function after a specified delay, handling exceptions optionally.

    Waits for 'sleep' seconds before calling 'func' with 'input'. Handles exceptions by
    printing a message and optionally re-raising them.

    Parameters:
        input (Any): Input to the function.

        func (Callable): Function to execute.

        sleep (int, optional): Time in seconds to wait before calling the function. Defaults to 0.1.

        message (Optional[str], optional): Message to print on exception. Defaults to None.

        ignore_error (bool, optional): If True, ignores exceptions. Defaults to False.

        **kwargs: Additional keyword arguments for the function.

    Returns:
        Any: Result of the function call.

    Raises:
        Exception: Re-raises the exception unless 'ignore_error' is True.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> hold_call(5, add_one, sleep=2)
        6
    """
    try:
        time.sleep(sleep)
        return func(input, **kwargs)
    except Exception as e:
        if message:
            print(f"{message} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore_error:
            raise

async def ahold_call(input: Any, 
                     func: Callable, 
                     sleep: int = 5, 
                     message: Optional[str] = None, 
                     ignore_error: bool = False, 
                     **kwargs) -> Any:
    """
    Asynchronously executes a function after a specified delay, handling exceptions optionally.

    Waits for 'sleep' seconds before calling 'func' with 'input'. Handles exceptions by
    printing a message and optionally re-raising them.

    Parameters:
        input (Any): Input to the function.

        func (Callable): Asynchronous function to execute.

        sleep (int, optional): Time in seconds to wait before calling the function. Defaults to 5.

        message (Optional[str], optional): Message to print on exception. Defaults to None.

        ignore_error (bool, optional): If True, ignores exceptions. Defaults to False.

        **kwargs: Additional keyword arguments for the function.

    Returns:
        Any: Result of the asynchronous function call.

    Raises:
        Exception: Re-raises the exception unless 'ignore_error' is True.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(ahold_call(5, async_add_one, sleep=2))
        6
    """
    try:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"The function {func} must be an asynchronous function.")
        await asyncio.sleep(sleep)
        return await func(input, **kwargs)
    except Exception as e:
        if message:
            print(f"{message} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore_error:
            raise

def l_call(input: Any, 
           func: Callable, 
           flatten_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True, **kwags) -> List[Any]:
    """
    Applies a function to each element of `input`, after converting it to a list.

    This function converts the `input` to a list, with options to flatten structures 
    and lists, and then applies a given `func` to each element of the list.

    Parameters:
        input (Any): The input to be converted to a list and processed.

        func (Callable): The function to apply to each element of the list.

        flatten_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.

        flat (bool, optional): If True, flattens nested lists in the input. Defaults to False.

        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the `func` to each element.

    Raises:
        ValueError: If the `func` cannot be applied to the `input`.

    Example:
        >>> def square(x):
        ...     return x * x
        >>> l_call([1, 2, 3], square)
        [1, 4, 9]
    """
    try:
        lst = to_list(input, flatten_dict, flat, dropna)
        return [func(i, **kwags) for i in lst]
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

async def al_call(input: Any, 
                  func: Callable, 
                  flatten_dict: bool = False, 
                  flat: bool = False, 
                  dropna: bool = True, **kwags) -> List[Any]:
    """
    Asynchronously applies a function to each element of `input`, after converting it to a list.

    This function converts the `input` to a list, with options to flatten 
    dictionaries and lists, and then applies a given asynchronous `func` to 
    each element of the list asynchronously.

    Parameters:
        input (Any): The input to be converted to a list and processed.

        func (Callable): The asynchronous function to apply to each element of the list.

        flatten_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.

        flat (bool, optional): If True, flattens nested lists in the input. Defaults to False.

        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the `func` to each element.

    Raises:
        ValueError: If the `func` cannot be applied to the `input`.

    Example:
        >>> async def async_square(x):
        ...     return x * x
        >>> asyncio.run(al_call([1, 2, 3], async_square))
        [1, 4, 9]
    """
    try:
        lst = to_list(input, flatten_dict, flat, dropna)
        tasks = [func(i, **kwags) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

def m_call(input: Union[Any, List[Any]], 
           func: Union[Callable, List[Callable]], 
           flatten_dict: bool = False, 
           flat: bool = True, 
           dropna: bool = True, **kwags) -> List[Any]:
    """
    Maps multiple functions to corresponding elements of the input.

    This function applies a list of functions to a list of inputs, with each function
    being applied to its corresponding input element. It asserts that the number of inputs
    and functions are the same and raises an error if they are not.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results from applying each function to its corresponding input.

    Raises:
        ValueError: If the number of provided inputs and functions are not the same.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> m_call([1, 2], [add_one, add_one])
        [2, 3]
    """
    input = to_list(input, flatten_dict, flat, dropna)
    func = to_list(func)
    assert len(input) == len(func), "The number of inputs and functions must be the same."
    return to_list([l_call(inp, f, flatten_dict, flat, dropna, **kwags) 
                    for f, inp in zip(func, input)])

async def am_call(input: Union[Any, List[Any]], 
                  func: Union[Callable, List[Callable]], 
                  flatten_dict: bool = False, 
                  flat: bool = True, 
                  dropna: bool = True, **kwags) -> List[Any]:
    """
    Asynchronously applies multiple functions to corresponding elements of the input.

    This asynchronous function maps a list of functions to a list of inputs, with each 
    function being applied to its corresponding input element asynchronously. It ensures 
    that the number of inputs and functions are the same, raising a `ValueError` if not.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results from applying each function to its corresponding input.

    Raises:
        ValueError: If the number of inputs and functions do not match.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(am_call([1, 2], [async_add_one, async_add_one]))
        [2, 3]
    """
    input = to_list(input, flatten_dict, flat, dropna)
    func = to_list(func)
    assert len(input) == len(func), "Input and function counts must match."
    
    tasks = [al_call(inp, f, flatten_dict, flat, dropna, **kwags) 
             for f, inp in zip(func, input)]
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)

def e_call(input: Any, 
           func: Callable, 
           flatten_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True, **kwags) -> List[Any]:
    """
    Applies each function in a list of functions to all elements in the input.

    This function expands the input to match the number of functions and then
    applies each function to the entire input. It is useful for applying a series
    of different transformations to the same input.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list of results after applying each function to the input.

    Example:
        >>> def square(x):
        ...     return x**2
        >>> e_call([1, 2, 3], [square])
        [[1], [4], [9]]
    """

    _f = lambda x, y: m_call(create_copy(x, len(to_list(y))), y, 
                            flatten_dict=flatten_dict, flat=flat, dropna=dropna, **kwags)
    return to_list([_f(inp, func) for inp in to_list(input)], flat=flat)

async def ae_call(input_: Any, 
                  func_: Callable, 
                  flatten_dict: bool = False,
                  flat: bool = False, 
                  dropna: bool = True, **kwags):
    """
    Asynchronously applies each function in a list of functions to all elements in the input.

    This asynchronous function expands the input to match the number of functions and 
    then asynchronously applies each function to the entire input. It is useful for applying a series 
    of different asynchronous transformations to the same input.

    Parameters:
        input_ (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func_ (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Example:
        >>> async def async_square(x):
        ...     return x**2
        >>> asyncio.run(ae_call([1, 2, 3], [async_square]))
        [[1, 4, 9]]
    """
    async def _async_f(x, y):
        return await am_call(create_copy(x, len(to_list(y))), y, flatten_dict=flatten_dict, flat=flat, dropna=dropna, **kwags)

    tasks = [_async_f(inp, func_) for inp in to_list(input_)]
    return await asyncio.gather(*tasks)

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

def create_id() -> str:
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
    return hashlib.sha256(current_time + random_bytes).hexdigest()

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

