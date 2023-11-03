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

import re
import copy
import json
import tempfile
import csv
import os
import time
import asyncio

from typing import (Any, 
                    Callable, 
                    Dict, 
                    Iterable, 
                    List, 
                    MutableMapping, 
                    Union, 
                    Generator, 
                    Optional)

def _flatten_dict(d: Dict[str, Any], 
                  parent_key: str = "", 
                  sep: str = "_") -> Generator:
    """
    Creates a generator that flattens a nested dictionary.

    This function takes a dictionary that may have nested dictionaries as
    values and flattens it by combining the keys into a single string using
    a specified separator.

    Parameters:
        d (Dict[str, Any]): The dictionary to be flattened.
        parent_key (str, optional): An initial prefix to prepend to keys.
            Defaults to an empty string.
        sep (str, optional): The string that separates the concatenated keys.
            Defaults to an underscore ("_").

    Yields:
        Tuple[str, Any]: A pair of the new key and its corresponding value in
        the flattened structure.

    Examples:
        >>> complex_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        >>> flat_items = list(_flatten_dict(complex_dict))
        >>> print(flat_items)
        [('a', 1), ('b_c', 2), ('b_d_e', 3)]

    Notes:
        - Nested dictionaries are expanded and their keys are concatenated.
        - Lists within the dictionary are enumerated, and their indices become
          part of the keys.
    """
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, MutableMapping):
            yield from _flatten_dict(v, new_key, sep)   
        elif isinstance(v, list):
            for i, item in enumerate(v):
                yield from _flatten_dict({str(i): item}, new_key)    
        else:
            yield (new_key, v)


def to_flat_dict(d: Dict[str, Any], 
                 parent_key: str = "", 
                 sep: str = "_") -> Dict[str, Any]:
    """
    Transforms a nested dictionary into a single-level dictionary with 
    concatenated keys.

    Parameters:
        d (Dict[str, Any]): A potentially nested dictionary to be transformed
            into a flat structure.
        parent_key (str, optional): A prefix to add to each key in the 
            flattened dictionary. Default is an empty string.
        sep (str, optional): A string used to separate the elements of
            concatenated keys. Default is "_".

    Returns:
        Dict[str, Any]: The flattened dictionary where each key represents a 
        path through the original nested keys.

    Examples:
        >>> complex_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        >>> flat_version = to_flat_dict(complex_dict)
        >>> print(flat_version)
        {'a': 1, 'b_c': 2, 'b_d_e': 3}

    Notes:
        - If `parent_key` is provided, it will be prepended to each key followed
          by the separator.
        - The function is particularly useful when dealing with JSON-like data
          structures that need to be simplified for analysis or storage.
    """
    return dict(_flatten_dict(d, parent_key=parent_key, sep=sep))

def _flatten_list(lst: List[Any]) -> Generator:
    
    """
    Generates a sequence of elements by flattening a nested list.

    This function takes a list that can contain multiple levels of nested lists
    and yields each element in a sequential order, regardless of its depth in
    the original list.

    Parameters:
        lst (List[Any]): The list to be flattened. It can be a simple list or
        one with nested sublists.

    Yields:
        Any: The next element in the flattened version of the original nested
        list.

    Examples:
        >>> complex_list = [1, [2, [3, 4], 5], 6]
        >>> flattened_list = list(_flatten_list(complex_list))
        >>> print(flattened_list)
        [1, 2, 3, 4, 5, 6]

    Notes:
        - The function uses recursion to handle lists within lists.
        - It is a generator function, so it yields elements one by one instead
          of returning a list.
    """
    for el in lst:
        if isinstance(el, list):
            yield from _flatten_list(el)
        else:
            yield el


