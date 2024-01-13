import inspect
import unittest
from typing import Any, Dict, Tuple, Type

import csv
import binascii
import re
from datetime import datetime
from dateutil import parser
import io
from typing import List, Union, Any, Optional, Type
import unittest

def infer_type_from_string(input_str: str) -> Union[int, float, bool, str]:
    """Infer the type of the input string and return the value in the inferred type.

    Args:
        input_str: A string whose type is to be inferred.

    Returns:
        The input string converted to an integer, float, boolean, or string.

    Examples:
        >>> infer_type_from_string("42")
        42
        >>> infer_type_from_string("3.14")
        3.14
        >>> infer_type_from_string("true")
        True
        >>> infer_type_from_string("hello")
        'hello'
    """
    try:
        return int(input_str)
    except ValueError:
        pass

    try:
        return float(input_str)
    except ValueError:
        pass

    if input_str.lower() in ['true', 'false']:
        return input_str.lower() == 'true'

    return input_str

def str_to_datetime(datetime_str: str, fmt: Optional[str] = None) -> datetime:
    """Convert a string representation of a date and time to a datetime object.

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
    """Convert the first numeric value in the input string to the specified number type.

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


def _extract_docstring_details_google(func: Type[Any]) -> Tuple[str, Dict[str, str]]:
    """
    Extracts the function description and parameter descriptions from a docstring following the Google style guide.

    Args:
        func (Type[Any]): The function from which to extract docstring details.

    Returns:
        A tuple containing the function description and a dictionary of parameter descriptions.

    Examples:
        def example_function(param1: int, param2: str) -> bool:
            '''
            Determines if the string representation of param1 is equal to param2.

            Args:
                param1 (int): The integer to compare.
                param2 (str): The string to compare.

            Returns:
                True if param1 as a string is equal to param2, False otherwise.
            '''
            return str(param1) == param2

        description, params = _extract_docstring_details_google(example_function)
        print(description)  # Output: Determines if the string representation of param1 is equal to param2.
        print(params)       # Output: {'param1': 'The integer to compare.', 'param2': 'The string to compare.'}
    """
    docstring = inspect.getdoc(func)
    if not docstring:
        return "No description available.", {}

    lines = docstring.split('\n')
    func_description = lines[0].strip()

    param_start_pos = 0
    lines_len = len(lines)
    
    params_description = {}
    
    for i in range(1, lines_len):
        if lines[i].startswith(('Args', 'Arguments', 'Parameters')):
            param_start_pos = i + 1
            break

    current_param = None
    for i in range(param_start_pos, lines_len):
        if lines[i] == '':
            continue
        elif lines[i].startswith(' '):
            param_desc = lines[i].split(':', 1)
            if len(param_desc) == 1:
                params_description[current_param] += ' ' + param_desc[0].strip()
                continue
            param, desc = param_desc
            param = param.split('(')[0].strip()
            params_description[param] = desc.strip()
            current_param = param
        else:
            break

    return func_description, params_description
