
import re
from typing import Any, Dict, Generator, Iterable, List, MutableMapping, Optional, Union

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
    