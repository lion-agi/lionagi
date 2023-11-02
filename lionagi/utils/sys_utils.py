# Standard Library Imports
import re
import copy
import json
import tempfile
import csv
import os
import time

# Asynchronous Programming
import asyncio

# Typing Imports
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Union


def _flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_"):
    """
    Flatten a nested dictionary recursively (Generator function).

    This generator function takes a dictionary that may contain nested dictionaries as its values
    and yields key-value pairs where nesting is removed, and keys are composite of 
    parent and child keys separated by a separator.

    Parameters:
    - d (Dict[str, Any]): Input dictionary to be flattened.
    - parent_key (str, optional): Key to be used as parent key in the new flattened dictionary. Defaults to "".
    - sep (str, optional): Separator to be used between parent and child keys. Defaults to "_".

    Yields:
    - key-value pairs in flattened form.

    Example:
    >>> d = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    >>> flat_d = dict(_flatten_dict(d))
    >>> flat_d  # Output: {'a': 1, 'b_c': 2, 'b_d_e': 3}
    """
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k  # Generate new key based on parent_key and separator
        if isinstance(v, MutableMapping):
            # Recursively flatten the nested dictionary and yield from it
            yield from _flatten_dict(v, new_key, sep)
        elif isinstance(v, list):
            # If a list is encountered, enumerate through the list and recursively flatten
            for i, item in enumerate(v):
                yield from _flatten_dict({str(i): item}, new_key)
        else:
            # Yield the key-value pair
            yield (new_key, v)
            
def to_flat_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """
    Flatten a nested dictionary recursively. 

    This function takes a dictionary that may contain nested dictionaries as its values
    and returns a new dictionary where nesting is removed, and keys are composite of 
    parent and child keys separated by a separator.

    Parameters:
    - d (Dict[str, Any]): Input dictionary to be flattened.
    - parent_key (str, optional): Key to be used as parent key in the new flattened dictionary. Defaults to "".
    - sep (str, optional): Separator to be used between parent and child keys. Defaults to "_".

    Returns:
    - Dict[str, Any]: Flattened dictionary.

    Example:
    >>> d = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
    >>> flat_d = to_flat_dict(d)
    >>> flat_d  # Output: {'a': 1, 'b_c': 2, 'b_d_e': 3}
    """
    return dict(_flatten_dict(d, parent_key=parent_key, sep=sep))

def _flatten_list(lst: List[Any]):
    """
    Flatten a nested list (Generator function).

    This generator function takes a list that may contain nested lists as its elements
    and yields values in a flattened manner.

    Parameters:
    - lst (List[Any]): Input list to be flattened.

    Yields:
    - Elements in flattened form.

    # Examples:
    >>> list(_flatten_list([1, 2, [3, 4, [5, 6], 7], 8]))
    [1, 2, 3, 4, 5, 6, 7, 8]
    """
    for el in lst:
        if isinstance(el, list):
            # If an element is a list, recursively flatten it and yield from it
            yield from _flatten_list(el)
        else:
            # Yield the element
            yield el

def to_flat_list(lst: List[Any], dropna: bool = True) -> List[Any]:
    """
    Convert to a flat list.

    This function takes a list that may contain nested lists and/or None values
    and returns a new list where nesting is removed. Optionally, None values can be dropped.

    Parameters:
    - lst (List[Any]): Input list to be flattened.
    - dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
    - List[Any]: Flattened list.

    Example:
    >>> to_flat_list([1, None, 2, [3, None, 4, [5, None], 6], 7, None, 8])
    [1, 2, 3, 4, 5, 6, 7, 8]
    """
    if dropna:
        return [el for el in _flatten_list(lst) if el is not None]
    else:
        return list(_flatten_list(lst))