def _flat_list(lst: List[Any], dropna: bool = True) -> List[Any]:
    """
    Flattens a nested list into a single-level list, with an option to exclude None values.

    This function takes a list that may contain other lists as elements and flattens it,
    producing a one-dimensional list. It can also be configured to omit all None values
    from the resulting list.

    Parameters:
        lst (List[Any]): The list to be flattened. It may contain nested lists.
        dropna (bool, optional): Whether to exclude None values from the flattened list.
            Defaults to True, which removes None values.

    Returns:
        List[Any]: A flattened version of the input list. If dropna is True, the resulting
                   list will not contain any None values.

    Examples:
        >>> example_list = [1, [2, None, [3, None], 4], 5]
        >>> _flat_list(example_list)
        [1, 2, 3, 4, 5]
        
        >>> _flat_list(example_list, dropna=False)
        [1, 2, None, 3, None, 4, 5]

    Notes:
        - This function internally uses a generator to perform the flattening.
        - Setting dropna to False retains None values, which may be desired if None
          represents meaningful information, such as missing data.
    """
    if dropna:
        return [el for el in _flatten_list(lst) if el is not None]
    else:
        return list(_flatten_list(lst))


def to_list(input_: Union[Iterable, Any], 
            flat_dict: bool = False, 
            flat: bool = True, 
            dropna: bool = True) -> List[Any]:
    """
    Converts input of various types to a list with options for flattening.

    This function accepts an iterable, dictionary, or single value and converts it
    into a list. It offers options to flatten nested dictionaries into single-key
    entries and to flatten nested lists.

    Parameters:
        input_ (Union[Iterable, Any]): The input to be converted to a list.
        flat_dict (bool, optional): If True, flattens dictionaries such that each
            key-value pair becomes a single-item dictionary in the list.
            Defaults to False.
        flat (bool, optional): If True, flattens any nested lists in the input.
            Defaults to True.
        dropna (bool, optional): If True, removes any 'None' values from the list.
            Defaults to True.

    Returns:
        List[Any]: A list representation of the input. Depending on the flags, this
            list may be flattened and/or have 'None' values removed.

    Raises:
        ValueError: If the input is None, callable, or otherwise not convertible to a list.

    Examples:
        >>> to_list({"a": 1, "b": {"c": 2}}, flat_dict=True)
        [{'a': 1}, {'b_c': 2}]
        
        >>> to_list([1, 2, [3, 4]])
        [1, 2, 3, 4]
    """
    if input_ is None or callable(input_):
        raise ValueError("None or callable types are not supported.")
    
    try:
        out: List[Any] = []
        if isinstance(input_, Iterable):
            if isinstance(input_, dict):
                if flat_dict:
                    out = [{k: v} for k, v in dict(_flatten_dict(input_)).items()]
                else:
                    out = [input_]
            elif isinstance(input_, str):
                out = [input_]
            else:
                out = [i for i in input_]
        else:
            out = [input_]
        return _flat_list(out, dropna=dropna) if flat else out
    except Exception as e:
        raise ValueError(f"Input can't be converted to list. Error: {e}")


def str_to_num(str_: str, 
               upper_bound: Union[int, float]=100, 
               lower_bound: Union[int, float]=1, 
               type_: type=int, 
               precision: int=None) -> Union[int, float, str]:
    """
    Converts a numeric string into a number, ensuring it is within specified bounds.

    This function searches for numeric patterns in a string, converts the found number
    to a specified type, and ensures it lies within an inclusive range defined by
    `lower_bound` and `upper_bound`. If the type is float and `precision` is specified,
    the number is rounded to that many decimal places.

    Parameters:
        str_ (str): The string to extract the number from.
        upper_bound (Union[int, float], optional): The maximum allowable number. 
            Defaults to 100.
        lower_bound (Union[int, float], optional): The minimum allowable number. 
            Defaults to 1.
        type_ (type, optional): The data type to convert the number to. 
            Defaults to int.
        precision (int, optional): The number of decimal places for rounding if the 
            type is float. Only applies when `type_` is float. Defaults to None.

    Returns:
        Union[int, float, str]: The number converted from the string, adhering to
        the specified type and precision, or an explanatory string if the number
        is out of bounds.

    Raises:
        ValueError: If the string does not contain a number, or if the number is not
                    within the specified bounds, or if `upper_bound` is less than 
                    `lower_bound`.

    Example:
        >>> str_to_num("The value is 123.45.")
        123
        >>> str_to_num("123.45", type_=float, precision=1)
        123.5
    """
    try:
        numbers = re.findall(r'\d+\.?\d*', str_)
        num = type_(''.join(numbers))
        if type_ == float and precision is not None:
            num = round(num, precision)
    except Exception as e:
        raise ValueError(f"Error converting string to number. {e}")

    if upper_bound < lower_bound:
        raise ValueError("Upper bound must be greater than lower bound")
    
    if lower_bound <= num <= upper_bound:
        return num
    elif num < lower_bound:
        return f"Number {num} less than lower bound {lower_bound}"
    elif num > upper_bound:
        return f"Number {num} greater than upper bound {upper_bound}"


