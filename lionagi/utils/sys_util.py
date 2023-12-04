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
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def _flatten_dict(input: Dict[str, Any], parent_key: str = '', 
                  sep: str = '_') -> Generator[tuple[str, Any], None, None]:
    """
    Flatten a nested dictionary into a flat dictionary.

    This function recursively flattens a nested dictionary, using a separator
    to concatenate nested keys into a single key. It handles nested dictionaries
    and lists within the dictionary.

    Args:
        input (Dict[str, Any]): The dictionary to flatten.
        parent_key (str, optional): A string to prepend to keys. Defaults to ''.
        sep (str, optional): The separator to use between nested keys. Defaults to '_'.

    Yields:
        Generator[tuple[str, Any], None, None]: A generator yielding tuples of 
        the form (key, value), where 'key' is the flattened key and 'value' is 
        the associated value.

    Examples:
        >>> sample_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        >>> list(_flatten_dict(sample_dict))
        [('a', 1), ('b_c', 2), ('b_d_e', 3)]

        >>> sample_dict_with_list = {"a": 1, "b": [{"c": 2}, {"d": 3}]}
        >>> list(_flatten_dict(sample_dict_with_list))
        [('a', 1), ('b_0_c', 2), ('b_1_d', 3)]
    """
    for key, value in input.items():
        new_key = f'{parent_key}{sep}{key}' if parent_key else key
        if isinstance(value, MutableMapping):
            yield from _flatten_dict(value, new_key, sep=sep)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, MutableMapping):
                    yield from _flatten_dict(item, f'{new_key}{sep}{i}', sep=sep)
                else:
                    yield (f'{new_key}{sep}{i}', item)
        else:
            yield (new_key, value)


