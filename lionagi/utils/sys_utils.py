from collections.abc import Iterable, MutableMapping
import re

def flatten_dict(_dict: dict, parent_key=None, seperator: str='_') -> dict:
    """
    utility function to convert a nested dictionary into a flattened dictionary recursively to the lowest level, return as a flattened dictionary

    Args:
        dictionary (dict): the nested dictionary to be flattened
        parent_key (bool, optional): add the key of immediate enclosing parent dictionary to the nested dictionary within. Defaults to True
        separator (str, optional): Seperator between parent key and the next child key. Defaults to '_'.

    Returns:
        dict: a flattened dictionary
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

def __flatten_list(xs: list):
    """
    utility generator to flatten a nested list recursively to the lowest level, return the elements in the flattened list

    Args:
        xs (list): nested dict to be flattened

    Yields:
        Any: element in the flattened list
    """
    for x in xs:
        if isinstance(x, list):
            yield from __flatten_list(x)
        else:
            yield x

def _flatten_list(_input: list) -> list:
    """
    Main function for calling _flatten_list
    
    Args:
        _input (list): _description_

    Returns:
        list: _description_
    """
    return [i for i in __flatten_list(_input) if i is not None]


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
                    outs [(_input).items()]
            elif isinstance(_input, str):
                outs = [_input]
            else:
                outs = [i for i in _input.__iter__()]
        else:
            outs = [_input]
        return _flatten_list(outs) if flat else outs
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
    