def create_copies(input_: Any, n: int) -> List[Any]:
    """
    Creates multiple deep copies of a given object.

    Given an input object, this function generates a list containing a specified
    number of deep copies of that object. Deep copying ensures that all nested
    objects are independently duplicated.

    Parameters:
        input_ (Any): The object to duplicate.
        n (int): The number of deep copies to create.

    Returns:
        List[Any]: A list containing 'n' deep copies of the 'input_' object.

    Examples:
        >>> create_copies({"a": 1}, 2)
        [{'a': 1}, {'a': 1}]

    Notes:
        - The 'copy.deepcopy()' function from the 'copy' module is used to create deep copies.
        - This function can be used with any object that is 'deepcopy' compatible.
    """
    return [copy.deepcopy(input_) for _ in range(n)]

def dict_to_temp(d: Dict[str, Any]) -> tempfile.NamedTemporaryFile:
    """
    Writes a dictionary to a named temporary file in JSON format.

    This function takes a dictionary and saves its JSON representation to a
    named temporary file, which can be accessed through the file's name attribute.
    The temporary file is not immediately deleted upon closure, allowing for its
    use even after the file object is closed.

    Parameters:
        d (Dict[str, Any]): The dictionary to serialize and save.

    Returns:
        tempfile.NamedTemporaryFile: A temporary file object that points to the
                                     file containing the JSON data.

    Examples:
        >>> temp_file = dict_to_temp({"a": 1})
        >>> print(temp_file.name)  # Displays the path to the temporary file.
    """
    temp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump(d, temp)
    temp.close()
    return temp


