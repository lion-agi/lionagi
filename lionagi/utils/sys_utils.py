from collections.abc import Iterable, MutableMapping
import re

def flatten_dict(_dict: dict, parent_key=None, seperator: str='_') -> dict:
    """
    Utility function to recursively flatten a nested dictionary.

    Parameters:
        nested_dict (dict): The nested dictionary to flatten.
        parent_key (str, optional): Prefix for keys in the flattened dictionary.
        separator (str, optional): Separator between parent and child keys.

    Returns:
        dict: A flattened dictionary.
    """
    items = []
    for key, value in _dict.items():
        new_key = str(parent_key) + seperator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten_dict(value, new_key, seperator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flatten_dict({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)

def flatten_list_gen(nested_list: list):
    """
    Utility generator to recursively flatten a nested list.
    
    Parameters:
        nested_list (list): The nested list to be flattened.
        
    Yields:
        Element in the flattened list.
    """
    for element in nested_list:
        if isinstance(element, list):
            yield from flatten_list_gen(element)
        else:
            yield element

def flatten_list_filter_none(input_list: list) -> list:
    """
    Main function for flattening a nested list and filtering out None values.
    
    Args:
        input_list (list): Nested list to be flattened.

    Returns:
        list: Flattened list with None values filtered out.
    """
    return [element for element in flatten_list_gen(input_list) if element is not None]

def to_list(_input, flat_dict: bool=False, flat=True) -> list:
    """
    Function to convert the input into a list. If the input is Iterable (e.g. set, tuple),
    each item in the iterable will be an element in the list. If the input is a dictionary,
    a list of tuples (key, value) will be returned. However, when flatten_dict is True, 
    a flattened version of dictionary will be used. If the input is a regular non-iterable 
    object, a single-item list will be returned. 

    Parameters:
        _input : Any
            Any type of input that needs to be converted to list.
        flatten_dict : bool, default=False
            If True, returns a list containing the flattened version of 
            the dictionary (key, value) pairs. Otherwise, returns the 
            original (key, value) pairs of dictionary as list.
    Returns:
        List[Any]
            List representation of the input.
    Raises:
        ValueError: If input can't be converted to list.
    """
    try:
        outs = []
        if isinstance(_input, Iterable):
            if isinstance(_input, dict):
                if flat_dict:
                    outs = [flatten_dict(_input).items()]
                else: 
                    outs = [(_input).items()]
            elif isinstance(_input, str):
                outs = [_input]
            else:
                outs = [i for i in _input.__iter__()]
        else:
            outs = [_input]
        return flatten_list_filter_none(outs) if flat else outs
    except Exception as e:
        raise ValueError(f"Given input cannot be converted to list. Error: {e}")

def str_to_num(_str: str, upper_bound: [int, float]=100, 
               lower_bound: [int, float]=1, _type: type=int):
    num=''
    try: 
        numbers = re.findall('\\d+', _str)
        num = _type(''.join(numbers))
    except Exception as e:
        raise ValueError(f"Error converting string to number. {e}")
    
    if lower_bound and upper_bound:
        if upper_bound < lower_bound:
            raise ValueError("Upper bound must be greater than lower bound")
        if lower_bound <= num <= upper_bound:
            return num
        else:
            return f"Number {num} out of range [{lower_bound}, {upper_bound}]"
    elif lower_bound and not upper_bound:
        if lower_bound <= num:
            return num
        else:
            return f"Number {num} less than lower bound {lower_bound}"
    elif upper_bound and not lower_bound:
        if num <= upper_bound:
            return num
        else:
            return f"Number {num} greater than upper bound {upper_bound}"
    elif not lower_bound and not upper_bound:
        return num