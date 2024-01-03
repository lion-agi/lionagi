import re
from typing import Optional, Union, Iterable, List, Any, Type

from .flat_util import flatten_list


def str_to_num(input_: str, 
               upper_bound: Optional[Union[int, float]] = None, 
               lower_bound: Optional[Union[int, float]] = None, 
               num_type: Type[Union[int, float]] = int, 
               precision: Optional[int] = None) -> Union[int, float]:
    """
    Converts the first number in the input string to the specified numeric type.

    Args:
        input_str (str): The input string to extract the number from.
        
        upper_bound (Optional[Union[int, float]]): The upper bound for the number. Defaults to None.
        
        lower_bound (Optional[Union[int, float]]): The lower bound for the number. Defaults to None.
        
        num_type (Type[Union[int, float]]): The type of the number to return (int or float). Defaults to int.
        
        precision (Optional[int]): The precision for the floating-point number. Defaults to None.

    Returns:
        Union[int, float]: The converted number.

    Raises:
        ValueError: If no numeric values are found in the string or if there are conversion errors.
    """
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
    
def to_list(input_: Any, flatten: bool = True, dropna: bool = False) -> List[Any]:
    """
    Converts the input to a list, optionally flattening it and dropping None values.

    Args:
        input_item (Any): The input to convert to a list.
        
        flatten (bool): Whether to flatten the input if it is a nested list. Defaults to True.
        
        dropna (bool): Whether to drop None values from the list. Defaults to False.

    Returns:
        List[Any]: The input converted to a list.

    Raises:
        ValueError: If the input cannot be converted to a list.
    """
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