def to_flat_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Converts a nested dictionary into a flat dictionary.

    This function takes a dictionary with potentially nested structures and 
    flattens it, using a specified separator to concatenate nested keys.

    Args:
        d (Dict[str, Any]): The dictionary to be flattened.
        parent_key (str, optional): The initial key to use for nested keys. Defaults to ''.
        sep (str, optional): Separator used between nested keys. Defaults to '_'.

    Returns:
        Dict[str, Any]: A flat dictionary with concatenated keys.

    Example:
        >>> nested_dict = {'a': 1, 'b': {'c': 2}}
        >>> to_flat_dict(nested_dict)
        {'a': 1, 'b_c': 2}
    """
    return dict(_flatten_dict(d, parent_key=parent_key, sep=sep))

def _flatten_list(lst: List[Any], dropna: bool = True) -> Generator[Any, None, None]:
    """
    Flattens a nested list into a single-level list.

    This function recursively flattens nested lists. It can optionally drop 'None' values
    from the list.

    Args:
        lst (List[Any]): The list to flatten.
        dropna (bool, optional): Whether to drop 'None' values. Defaults to True.

    Yields:
        Generator[Any, None, None]: A generator yielding elements from the flattened list.

    Example:
        >>> nested_list = [1, [2, 3, None], 4]
        >>> list(flatten_list(nested_list))
        [1, 2, 3, 4]
    """
    for el in lst:
        if isinstance(el, list):
            yield from _flatten_list(el, dropna=dropna)
        else:
            if el is not None or not dropna:
                yield el

def to_list(input_: Union[Iterable, Any], flat_dict: bool = False, flat: bool = True, dropna: bool = True) -> List[Any]:
    """
    Converts a given input into a list, with options to flatten and handle dictionaries.

    This function is versatile, capable of converting various types of input into a list.
    It can handle flattening of nested lists and dictionaries. It also has options to
    drop 'None' values and to handle dictionary inputs specially.

    Args:
        input_ (Union[Iterable, Any]): The input to be converted into a list.
        flat_dict (bool, optional): If True and the input is a dictionary, it gets flattened. Defaults to False.
        flat (bool, optional): If True, the output list is flattened. Defaults to True.
        dropna (bool, optional): If True, 'None' values are dropped in the flattening process. Defaults to True.

    Raises:
        ValueError: If the input is None, callable, or cannot be converted to a list.

    Returns:
        List[Any]: The resulting list after applying the specified transformations.

    Example:
        >>> to_list({'a': 1, 'b': [2, 3]}, flat_dict=True)
        [{'a': 1}, {'b_0': 2}, {'b_1': 3}]
    """
    if input_ is None or callable(input_):
        raise ValueError("Unsupported type: None or callable types are not convertable to a list.")
    
    try:
        if isinstance(input_, dict):
            if flat_dict:
                input_ = dict(_flatten_dict(input_))  # Flatten and convert to dictionary first
                return [{k: v} for k, v in input_.items()]
            out = [input_]
        elif isinstance(input_, Iterable) and not isinstance(input_, str):
            out = list(input_)
        else:
            out = [input_]
        
        if flat: # Flatten if necessary
            out = list(_flatten_list(out, dropna=dropna))

        return out
    except TypeError as e:
        raise ValueError(f"Unable to convert input to list. Error: {e}")
    
def str_to_num(str_: str, 
               upper_bound: Union[int, float] = 100, 
               lower_bound: Union[int, float] = 1, 
               type_: type = int, 
               precision: int = None) -> Union[int, float, str]:
    """
    Extracts the first numeric value from a string and converts it to a specified type,
    enforcing upper and lower bounds.

    This function searches for numeric values in a given string, converts the first
    found value to either an integer or a float (as specified), and then checks if this
    value is within a specified range. If the value is outside the range, a message is
    returned instead of the number.

    Args:
        str_ (str): The string to search for numeric values.
        upper_bound (Union[int, float], optional): The upper bound for the numeric value. Defaults to 100.
        lower_bound (Union[int, float], optional): The lower bound for the numeric value. Defaults to 1.
        type_ (type, optional): The type to convert the numeric value to, either int or float. Defaults to int.
        precision (int, optional): The number of decimal places for rounding if type_ is float. Defaults to None.

    Raises:
        ValueError: If upper_bound is less than lower_bound, or if no numeric values are found in the string,
                    or if there is an error during conversion.

    Returns:
        Union[int, float, str]: The converted numeric value, or a message if the value is out of bounds.

    Example:
        >>> str_to_num("Value is 123.45 in the range", type_=float, precision=1)
        123.4
        >>> str_to_num("Temperature -5.6 degrees", -10, 10)
        -6
        >>> str_to_num("Out of range value 150", 1, 100)
        'Number 150 is greater than the upper bound of 100.'
    """
    if upper_bound < lower_bound:
        raise ValueError("upper_bound must be greater than or equal to lower_bound")

    numbers = re.findall(r'-?\d+\.?\d*', str_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {str_}")
    
    num_str = numbers[0]  # Take the first numeric string match
    try:
        if type_ == float:
            num = float(num_str)
            if precision is not None:
                num = round(num, precision)
        else:
            num = int(float(num_str))  # Convert via float for strings like "123.45"

        if lower_bound <= num <= upper_bound:
            return num
        elif num < lower_bound:
            return f"Number {num} is less than the lower bound of {lower_bound}."
        elif num > upper_bound:
            return f"Number {num} is greater than the upper bound of {upper_bound}."
    except ValueError as e:
        raise ValueError(f"Error converting string to number: {e}")

def make_copy(input_: Any, n: int) -> Any:
    """
    Creates a deep copy of the input object a specified number of times.

    This function makes one or more deep copies of the provided input. If the specified
    number of copies is greater than 1, a list of deep copies is returned.

    Args:
        input_ (Any): The object to be copied.
        n (int): The number of deep copies to create.

    Raises:
        ValueError: If the number of copies, n, is not a positive integer.

    Returns:
        Any: A deep copy of the input, or a list of deep copies if n > 1.

    Example:
        >>> sample_dict = {'key': 'value'}
        >>> make_copy(sample_dict, 2)
        [{'key': 'value'}, {'key': 'value'}]
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a positive integer: {n}")
    if n == 1: 
        return copy.deepcopy(input_)
    else:
        return [copy.deepcopy(input_) for _ in range(n)]

def to_temp(input_: Any, flat_dict: bool = False, flat: bool = False, dropna: bool = False) -> tempfile._TemporaryFileWrapper:
    """
    Converts the input to a list (with options to flatten it) and writes it to a temporary file in JSON format.

    This function is useful for serializing data to a temporary JSON file for 
    transient storage or testing purposes. It includes options to flatten dictionaries
    and lists in the input.

    Args:
        input_ (Any): The input to be converted and written to a temporary file.
        flat_dict (bool, optional): If True, flatten dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flatten lists in the input. Defaults to False.
        dropna (bool, optional): If True, drop None values during flattening. Defaults to False.

    Raises:
        TypeError: If the input data is not JSON serializable.

    Returns:
        tempfile._TemporaryFileWrapper: A temporary file containing the JSON serialized data.

    Example:
        >>> temp_file = to_temp({'a': 1, 'b': [2, 3]}, flat_dict=True)
        >>> temp_file.name  # Doctest: +ELLIPSIS
        '/tmp/...'
    """
    input_ = to_list(input_, flat_dict, flat, dropna)
    
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input_, temp)
    except TypeError as e:
        temp.close()  # Ensure the file is closed before raising the error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp.close()
    return temp

