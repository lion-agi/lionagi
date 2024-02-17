import os
import copy
import re
from datetime import datetime
from hashlib import sha256
import json

from typing import Any, List, Dict, Iterable, Type

import pandas as pd
from pandas import DataFrame

from .sys_util import SysUtil


def create_copy(input_: Any, num: int = 1) -> Any | List[Any]:
    """
    creates a deep copy of the input. if n is greater than 1, returns a list of deep
    copies.

    Args:
        input_ (Any): The input to copy, which can be of any type.
        num (int, optional): The number of copies to make. default to 1.

    Raises:
        ValueError: If 'n' is not a positive integer.

    Returns: Any | List[Any]: A single deep copy of the input if n is 1, otherwise a
    list of deep copies.

    examples:
        >>> create_copy([1, 2, 3], 2)
        [[1, 2, 3], [1, 2, 3]]
        >>> create_copy('Hello', 3)
        ['Hello', 'Hello', 'Hello']

    """
    if not isinstance(num, int) or num < 1:
        raise ValueError(f"'num' must be a positive integer: {num}")
    if num == 1:
        return copy.deepcopy(input_)
    else:
        return [copy.deepcopy(input_) for _ in range(num)]


def create_id(n: int = 32) -> str:
    """
    Generates a SHA256 hash based on the current time and random bytes, truncated to a
    specified length.

    This function creates a unique identifier by combining the current ISO format time
    and random bytes, then applying a SHA256 hash and truncating the result to a
    specified length. It's useful for generating unique IDs for objects, transactions,
    or sessions where uniqueness and a degree of unpredictability are required.

    Args:
        n (int, optional): The desired length of the hash string.Defaults to 32 characters

    Returns:
        str: A unique hash string of the specified length.

    Examples:
        >>> create_id(8)  # Example output: 'e3b0c442'

    Note:
        The output will vary due to the randomness and current time used in hash
        generation.

    """
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(42)
    return sha256(current_time + random_bytes).hexdigest()[:n]


def get_bins(input_: List[str], upper: Any | None) -> List[List[int]]:
    """
    distributes a list of strings into bins where the total character length per bin
    does not exceed a limit.

    iterates through a list of strings, grouping them into 'bins'. each bin contains
    indices from the original list, ensuring the sum of the lengths of the strings
    referenced by these indices does not exceed the 'upper' limit, if specified. if
    'upper' is None, all strings are placed into a single bin. this approach is
    particularly useful for batch processing tasks where there is a limit on processing
    capacity per batch (e.g., sending SMS messages, API requests), or when no limit is
    desired, facilitating efficient data organization and processing.

    Args:
        input_ (List[str]):
            The list of strings to be distributed into bins.
        upper (int | None, optional):
            The maximum allowed total character length for each bin, or None for no limit.
            defaults to 2000 characters.

    Returns:
        List[List[int]]:
            A list of bins, where each bin is a list of indices from 'input_' that
            meets the length criteria.

    Examples:
        >>> get_bins(["hello", "world", "this", "is", "a", "test"], 10)
        [[0, 1], [2, 3], [4, 5]]
        >>> get_bins(["one", "two", "three", "four", "five"], None)
        [[0, 1, 2, 3, 4]]
    """

    if upper is None:
        upper = 2000

    current = 0
    bins = []
    current_bin = []
    for idx, item in enumerate(input_):

        if current + len(item) < upper:
            current_bin.append(idx)
            current += len(item)

        else:
            bins.append(current_bin)
            current_bin = [idx]
            current = len(item)

    if current_bin:
        bins.append(current_bin)

    return bins


