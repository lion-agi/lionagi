import re
from typing import Any, Dict, Generator, Iterable, List, MutableMapping, Optional, Union
import json


def _flatten(input_iter: Iterable, dropna: bool) -> Iterable[Any]:
    for item in input_iter:
        if isinstance(item, Iterable) and not isinstance(item, str):
            yield from _flatten(item, dropna)
        elif not dropna or item is not None:
            yield item
            
            
def to_list(input: Union[Iterable, Any], flatten: bool = True, dropna: bool = True) -> List[Any]:
    if input is None:
        raise ValueError("None type cannot be converted to a list.")

    if isinstance(input, MutableMapping):  # Input is a dictionary
        # Convert dictionary to list of tuples (key, value) and then flatten if required
        iterables = [(k, v) for k, v in input.items()]
    elif isinstance(input, Iterable) and not isinstance(input, str):
        # Directly use iterables except for strings which should be treated as scalars
        iterables = input
    else:
        # Treat anything else as a single-value iterable
        iterables = [input]

    # Now we need to flatten the iterable if required
    if flatten:
        return list(_flatten(iterables, dropna))
    else:
        return list(iterables)


def _flatten_dict(input: Dict[str, Any], parent_key: str = '', 
                  sep: str = '_') -> Generator[tuple[str, Any], None, None]:

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

    return dict(_flatten_dict(input, parent_key, sep))

def _flatten_list(input: List[Any], dropna: bool = True) -> Generator[Any, None, None]:

    for element in input:
        if isinstance(element, list):
            yield from _flatten_list(element, dropna)
        elif element is not None or not dropna:
            yield element

def to_list(input: Union[Iterable, Any], flatten_dict: bool = False, flat: bool = True, 
            dropna: bool = True, parent_key: str = '', sep: str = '_') -> List[Any]:

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
    