def to_csv(input_: List[Dict[str, Any]],
           filename: str,
           out: bool = False,
           file_exist_ok: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    Writes a list of dictionaries to a CSV file.

    This function writes a list of dictionaries to a CSV file, with dictionary keys
    as column headers. It can also return the original input if specified. The function
    ensures the specified file path exists or creates it if allowed.

    Args:
        input_ (List[Dict[str, Any]]): The list of dictionaries to write to a CSV file.
        filename (str): The path to the output CSV file.
        out (bool, optional): If True, return the original input list. Defaults to False.
        file_exist_ok (bool, optional): If True, create the directory for the file if it doesn't exist. Defaults to False.

    Raises:
        FileNotFoundError: If the directory for the file does not exist and file_exist_ok is False.

    Returns:
        Optional[List[Dict[str, Any]]]: The original input list if out is True, otherwise None.

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> to_csv(data, 'people.csv')
    """
    if not os.path.exists(os.path.dirname(filename)) and os.path.dirname(filename) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filename)} does not exist.")

    with open(filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input_[0].keys())
        writer.writeheader()
        writer.writerows(input_)

    return input_ if out else None

def hold_call(input_: Any, 
              func_: Callable, 
              hold: int = 1, 
              msg: Optional[str] = None, 
              ignore: bool = False, 
              **kwargs) -> Any:
    """
    Executes a function after a specified delay, handling exceptions optionally.

    This function waits for a given number of seconds (hold) before calling the 
    provided function with the input. If an exception occurs during the function call, 
    it prints a custom message (if provided) and optionally re-raises the exception.

    Args:
        input_ (Any): The input to pass to the function.
        func_ (Callable): The function to be executed.
        hold (int, optional): The time in seconds to wait before calling the function. Defaults to 1.
        msg (Optional[str], optional): A custom message to print in case of an exception. Defaults to None.
        ignore (bool, optional): If True, ignores the exception and doesn't re-raise it. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call.

    Raises:
        Exception: Reraises the exception if ignore is False.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> hold_call(5, add_one, hold=2)
        6
    """
    try:
        time.sleep(hold)
        return func_(input_, **kwargs)
    except Exception as e:
        if msg:
            print(f"{msg} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore:
            raise

async def ahold_call(input_: Any, 
                     func_: Callable, 
                     hold: int = 5, 
                     msg: Optional[str] = None, 
                     ignore: bool = False, 
                     **kwargs) -> Any:
    """
    Asynchronously executes a function after a specified delay, handling exceptions optionally.

    This function waits for a given number of seconds (hold) before calling the 
    provided asynchronous function with the input. If an exception occurs during 
    the function call, it prints a custom message (if provided) and optionally 
    re-raises the exception.

    Args:
        input_ (Any): The input to pass to the function.
        func_ (Callable): The asynchronous function to be executed.
        hold (int, optional): The time in seconds to wait before calling the function. Defaults to 5.
        msg (Optional[str], optional): A custom message to print in case of an exception. Defaults to None.
        ignore (bool, optional): If True, ignores the exception and doesn't re-raise it. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the asynchronous function call.

    Raises:
        Exception: Reraises the exception if ignore is False.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(ahold_call(5, async_add_one, hold=2))
        6
    """
    try:
        if not asyncio.iscoroutinefunction(func_):
            raise TypeError(f"The function {func_} must be an asynchronous function.")
        await asyncio.sleep(hold)
        return await func_(*input_, **kwargs)
    except Exception as e:
        if msg:
            print(f"{msg} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore:
            raise

def l_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies a function to each element of the input, after converting it to a list.

    This function converts the input to a list (with options to flatten dictionaries and lists),
    and then applies a given function to each element of the list.

    Args:
        input_ (Any): The input to be converted to a list and processed.
        func_ (Callable): The function to apply to each element of the list.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens lists in the input. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the function to each element.

    Raises:
        ValueError: If the function cannot be applied to the input.

    Example:
        >>> def square(x):
        ...     return x * x
        >>> l_call([1, 2, 3], square)
        [1, 4, 9]
    """
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        return [func_(i) for i in lst]
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

async def al_call(input_: Any, 
                  func_: Callable, 
                  flat_dict: bool = False, 
                  flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies a function to each element of the input, after converting it to a list.

    This function converts the input to a list (with options to flatten dictionaries and lists),
    and then applies a given asynchronous function to each element of the list asynchronously.

    Args:
        input_ (Any): The input to be converted to a list and processed.
        func_ (Callable): The asynchronous function to apply to each element of the list.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens lists in the input. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the function to each element.

    Raises:
        ValueError: If the function cannot be applied to the input.

    Example:
        >>> async def async_square(x):
        ...     return x * x
        >>> asyncio.run(al_call([1, 2, 3], async_square))
        [1, 4, 9]
    """
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        tasks = [func_(i) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

def m_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies multiple functions to corresponding elements of the input.

    This function maps a list of functions to a list of inputs. Each function is applied
    to its corresponding input. The function assumes that the number of inputs and functions
    are equal and throws an assertion error otherwise.

    Args:
        input_ (Any): The input or list of inputs.
        func_ (Callable): The function or list of functions to apply.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens the output list. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: The list of results from applying each function to its corresponding input.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> m_call([1, 2], [add_one, add_one])
        [2, 3]
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "The number of inputs and functions must be the same."
    return to_list([l_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
                    for f, inp in zip(lst_func, lst_input)], flat=True)

async def am_call(input_: Any, 
                  func_: Callable, 
                  flat_dict: bool = False, 
                  flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies multiple functions to corresponding elements of the input.

    This function asynchronously maps a list of functions to a list of inputs. 
    Each function is applied to its corresponding input. The function assumes 
    that the number of inputs and functions are equal and throws an assertion error otherwise.

    Args:
        input_ (Any): The input or list of inputs.
        func_ (Callable): The function or list of functions to apply.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens the output list. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: The list of results from applying each function to its corresponding input.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(am_call([1, 2], [async_add_one, async_add_one]))
        [2, 3]
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "Input and function counts must match."
    
    tasks = [al_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
             for f, inp in zip(lst_func, lst_input)]
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)

def e_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies each function in a list of functions to all elements in the input.

    This function expands the input to match the number of functions and then
    applies each function to the entire input. Useful for applying a series of
    different transformations to the same input.

    Args:
        input_ (Any): The input or list of inputs.
        func_ (Callable): The function or list of functions to apply.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens the output list. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list of results after applying each function to the input.

    Example:
        >>> def square(x):
        ...     return [i * i for i in x]
        >>> e_call([1, 2, 3], [square])
        [[1, 4, 9]]
    """

    f = lambda x, y: m_call(make_copy(x, len(to_list(y))), y, 
                            flat_dict=flat_dict, flat=flat, dropna=dropna)
    return to_list([f(inp, func_) for inp in to_list(input_)], flat=flat)

async def ae_call(input_: Any, 
                  func_: Callable, 
                  flat_dict: bool = False, 
                  flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies each function in a list of functions to all elements in the input.

    This function asynchronously expands the input to match the number of functions and 
    then applies each function to the entire input. Useful for applying a series of 
    different asynchronous transformations to the same input.

    Args:
        input_ (Any): The input or list of inputs.
        func_ (Callable): The function or list of functions to apply.
        flat_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.
        flat (bool, optional): If True, flattens the output list. Defaults to False.
        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying each function to the input.

    Example:
        >>> async def async_square(x):
        ...     return [i * i for i in x]
        >>> asyncio.run(ae_call([1, 2, 3], [async_square]))
        [[1, 4, 9]]
    """
    async def async_f(x, y):
        return await am_call(make_copy(x, len(to_list(y))), y, flat_dict=flat_dict, flat=flat, dropna=dropna)

    tasks = [async_f(inp, func_) for inp in to_list(input_)]
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

def generate_id() -> str:
    """
    Generates a unique ID based on the current time and random bytes.

    This function combines the current time in ISO 8601 format with 16 random bytes
    to create a unique identifier. The result is hashed using SHA-256 and the first
    16 characters of the hexadecimal digest are returned.

    Returns:
        str: A 16-character unique identifier.

    Example:
        >>> generate_id()  # Doctest: +ELLIPSIS
        '...'
    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(16)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:16]

def make_filepath(dir_: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True) -> str:
    """
    Creates a file path by optionally appending a timestamp to the filename.

    This function constructs a file path by combining a directory, an optional timestamp,
    and a filename. It also ensures the existence of the directory.

    Args:
        dir_ (str): The directory in which the file is to be located.
        filename (str): The name of the file.
        timestamp (bool, optional): If True, appends a timestamp to the filename. Defaults to True.
        dir_exist_ok (bool, optional): If True, creates the directory if it doesn't exist. Defaults to True.

    Returns:
        str: The full path to the file.

    Example:
        >>> make_filepath('/tmp/', 'log.txt', timestamp=False)
        '/tmp/log.txt'
    """
    os.makedirs(dir_, exist_ok=dir_exist_ok)
    if timestamp:
        timestamp = get_timestamp()
        return f"{dir_}{timestamp}{filename}"
    else:
        return f"{dir_}{filename}"
    
def append_to_jsonl(data: Any, filename: str) -> None:
    """
    Appends data to a JSON lines (jsonl) file.

    This function serializes the given data to a JSON-formatted string and appends it
    to a file, with each entry on a new line. Suitable for logging or data collection
    where entries are added over time.

    Args:
        data (Any): The data to be serialized and appended.
        filename (str): The path to the jsonl file.

    Example:
        >>> append_to_jsonl({"key": "value"}, "data.jsonl")
        # This will append {"key": "value"} to the file data.jsonl
    """
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")