def str_to_num(
        input_: str, upper_bound: float = None, lower_bound: float = None,
        num_type: type = int, precision: int = None) -> Any:
    """
    extracts the first number from a string and converts it to a specified numeric
    type, with optional bounds and precision.

    parses a string to find the first occurrence of a numeric value, then converts this
    number to either an integer or a float, based on the specified `num_type`. the
    function allows for setting optional upper and lower bounds on the numeric value,
    as well as specifying the precision (number of decimal places) for floating-point
    numbers.

    Args:
        input_ (str): The string containing the number to convert.
        upper_bound (float | None, optional):
                The upper limit for the number. if specified, the extracted number must be
                less than this value.
        lower_bound (float | None, optional):
                The lower limit for the number. if specified, the extracted number must be
                greater than this value.
        num_type (type, optional):
                The data type to convert the number to. defaults to `int`.
        precision (int | None, optional):
                The number of decimal places for the number if `num_type` is `float`.
                ignored for integers.

    Returns:
        int | float:
                The extracted and converted number, nested_structure to the specified
                constraints and precision.

    Raises:
        ValueError:
                If no numeric values are found in the string or if the extracted number
                does not meet the specified bounds.

    examples:
        >>> str_to_num("The room number is 42.", upper_bound=100)
        42
        >>> str_to_num("Approximately 3.14159.", num_type=float, precision=2)
        3.14

    """
    number_str = _extract_first_number(input_)
    if number_str is None:
        raise ValueError(f"No numeric values found in the string: {input_}")

    number = _convert_to_num(number_str, num_type, precision)

    if upper_bound is not None and number > upper_bound:
        raise ValueError(
            f"Number {number} is greater than the upper bound of {upper_bound}.")

    if lower_bound is not None and number < lower_bound:
        raise ValueError(
            f"Number {number} is less than the lower bound of {lower_bound}.")

    return number


def strip_lower(input_: Any) -> str:
    """
    Converts an input_ to a stripped, lowercase string.

    Args:
        input_ (Any): The input_ to convert.

    Raises:
        ValueError: If the input_ cannot be converted to a string.

    Returns:
        str: The converted, stripped, and lowercase string.

    Examples:
        >>> strip_lower("  Hello WORLD  ")
        'hello world'
    """

    try:
        return str(input_).strip().lower()

    except Exception as e:
        raise ValueError(f"Could not convert input_ to string: {input_}, Error: {e}")


def to_dict(input_: Any) -> Dict[Any, Any]:
    """
    Converts a JSON string to a dictionary, or returns the input_ if it is already a
    dictionary.

    Args:
        input_ (Any): The input_ JSON string or dictionary.

    Raises:
        ValueError: If the input_ cannot be converted to a dictionary.
        TypeError: If the input_ type is not supported for conversion.

    Returns:
        Dict[Any, Any]: The input_ converted to a dictionary.

    Examples:
        >>> to_dict('{"key": "value"}')
        {'key': 'value'}
        >>> to_dict({'already': 'a dict'})
        {'already': 'a dict'}
    """
    if isinstance(input_, str):
        try:
            return json.loads(input_)

        except Exception as e:
            raise ValueError(f"Could not convert input_ to dict: {e}") from e

    elif isinstance(input_, dict):
        return input_

    else:
        raise TypeError(
            f"Could not convert input_ to dict: {type(input_).__name__} given.")


def to_df(
        item: List[Dict | DataFrame] | DataFrame,
        how: str = 'all',
        drop_kwargs: Dict[str, Any] | None = None,
        reset_index: bool = True,
        **kwargs: Any
) -> DataFrame:
    """
    converts a given item into a pandas DataFrame.

    this function is capable of handling various input types, including lists of
    dictionaries, lists of pandas DataFrames, or a single DataFrame. it provides
    options to drop rows with missing values based on specified criteria ('any' or
    'all') and to reset the index of the resulting DataFrame.

    Args:
        item (Union[List[Dict], List[DataFrame], DataFrame]):
            The item to be converted into a DataFrame. this can be a list of dictionaries,
            a list of DataFrames, or a single DataFrame.
        how (str, optional):
             Specify the method to drop rows with missing values. accepts 'any' or 'all'.
            defaults to 'all'.
        drop_kwargs (Dict[str, Any] | None, optional):
            Additional keyword arguments for the `dropna` method. defaults to None.
        reset_index (bool, optional):
            Whether to reset the index of the resulting DataFrame. defaults to True.
        **kwargs:
            Additional keyword arguments for the `reset_index` method, if `reset_index` is
            True.

    Returns:
        DataFrame:
            A DataFrame created from the input item.

    Raises:
        ValueError:
            If an error occurs during the conversion process.

    Examples:
        Convert a list of dictionaries to a DataFrame:
        >>> data = [{'A': 1, 'B': 2}, {'A': 3, 'B': 4}]
        >>> df = to_df(data)
        >>> print(df)
           A  B
        0  1  2
        1  3  4

        Convert a DataFrame, dropping rows where all values are NA and resetting the index
        >>> df = pd.DataFrame({'A': [1, None], 'B': [None, 4]})
        >>> result = to_df(df, how='all', reset_index=True)
        >>> print(result)
             A    B
        0  1.0  NaN
        1  NaN  4.0
    """
    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        dfs = ''

        if isinstance(item, List):
            if SysUtil.is_same_dtype(item, DataFrame):
                dfs = pd.concat(item)
            if SysUtil.is_same_dtype(item, Dict):
                dfs = pd.DataFrame(item)

        elif isinstance(item, pd.DataFrame):
            dfs = item

        drop_kwargs['how'] = how
        dfs = dfs.dropna(**drop_kwargs)

        if reset_index:
            drop = kwargs.pop('drop', True)
            inplace = kwargs.pop('inplace', True)
            dfs.reset_index(drop=drop, inplace=inplace, **kwargs)

        return dfs

    except Exception as e:
        raise ValueError(f'Error converting items to DataFrame: {e}')


