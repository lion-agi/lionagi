from typing import Any, Dict, Iterable, List, MutableMapping, Union, Tuple
import re
import copy

def flatten_dict(d: Dict[str, Any], parent_key: str = None, sep: str = '_') -> Dict[str, Any]:
    """
    Flattens a nested dictionary recursively.
    
    Args:
        d (dict[str, Any]): The dictionary to flatten.
        parent_key (str, optional): The parent key in the case of a nested dictionary. Defaults to None.
        sep (str, optional): The separator to use when combining keys. Defaults to '_'.
        
    Returns:
        dict[str, Any]: The flattened dictionary.
        
    # Examples:
        >>> flatten_dict({'a': 1, 'b': {'c': 2, 'd': 3}})
        {'a': 1, 'b_c': 2, 'b_d': 3})
    """
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        # Build the new key
        new_k = f"{parent_key}{sep}{k}" if parent_key else k
        
        # If the value is a MutableMapping, recurse
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_k, sep).items())
            
        # If the value is a list, iterate and recurse on each value
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict({str(i): item}, new_k).items())
                
        else:
            # If the value is neither a MutableMapping nor a list, add the item to the items list
            items.append((new_k, v))
            
    # Convert the items list back into a dict and return
    return dict(items)

def _flatten_list(lst: List[Any]) -> Iterable:
    """
    Recursively flattens a nested list or a single element into an iterable.
    
    Args:
        lst (List[Any]): A potentially nested list or a single element to flatten.
        
    Yields:
        Iterable: An iterator over the flattened elements.
    
    # Examples:
        >>> list(_flatten_list([1, 2, [3, 4, [5, 6], 7], 8]))
        [1, 2, 3, 4, 5, 6, 7, 8]
    """
    # Check if lst is actually a list
    if not isinstance(lst, list):
        yield lst
        return
    
    # Iterate through the list to flatten nested lists
    for el in lst: 
        if isinstance(el, list): 
            yield from _flatten_list(el)  # Recursive calling for nested lists
        else: 
            yield el  # Yielding non-list elements directly

def to_FlatList(lst: List[Any], dropna=True) -> List[Any]:
    """
    Converts a potentially nested list or a single element into a flattened list with an option to filter None values.
    
    Args:
        lst (List[Any]): A potentially nested list or a single element to flatten.
        dropna (bool, optional): Whether to filter out None values. Defaults to True.
        
    Returns:
        List[Any]: A flattened list.
    
    # Examples:
        >>> to_FlatList([1, None, 2, [3, None, 4, [5, None], 6], 7, None, 8])
        [1, 2, 3, 4, 5, 6, 7, 8]
    """
    # Check whether to filter None values
    if dropna:
        # Filter out None values while flattening
        return [el for el in _flatten_list(lst) if el is not None]
    else:
        # Flatten without filtering None values
        return list(_flatten_list(lst))

def to_lst(input_: Union[Iterable, Any], flat_d: bool = False, flat: bool = True, dropna=True) -> List[Any]:
    """
    Convert various types of input to a list.
    
    Args:
        input_ (Union[Iterable, Any]): The input to convert.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.
    
    Returns:
        List[Any]: A list converted from the input.
    
    Raises:
        ValueError: If the input is None or a callable.
    
    Examples:
        >>> to_lst({"a": 1, "b": {"c": 2}}, flat_d=True)
        [{'a': 1}, {'b_c': 2}]
        >>> to_lst([1, 2, [3, 4]])
        [1, 2, 3, 4]
    """
    if input_ is None or callable(input_):
        raise ValueError("None or callable types are not supported.")
    
    try:
        out: List[Any] = []
        if isinstance(input_, Iterable):
            if isinstance(input_, dict):
                if flat_d:
                    out = [{k: v} for k, v in flatten_dict(input_).items()]
                else:
                    out = [input_]
            elif isinstance(input_, str):
                out = [input_]
            else:
                out = [i for i in input_]
        else:
            out = [input_]
        return to_FlatList(out, dropna=dropna) if flat else out
    except Exception as e:
        raise ValueError(f"Input can't be converted to list. Error: {e}")


def str_to_num(_str: str, upper_bound: Union[int, float]=100, 
               lower_bound: Union[int, float]=1, _type: type=int, precision: int=None):
    """
    Convert a string containing numeric characters to a specified numeric type.
    The function also validates the converted number against optional upper and lower bounds.
    
    Args:
        _str (str): Input string containing numeric characters.
        upper_bound (Union[int, float], optional): The upper limit for the converted number. Defaults to 100.
        lower_bound (Union[int, float], optional): The lower limit for the converted number. Defaults to 1.
        _type (type, optional): The target numeric type to which the string should be converted. Can be int or float. Defaults to int.
        precision (int, optional): The number of decimal places to round to if the target type is float. Defaults to None, meaning no rounding.
    
    Returns:
        Union[int, float, str]: The converted number within the specified bounds, or a string message indicating why the conversion failed.
        
    Raises:
        ValueError: If conversion to the specified numeric type or validation against bounds fails.
        
    Examples:
        >>> str_to_num("value is 45", upper_bound=50, lower_bound=10)
        45
        >>> str_to_num("value is 105", upper_bound=100)
        'Number 105 greater than upper bound 100'
        >>> str_to_num("value is 45.6789", _type=float)
        45.6789
        >>> str_to_num("value is 45.6789", _type=float, precision=2)
        45.68
    """
    
    try:
        # Extract numbers from the string and join them
        numbers = re.findall(r'\d+\.?\d*', _str)
        num = _type(''.join(numbers))
        
        # If the type is float and precision is defined, round to the specified decimal places
        if _type == float and precision is not None:
            num = round(num, precision)
        
    except Exception as e:
        raise ValueError(f"Error converting string to number. {e}")
    
    # Validate the bounds
    if upper_bound < lower_bound:
        raise ValueError("Upper bound must be greater than lower bound")
        
    if lower_bound <= num <= upper_bound:
        return num
    elif num < lower_bound:
        return f"Number {num} less than lower bound {lower_bound}"
    elif num > upper_bound:
        return f"Number {num} greater than upper bound {upper_bound}"
    
def create_copies(_input: Any, n: int) -> List[Any]:
    """
    Create 'n' deep copies of the given input.
    
    Parameters:
        _input: Any
            The input object to be copied.
        n: int
            The number of copies to create.
            
    Returns:
        List[Any]
            A list containing 'n' deep copies of the input.
    """
    return [copy.deepcopy(_input) for _ in range(n)]