def to_list(input_: Union[Iterable, Any], flat_dict: bool = False, flat: bool = True, dropna: bool = True) -> List[Any]:
    """
    Convert various types to a list.

    This function takes an input of various types (iterables, dictionaries, or single values)
    and converts it into a list. It has options for flattening dictionaries and lists.

    Parameters:
    - input_ (Union[Iterable, Any]): Input to be converted to a list.
    - flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
    - flat (bool, optional): Whether to return a flattened list. Defaults to True.
    - dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
    - List[Any]: Converted list.

    Examples:
        >>> to_list({"a": 1, "b": {"c": 2}}, flat_d=True)
        >>> output: [{'a': 1}, {'b_c': 2}]
        >>> to_list([1, 2, [3, 4]])
        >>> output: [1, 2, 3, 4]
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
        return to_flat_list(out, dropna=dropna) if flat else out
    except Exception as e:
        raise ValueError(f"Input can't be converted to list. Error: {e}")
    
def str_to_num(str_: str, upper_bound: Union[int, float]=100, 
                        lower_bound: Union[int, float]=1, type_: type=int, precision: int=None) -> Union[int, float, str]:
    """
    Convert a string to a number within specified bounds.

    This function takes a string and extracts numbers from it. 
    It then converts the extracted number to the specified type 
    and checks if it falls within the defined bounds.

    Parameters:
    - str_ (str): Input string containing the number.
    - upper_bound (Union[int, float], optional): Upper bound for the number. Defaults to 100.
    - lower_bound (Union[int, float], optional): Lower bound for the number. Defaults to 1.
    - type_ (type, optional): Type to which the number should be converted. Defaults to int.
    - precision (int, optional): Number of decimal places if the type is float. Defaults to None.

    Returns:
    - Union[int, float, str]: Converted number or a string indicating out-of-bound value.

    Example:
    >>> str_to_num("abc 123", upper_bound=200)
    >>> 123  # Output
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
    Create multiple deep copies of an object.

    Parameters:
    - input_ (Any): The object to be copied.
    - n (int): Number of copies.

    Returns:
    - List[Any]: List of deep copies.

    Example:
    >>> create_multiple_copies({"a": 1}, 2)
    >>> [{"a": 1}, {"a": 1}]  # Output
    """
    return [copy.deepcopy(input_) for _ in range(n)]

def dict_to_temp(d: Dict[str, Any]) -> tempfile.NamedTemporaryFile:
    """
    Save a dictionary to a temporary file.

    Parameters:
    - d (Dict[str, Any]): The dictionary to be saved.

    Returns:
    - tempfile.NamedTemporaryFile: The temporary file object.

    Example:
    >>> temp_file = dict_to_temp_file({"a": 1})
    >>> temp_file.name  # Output will be the temporary file's name.
    """
    temp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump(d, temp)
    temp.close()
    return temp

def to_csv(input_, filename, out=False, exist_ok=False):
    """
    Converts a list of dictionaries to a CSV file.
    
    Args:
        input_ (list): List of dictionaries to be converted to CSV.
        filename (str): Name of the csv file to write the data to.
        out (bool): Whether to return the list of dictionaries as is.
        exist_ok (bool): Whether to create the directory if it does not exist.

    Returns:
        list or None: Returns the list of dictionaries if `out` is True, otherwise None.
    """
    # Check if the directory exists. If not, create it.
    dir_name = os.path.dirname(filename)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=exist_ok)
    
    # Convert input_ to a list of dictionaries
    list_of_dicts = input_
    
    # Extract headers from the first dictionary, assuming all dictionaries have the same keys
    if list_of_dicts:
        headers = list(list_of_dicts[0].keys())
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            writer.writeheader()
            for row in list_of_dicts:
                writer.writerow(row)

    if out:
        return list_of_dicts

# Hold call, a delayed call with error handling
def hold_call(input_, func_, hold=5, msg=None, ignore=False, **kwargs):
    """
    Executes a function after a specified hold time and handles exceptions.

    Args:
        input_ (Any): The input to the function.
        func_ (Callable): The function to execute.
        hold (int, optional): The time in seconds to wait before executing the function. Defaults to 5.
        msg (str, optional): The message to display in case of an error.
        ignore (bool, optional): Whether to ignore errors and print the message. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function execution or None if 'ignore' is True and an exception occurs.

    Raises:
        Exception: If any error occurs during function execution and 'ignore' is False.
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
        
# Asynchronous hold call
async def ahold_call(input_, func_, hold=5, msg=None, ignore=False, **kwargs):
    """
    Asynchronously executes a function after a specified hold time and handles exceptions.

    Args:
        input_ (Any): The input to the function.
        func_ (Callable): The async function to execute.
        hold (int, optional): The time in seconds to wait before executing the function. Defaults to 5.
        msg (str, optional): The message to display in case of an error.
        ignore (bool, optional): Whether to ignore errors and print the message. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function execution or None if 'ignore' is True and an exception occurs.

    Raises:
        Exception: If any error occurs during function execution and 'ignore' is False.
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

# List call, applies function on each element in a list
def l_call(input_: Any, func_: Callable, 
           flat_dict: bool = False, flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies a function to each element in a list, where the list is created from the input.

    Args:
        input_ (Any): The input to convert into a list.
        func_ (Callable): The function to apply to each element in the list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the function.

    Raises:
        ValueError: If the given function is not callable or cannot be applied to the input.
    """
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        return [func_(i) for i in lst]
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

# Asynchronous list call, applies function on each element in a list
async def al_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies a function to each element in a list, where the list is created from the input.

    Args:
        input_ (Any): The input to convert into a list.
        func_ (Callable): The async function to apply to each element in the list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying the function.

    Raises:
        ValueError: If the given function is not callable or cannot be applied to the input.
    """
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        tasks = [func_(i) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

# Map call, applies function on each element in a list, element-wise mapped
def m_call(input_: Any, func_: Callable, 
           flat_dict: bool = False, flat: bool = False, 
           dropna: bool=True) -> List[Any]:
    """
    Applies multiple functions to multiple inputs. Each function is applied to its corresponding input.

    Args:
        input_ (Any): The inputs to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the functions to the inputs.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "The number of inputs and functions must be the same."
    return to_list([l_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) for f, inp in zip(lst_func, lst_input)], flat=True)

# Asynchronous map call, applies function on each element in a list, element-wise mapped
async def am_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool=True) -> List[Any]:
    """
    Asynchronously applies multiple functions to multiple inputs. Each function is applied to its corresponding input.

    Args:
        input_ (Any): The inputs to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying the functions to the inputs.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.
    """
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "The number of inputs and functions must be the same."
    
    tasks = [al_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) for f, inp in zip(lst_func, lst_input)]
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)

# Explode call, applies a list of functions to each element in the input list
def e_call(input_: Any, func_: Callable, 
           flat_dict: bool = False, flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    """
    Applies a list of functions to each element in the input list.

    Args:
        input_ (Any): The input to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the functions to the inputs.
    """
    f = lambda x, y: m_call(create_copies(x, len(to_list(y))), y, flat_dict=flat_dict, flat=flat, dropna=dropna)
    return to_list([f(inp, func_) for inp in to_list(input_)], flat=flat)

# Asynchronous explode call, applies a list of functions to each element in the input list
async def ae_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    """
    Asynchronously applies a list of functions to each element in the input list.

    Args:
        input_ (Any): The input to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_dict (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to False.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying the functions to the inputs.
    """
    async def async_f(x, y):
        return await am_call(create_copies(x, len(to_list(y))), y, flat_dict=flat_dict, flat=flat, dropna=dropna)

    tasks = [async_f(inp, func_) for inp in to_list(input_)]
    return await asyncio.gather(*tasks)