def to_readable_dict(input_: Dict | List) -> str | List:
    """
    Converts a dictionary to a JSON-formatted string with indentation or returns the
    input_ list as is.

    This function is designed to enhance the readability of dictionaries by converting
    them into a JSON-formatted string with proper indentation. If the input is a list,
    it returns the list without modifications. This utility is useful for debugging or
    displaying configuration settings in a more readable format.

    Args:
        input_ (Dict | List):
            A dictionary or list to be converted or returned as is.

    Returns:
        str | List:
            A JSON-formatted string with indentation if the input_ is a dictionary,
            or the input_ list as is without modification.

    Examples:
        Convert a dictionary to a JSON-formatted string:
        >>> to_readable_dict({'a': 1})
        '{\\n    "a": 1\\n}'

        Return a list as is:
        >>> to_readable_dict([1, 2, 3])
        [1, 2, 3]
    """
    if isinstance(input_, dict):
        return json.dumps(input_, indent=4)
    else:
        return input_


def _extract_first_number(input_: str) -> str:
    """
    Extracts the first numerical value from a string.

    Args:
        input_ (str): The string to search for numerical values.

    Returns:
        str: The first numerical value found, or None if no value is found.

    Examples:
        >>> _extract_first_number("Room 42 is open.")
        '42'
    """
    numbers = re.findall(r'-?\d+\.?\d*', input_)

    return numbers[0] if numbers else None


def _convert_to_num(number_str: str, num_type: type = int, precision: int = None) -> Any:
    """
    converts a string representation of a number to a specified numeric type.

    Args:
        number_str (str): The number as a string.
        num_type (type): The type to convert to, either int or float.
        precision (int, optional): The precision for float conversion, ignored for int.

    Raises:
        ValueError: If `num_type` is not int or float.

    Returns:
        Any: The number converted to the specified type.

    examples:
        >>> _convert_to_num('3.14159', float, 2)
        3.14
    """
    if num_type is int:
        return int(float(number_str))

    elif num_type is float:
        return round(float(number_str), precision) if precision is not None else float(
            number_str)

    else:
        raise ValueError(f"Invalid number type: {num_type}")


def is_homogeneous(
    iterables: Dict | List | Iterable,
    type_check: Type
) -> bool:
    """
    checks if all elements in a list conform to the specified type.

    this function iterates over a list to verify that each element matches the
    type specified by `type_check`. it is ideal for ensuring that a collection
    contains elements of only a single, specific type, which is a common requirement
    for operations that cannot process mixed-type data effectively.

    Args:
        iterables (List[Union[Dict, List, Iterable]]):
            The list whose elements are to be checked for type consistency.
        type_check (Type):
            The type (e.g., int, str, dict, list) that all elements in `iterables`
            are expected to match.

    Returns:
        bool: Returns True if all elements in `iterables` are of the `type_check` type;
        otherwise, returns False.

    Examples:
        >>> is_homogeneous([1, 2, 3], int)
        True
        >>> is_homogeneous([{ 'key': 'value' }, { 'another_key': 'another_value' }], dict)
        True
        >>> is_homogeneous([1, 'two', 3], int)
        False
    """
    return all(isinstance(it, type_check) for it in iterables)
