import re

from typing import Optional, Union, Iterable

from .flat_util import flatten_list


def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: type = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    numbers = re.findall(r'-?\d+\.?\d*', input_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {input_}")
    
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
    
def to_list(input_, flatten=True, dropna=False):
    if isinstance(input_, list) and flatten:
        input_ = flatten_list(input_)
        if dropna:
            input_ = [i for i in input_ if i is not None]
    elif isinstance(input_, Iterable) and not isinstance(input_, (str, dict)):
        try:
            input_ = list(input_)
        except:
            raise ValueError("Input cannot be converted to a list.")
    else:
        input_ = [input_]
    return input_