def to_csv(input_: List[Dict[str, Any]], 
           filename: str, 
           out: bool = False,
           exist_ok: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    Converts and writes a list of dictionaries to a CSV file.

    This function expects a uniform list of dictionaries, which it writes
    to a CSV file with headers corresponding to the dictionary keys. It can
    also ensure the existence of the directory for the CSV file and
    optionally return the original data.

    Args:
        input_ (List[Dict[str, Any]]): A list of dictionaries to be written
            to a CSV file.
        filename (str): The file path for the CSV output.
        out (bool, optional): If True, returns the input list of
            dictionaries; otherwise, returns None. Defaults to False.
        exist_ok (bool, optional): If True, will create the directory path
            for the file if it does not exist. Defaults to False.

    Returns:
        Optional[List[Dict[str, Any]]]: The list of dictionaries if `out`
            is True; otherwise, None.

    Raises:
        FileNotFoundError: If the directory does not exist and `exist_ok`
            is False.

    Examples:
        >>> data_dicts = [{'id': 1, 'value': 10}, {'id': 2, 'value': 20}]
        >>> to_csv(data_dicts, 'output.csv')
        # CSV file 'output.csv' is created with data from 'data_dicts'.

        >>> to_csv(data_dicts, 'output.csv', out=True)
        # CSV file 'output.csv' is created, and 'data_dicts' is returned.
    """
    dir_name = os.path.dirname(filename)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=exist_ok)

    list_of_dicts = input_
    if list_of_dicts:
        headers = list(list_of_dicts[0].keys())
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in list_of_dicts:
                writer.writerow(row)
    if out:
        return list_of_dicts


def hold_call(input_: Any, 
              func_: Callable, 
              hold: int = 5, 
              msg: Optional[str] = None, 
              ignore: bool = False, 
              **kwargs) -> Any:
    """
    Delays function execution with optional error handling.

    Executes `func_` with `input_` after a delay, with optional exception
    handling. If `ignore` is True, exceptions are caught and logged; 
    otherwise, they are raised.

    Args:
        input_ (Any): Input to pass to the function.
        func_ (Callable): Function to be executed.
        hold (int, optional): Delay before execution in seconds. 
            Defaults to 5.
        msg (Optional[str], optional): Error message to display on exception. 
            If not provided, a default error message is generated.
        ignore (bool, optional): If True, suppresses and logs exceptions;
            otherwise, exceptions are raised. Defaults to False.
        **kwargs: Additional keyword arguments for `func_`.

    Returns:
        Any: Result of `func_` if successful, None if ignored on error.

    Raises:
        Exception: If `ignore` is False and an exception occurs.
    
    Examples:
        >>> def add(a: int, b: int) -> int:
        ...     return a + b
        >>> hold_call((1, 2), add, hold=2)
        3
        >>> hold_call((1, 'a'), add, hold=2, ignore=True, msg="Add failed.")
        Add failed. Error: ...
    """
    try: 
        time.sleep(hold)
        return func_(input_, **kwargs)
    except Exception as e:
        msg = msg if msg else ''
        msg += f"Error: {e}"
        if ignore:
            print(msg)
            return None
        else:
            raise Exception(msg)


async def ahold_call(input_: Any, 
                     func_: Callable, 
                     hold: int = 5, 
                     msg: Optional[str] = None, 
                     ignore: bool = False, 
                     **kwargs) -> Any:
    """
    Asynchronously calls a function with a delay and optional error handling.

    Waits for a specified duration before calling the provided asynchronous function. 
    If an error occurs, the behavior is determined by the `ignore` flag; the error is 
    either logged or raised.

    Args:
        input_ (Any): Input for the function.
        func_ (Callable): Async function to call.
        hold (int, optional): Delay in seconds before calling `func_`. Default is 5.
        msg (Optional[str], optional): Message to log on error. If None, a default 
            message is generated. Default is None.
        ignore (bool, optional): If True, suppresses and logs errors; otherwise, 
            raises errors. Default is False.
        **kwargs: Extra arguments for `func_`.

    Returns:
        Any: The function's result on success, or None if an error is ignored.

    Raises:
        TypeError: If `func_` is not an asynchronous function.
        Exception: If an error occurs and `ignore` is False.

    Examples:
        >>> async def async_add(a, b): return a + b
        >>> await ahold_call((1, 2), async_add, 2)
        3
        >>> await ahold_call((1, 'a'), async_add, 2, ignore=True, msg="Failed.")
        Failed. Error: ...
    """
    try: 
        if not asyncio.iscoroutinefunction(func_):
            raise Exception(f"Given function {func_} is not a coroutine function.")
        await asyncio.sleep(hold)
        return await func_(input_, **kwargs)
    except Exception as e:
        msg = msg if msg else ''
        msg += f"Error: {e}"
        if ignore:
            print(msg)
            return None
        else:
            raise Exception(msg)


def l_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies a function to elements in a list derived from the input.

    This function converts the input into a list and then applies a provided function 
    to each element in the list. Options to flatten nested structures within the input 
    are available.

    Args:
        input_ (Any): Input to be transformed into a list.
        func_ (Callable): Function to apply to each list element.
        flat_dict (bool, optional): Flatten dictionaries within the input. 
            Defaults to False.
        flat (bool, optional): Flatten nested lists within the input. 
            Defaults to False.
        dropna (bool, optional): Exclude None values from the final list. 
            Defaults to True.

    Returns:
        List[Any]: Results after the function application.

    Raises:
        ValueError: If the function cannot be applied to the input.
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
    Asynchronously applies a function to elements in a list from the input.

    Converts the input into a list and applies an asynchronous function to each element. 
    The function supports flattening of nested lists and dictionaries and can exclude 
    None values.

    Args:
        input_ (Any): Input to be converted into a list.
        func_ (Callable): Async function to apply to each list element.
        flat_dict (bool, optional): Flatten dictionaries in the input. 
            Defaults to False.
        flat (bool, optional): Flatten nested lists in the input. 
            Defaults to False.
        dropna (bool, optional): Omit None values from the list. 
            Defaults to True.

    Returns:
        List[Any]: Async function results for each list element.

    Raises:
        ValueError: If the async function cannot be applied to the input.
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
           dropna: bool=True) -> List[Any]:
    """
    Element-wise applies functions to the corresponding inputs.

    Each input from the provided list is paired with a corresponding function
    from the functions list. The function is then applied to its paired input.

    Args:
        input_ (Any): Inputs to be converted and processed.
        func_ (Callable): Functions to be applied to inputs.
        flat_dict (bool, optional): Flatten input dictionaries. Defaults to False.
        flat (bool, optional): Flatten input lists. Defaults to False.
        dropna (bool, optional): Exclude None values. Defaults to True.

    Returns:
        List[Any]: Results from applying functions to inputs.

    Raises:
        AssertionError: If the count of inputs doesn't match functions.
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "The number of inputs and functions must be the same."
    return to_list([l_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
                    for f, inp in zip(lst_func, lst_input)], flat=True)


async def am_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool=True) -> List[Any]:
    """
    Asynchronously element-wise applies functions to corresponding inputs.

    Similar to `m_call`, but each function is applied asynchronously to its
    corresponding input. This is suited for I/O-bound or high-latency operations.

    Args:
        input_ (Any): Inputs for conversion and processing.
        func_ (Callable): Async functions for input application.
        flat_dict (bool, optional): Flatten dictionaries in inputs. Defaults to False.
        flat (bool, optional): Flatten lists in inputs. Defaults to False.
        dropna (bool, optional): Omit None values from results. Defaults to True.

    Returns:
        List[Any]: Results from async function applications.

    Raises:
        AssertionError: If inputs and functions counts don't align.
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "Input and function counts must match."
    
    tasks = [al_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
             for f, inp in zip(lst_func, lst_input)]
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)


# rewrite these documentation to more readable, understandable and easier to follow, lint with pep-8, and Enforce length limit  -------

# Explode call, applies a list of functions to each element in the input list
def e_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies each function from a list to every element in the input list.

    The input is converted into a list, and each element of this list is then
    passed through a series of functions, effectively 'exploding' the list
    with the results of these function applications.

    Args:
        input_ (Any): Input to convert into a list and process.
        func_ (Callable): Functions to apply to each input element.
        flat_dict (bool, optional): Flatten input dictionaries. Defaults to False.
        flat (bool, optional): Flatten resulting lists. Defaults to False.
        dropna (bool, optional): Exclude None values from results. Defaults to True.

    Returns:
        List[Any]: Results from applying each function to input elements.

    Example:
        >>> e_call([1, 2], [lambda x: x+1, lambda x: x*2])
        [2, 4, 3, 6]  # Assuming flat=True
    """
    f = lambda x, y: m_call(create_copies(x, len(to_list(y))), y, 
                            flat_dict=flat_dict, flat=flat, dropna=dropna)
    return to_list([f(inp, func_) for inp in to_list(input_)], flat=flat)


async def ae_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies each function from a list to every element in the input list.

    Similar to `e_call` but operates asynchronously. This is particularly beneficial
    when the functions involve I/O operations or any other high-latency tasks.

    Args:
        input_ (Any): Input to be converted and processed asynchronously.
        func_ (Callable): Async functions to apply to each input element.
        flat_dict (bool, optional): Flatten dictionaries in input. Defaults to False.
        flat (bool, optional): Flatten resulting lists. Defaults to False.
        dropna (bool, optional): Omit None values from results. Defaults to True.

    Returns:
        List[Any]: Results from applying each function to input elements.

    Example:
        # Assuming 'async_func' is an async function and flat=True
        >>> await ae_call([1, 2], [async_func])
        # Results after asynchronous execution
    """
    async def async_f(x, y):
        return await am_call(create_copies(x, len(to_list(y))), y, flat_dict=flat_dict, flat=flat, dropna=dropna)

    tasks = [async_f(inp, func_) for inp in to_list(input_)]
    return await asyncio.gather(*tasks)