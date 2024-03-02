import json
import re
from functools import singledispatch

from typing import (
    Any,
    Dict,
    List,
    Type,
    Iterable,
    Generator,
)

import pandas as pd
from pydantic import BaseModel

number_regex = re.compile(r"-?\d+\.?\d*")


# to_list functions with datatype overloads
@singledispatch
def to_list(input_: Any, flatten: bool = True, dropna: bool = True) -> List[Any]:
    """
    Converts the input object to a list. This function is capable of handling various input types,
    utilizing single dispatch to specialize for different types such as list, tuple, and set.
    The default implementation handles general iterables, excluding strings, bytes, bytearrays,
    and dictionaries, by attempting to convert them to a list, optionally flattening and dropping
    None values based on the provided arguments.

    Specialized implementations may use additional keyword arguments specific to their conversion logic.

    Args:
        input_ (Any): The input object to convert to a list.
        flatten (bool): If True, and the input is a nested list, the function will attempt to flatten it.
        dropna (bool): If True, None values will be removed from the resulting list.

    Returns:
        List[Any]: A list representation of the input, with modifications based on `flatten` and `dropna`.

    Raises:
        ValueError: If the input type is unsupported or cannot be converted to a list.

    Note:
        - This function uses `@singledispatch` to handle different input types via overloading.
        - The default behavior for dictionaries is to wrap them in a list without flattening.
        - For specific behaviors with lists, tuples, sets, and other types, see the registered implementations.
    """
    try:
        if (
                isinstance(input_, Iterable) and
                not isinstance(input_, (str, bytes, bytearray, dict))
        ):
            iterable_list = list(input_)
            return flatten_list(iterable_list, dropna) if flatten else iterable_list
        else:
            return [input_]
    except Exception as e:
        raise ValueError(f"Could not convert {type(input_)} object to list: {e}") from e


@to_list.register(list)
def _(input_: List[Any], flatten: bool = True, dropna: bool = True) -> List[Any]:
    return flatten_list(input_, dropna) if flatten else input_


@to_list.register(tuple)
def _(input_, flatten=True, dropna=True):
    """Specialized implementation of `to_list` for handling tuple inputs."""
    return flatten_list(list(input_), dropna) if flatten else list(input_)


@to_list.register(set)
def _(input_, flatten=True, dropna=True):
    """Specialized implementation of `to_list` for handling set inputs."""
    return list(dropna_iterator(list(input_))) if dropna else list(input_)


# to_dict functions with datatype overloads
@singledispatch
def to_dict(input_: Any, *args, **kwargs) -> Dict[Any, Any]:
    """
    Converts the input object to a dictionary. This base function raises a ValueError for unsupported types.
    The function is overloaded to handle specific input types such as dict, str, pandas.Series, pandas.DataFrame,
    and Pydantic's BaseModel, utilizing the single dispatch mechanism for type-specific conversions.

    Args:
        input_ (Any): The input object to convert to a dictionary.
        *args: Variable length argument list for additional options in type-specific handlers.
        **kwargs: Arbitrary keyword arguments for additional options in type-specific handlers.

    Returns:
        Dict[Any, Any]: A dictionary representation of the input object.

    Raises:
        ValueError: If the input type is not supported or cannot be converted to a dictionary.

    Note:
        - For specific behaviors with dict, str, pandas.Series, pandas.DataFrame, and BaseModel,
          see the registered implementations.
    """
    raise ValueError(f"Input type not supported: {type(input_).__name__}")


@to_dict.register(dict)
def _(input_: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Handles dictionary inputs directly, returning the input without modification.

    Args:
        input_ (Dict[Any, Any]): The dictionary to be returned.

    Returns:
        Dict[Any, Any]: The input dictionary, unchanged.
    """
    return input_


@to_dict.register(str)
def _(input_: str, *args, **kwargs) -> Dict[Any, Any]:
    """
    Converts a JSON-formatted string to a dictionary.

    Args:
        input_ (str): The JSON string to convert.
        *args: Variable length argument list for json.loads().
        **kwargs: Arbitrary keyword arguments for json.loads().

    Returns:
        Dict[Any, Any]: The dictionary representation of the JSON string.

    Raises:
        ValueError: If the string cannot be decoded into a dictionary.
    """
    try:
        return json.loads(input_, *args, **kwargs)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not convert input_ to dict: {e}") from e


@to_dict.register(pd.Series)
def _(input_: pd.Series, *args, **kwargs) -> Dict[Any, Any]:
    """
    Converts a pandas Series to a dictionary.

    Args:
        input_ (pd.Series): The pandas Series to convert.
        *args: Variable length argument list for Series.to_dict().
        **kwargs: Arbitrary keyword arguments for Series.to_dict().

    Returns:
        Dict[Any, Any]: The dictionary representation of the pandas Series.
    """
    return input_.to_dict(*args, **kwargs)


@to_dict.register(pd.DataFrame)
def _(input_: pd.DataFrame, *args, orient: str = "list", as_list: bool = False,
      **kwargs) -> Dict[Any, Any] | List[Dict[Any, Any]]:
    """
    Converts a pandas DataFrame to a dictionary or a list of dictionaries, based on the `orient` and `as_list` parameters.

    Args:
        input_ (pd.DataFrame): The pandas DataFrame to convert.
        *args: Variable length argument list for DataFrame.to_dict() or DataFrame.iterrows().
        orient (str): The orientation of the data. Default is 'list'.
        as_list (bool): If True, returns a list of dictionaries, one for each row. Default is False.
        **kwargs: Arbitrary keyword arguments for DataFrame.to_dict().

    Returns:
        Dict[Any, Any] | List[Dict[Any, Any]]: Depending on `as_list`, either a dictionary representation
        of the DataFrame or a list of dictionaries, one for each row.
    """
    if as_list:
        return [row.to_dict(*args, orient=orient, **kwargs) for _, row in
                input_.iterrows()]
    return input_.to_dict(*args, orient=orient, **kwargs)


@to_dict.register(BaseModel)
def _(input_: BaseModel, *args, **kwargs) -> Dict[Any, Any]:
    """
    Converts a Pydantic BaseModel instance to a dictionary.

    Args:
        input_ (BaseModel): The Pydantic BaseModel instance to convert.
        *args: Variable length argument list for the model's dict() method.
        **kwargs: Arbitrary keyword arguments for the model's dict() method.

    Returns:
        Dict[Any, Any]: The dictionary representation of the BaseModel instance.
    """
    return input_.model_dump(*args, **kwargs)


# to_str functions with datatype overloads
@singledispatch
def to_str(input_: Any, *args, **kwargs) -> str:
    """
    Converts the input object to a string. This function utilizes single dispatch to handle
    specific input types such as dict, str, list, pandas.Series, and pandas.DataFrame,
    providing type-specific conversions to string format.

    Args:
        input_ (Any): The input object to convert to a string.
        *args: Variable length argument list for additional options in type-specific handlers.
        **kwargs: Arbitrary keyword arguments for additional options in type-specific handlers.

    Returns:
        str: A string representation of the input object.

    Note:
        - The base implementation simply uses the str() function for conversion.
        - For detailed behaviors with dict, str, list, pandas.Series, and pandas.DataFrame,
          refer to the registered implementations.
    """
    return str(input_)


@to_str.register(dict)
def _(input_: dict, *args, **kwargs) -> str:
    """
    Converts a dictionary to a JSON-formatted string.

    Args:
        input_ (dict): The dictionary to convert.
        *args: Variable length argument list for json.dumps().
        **kwargs: Arbitrary keyword arguments for json.dumps().

    Returns:
        str: The JSON string representation of the dictionary.
    """
    return json.dumps(input_, *args, **kwargs)


@to_str.register(str)
def _(input_: str, *args, **kwargs) -> str:
    """
    Returns the input string unchanged.

    Args:
        input_ (str): The input string.
        *args: Ignored.
        **kwargs: Ignored.

    Returns:
        str: The input string, unchanged.
    """
    return input_


@to_str.register(list)
def _(input_: list, *args, as_list: bool = False, **kwargs) -> str | List[str]:
    """
    Converts a list to a string. Optionally, the function can return a string representation
    of the list itself or join the string representations of its elements.

    Args:
        input_ (list): The list to convert.
        *args: Variable length argument list for additional options in element conversion.
        as_list (bool): If True, returns the string representation of the list. If False,
                        returns the elements joined by a comma. Default is False.
        **kwargs: Arbitrary keyword arguments for additional options in element conversion.

    Returns:
        str: Depending on `as_list`, either the string representation of the list or a string
             of the elements joined by a comma.
    """
    lst_ = [to_str(item, *args, **kwargs) for item in input_]
    return str(lst_) if as_list else ", ".join(lst_)


@to_str.register(pd.Series)
def _(input_: pd.Series, *args, **kwargs) -> str:
    """
    Converts a pandas Series to a JSON-formatted string.

    Args:
        input_ (pd.Series): The pandas Series to convert.
        *args: Variable length argument list for Series.to_json().
        **kwargs: Arbitrary keyword arguments for Series.to_json().

    Returns:
        str: The JSON string representation of the pandas Series.
    """
    return input_.to_json(*args, **kwargs)


@to_str.register(pd.DataFrame)
def _(input_: pd.DataFrame, *args, as_list: bool = False, **kwargs) -> str | List[str]:
    """
    Converts a pandas DataFrame to a JSON-formatted string. Optionally, can convert to a list of dictionaries
    first if `as_list` is True, then to a string representation of that list.

    Args:
        input_ (pd.DataFrame): The pandas DataFrame to convert.
        *args: Variable length argument list for additional options in conversion.
        as_list (bool): If True, converts the DataFrame to a list of dictionaries before converting
                        to a string. Default is False.
        **kwargs: Arbitrary keyword arguments for DataFrame.to_json() or to_dict().

    Returns:
        str: Depending on `as_list`, either a JSON string representation of the DataFrame or a string
             representation of a list of dictionaries derived from the DataFrame.
    """
    if as_list:
        return to_dict(input_, as_list=True, *args, **kwargs)
    return input_.to_json(*args, **kwargs)


# to_df functions with datatype overloads

@singledispatch
def to_df(
        input_: Any,
        how: str = "all",
        drop_kwargs: Dict[str, Any] | None = None,
        reset_index: bool = True,
        **kwargs: Any,
) -> pd.DataFrame:
    """
    Converts various input types to a pandas DataFrame, with options for handling missing data and resetting the index.
    This function is overloaded to handle specific data structures such as lists of dictionaries, lists of pandas objects (DataFrames or Series), and more.

    The base implementation attempts to directly convert the input to a DataFrame, applying dropna and reset_index as specified.

    Args:
        input_ (Any): The input data to convert into a DataFrame. Accepts a wide range of types thanks to overloads.
        how (str): Specifies how missing values are dropped. Passed directly to DataFrame.dropna().
        drop_kwargs (Dict[str, Any] | None): Additional keyword arguments for DataFrame.dropna().
        reset_index (bool): If True, the DataFrame index will be reset, removing the index labels.
        **kwargs: Additional keyword arguments passed to the pandas DataFrame constructor.

    Returns:
        pd.DataFrame: A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Note:
        - This function is overloaded to provide specialized behavior for different input types, enhancing its flexibility.
    """

    if drop_kwargs is None:
        drop_kwargs = {}

    try:
        dfs = pd.DataFrame(input_, **kwargs)
        dfs.dropna(**(drop_kwargs | {"how": how}), inplace=True)
        return dfs.reset_index(drop=True) if reset_index else dfs

    except Exception as e:
        raise ValueError(f"Error converting input_ to DataFrame: {e}") from e


@to_df.register(list[dict])
def _(
        input_,
        how: bool = "all",
        drop_kwargs: Dict | None = None,
        reset_index: bool = True,
        **kwargs
) -> pd.DataFrame:
    """
    Overloaded `to_df` implementation for converting a list of dictionaries into a pandas DataFrame.

    This method is specifically optimized for handling lists of dictionaries, allowing for efficient conversion
    to DataFrame, with additional control over handling missing data and indexing.

    Args:
        input_ (list[dict]): A list of dictionaries, each representing a row in the DataFrame.
        how, drop_kwargs, reset_index, **kwargs: See the base `to_df` function for descriptions.

    Returns:
        pd.DataFrame: A DataFrame constructed from the list of dictionaries.

    Note:
        - Inherits behavior from the base `to_df` function for dropping missing values and resetting the index.
    """

    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        dfs = pd.DataFrame(input_, **kwargs)
        dfs.dropna(**(drop_kwargs | {"how": how}), inplace=True)
        return dfs.reset_index(drop=True) if reset_index else dfs
    except Exception as e:
        raise ValueError(f"Error converting input_ to DataFrame: {e}") from e


@to_df.register(list[pd.DataFrame | pd.Series] | pd.core.generic.NDFrame)
def _(
        input_: list[pd.DataFrame | pd.Series] | pd.core.generic.NDFrame,
        how: str = "all",
        drop_kwargs: Dict | None = None,
        reset_index: bool = True,
        **kwargs
) -> pd.DataFrame:
    """
    Overloaded `to_df` implementation for converting lists of pandas DataFrames or Series, or a single NDFrame, into a single pandas DataFrame.

    For lists, this method concatenates the elements into a single DataFrame. For a single NDFrame, it applies the provided processing directly.

    Args:
        input_ (list[pd.DataFrame | pd.Series] | pd.core.generic.NDFrame): Input data to be converted.
        how, drop_kwargs, reset_index, **kwargs: See the base `to_df` function for descriptions.

    Returns:
        pd.DataFrame: A single DataFrame obtained by concatenating the input DataFrames or Series, or the processed NDFrame.

    Note:
        - This method leverages `pd.concat` for lists of DataFrames or Series and applies `dropna` and `reset_index` as per the base `to_df` logic.
    """

    dfs = ''
    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        dfs = pd.concat(input_, **kwargs)

    except Exception as e1:
        try:
            input_ = to_list(input_)
            dfs = input_[0]
            if len(input_) > 1:
                for i in input_[1:]:
                    dfs = pd.concat([dfs, i], **kwargs)

        except Exception as e2:
            raise ValueError(f"Error converting input_ to DataFrame: {e1}, {e2}")

    dfs.dropna(**(drop_kwargs | {"how": how}), inplace=True)
    return dfs.reset_index(drop=True) if reset_index else dfs


def to_num(
        input_: Any,
        upper_bound: int | float | None = None,
        lower_bound: int | float | None = None,
        num_type: Type[int | float] = int,
        precision: int | None = None,
) -> int | float:
    """
    Converts the input to a numeric value of specified type, with optional bounds and precision.

    Args:
        input_ (Any): The input value to convert. Can be of any type that `to_str` can handle.
        upper_bound (float | None): The upper bound for the numeric value. If specified, values above this bound will raise an error.
        lower_bound (float | None): The lower bound for the numeric value. If specified, values below this bound will raise an error.
        num_type (Type[int | float]): The numeric type to convert to. Can be `int` or `float`.
        precision (int | None): The number of decimal places for the result. Applies only to `float` type.

    Returns:
        int | float: The converted numeric value, adhering to specified type and precision.

    Raises:
        ValueError: If the input cannot be converted to a number, or if it violates the specified bounds.
    """
    str_ = to_str(input_)
    return ConvertUtil.str_to_num(str_, upper_bound, lower_bound, num_type, precision)


def to_readable_dict(input_: Any | List[Any]) -> str | List[str]:
    """
    Converts a given input to a readable dictionary format, either as a string or a list of dictionaries.

    Args:
        input_ (Any | List[Any]): The input to convert to a readable dictionary format.

    Returns:
        str | List[str]: The readable dictionary format of the input.
    """

    return ConvertUtil.to_readable_dict(input_)


class ConvertUtil:

    @staticmethod
    def is_same_dtype(input_: list | dict, dtype: Type | None = None) -> bool:
        """
        Checks if all elements in a list or dictionary values are of the same data type.

        Args:
            input_ (list | dict): The input list or dictionary to check.
            dtype (Type | None): The data type to check against. If None, uses the type of the first element.

        Returns:
            bool: True if all elements are of the same type (or if the input is empty), False otherwise.
        """
        if not input_:
            return True

        iterable = input_.values() if isinstance(input_, dict) else input_
        first_element_type = type(next(iter(iterable), None))

        dtype = dtype or first_element_type

        return all(isinstance(element, dtype) for element in iterable)

    @staticmethod
    def xml_to_dict(root) -> Dict[str, Any]:
        import xml.etree.ElementTree as ET
        from collections import defaultdict
        
        def parse_xml(element: ET.Element, parent: Dict[str, Any]):
            children = list(element)
            if children:
                d = defaultdict(list)
                for child in children:
                    parse_xml(child, d)
                parent[element.tag].append(d if len(d) > 1 else d[next(iter(d))])
            else:
                parent[element.tag].append(element.text)

        result = defaultdict(list)
        parse_xml(root, result)
        return {k: v[0] if len(v) == 1 else v for k, v in result.items()}

    @staticmethod
    def str_to_num(
            input_: str,
            upper_bound: float | None = None,
            lower_bound: float | None = None,
            num_type: Type[int | float] = int,
            precision: int | None = None,
    ) -> int | float:
        number_str = ConvertUtil._extract_first_number(input_)
        if number_str is None:
            raise ValueError(f"No numeric values found in the string: {input_}")

        number = ConvertUtil._convert_to_num(number_str, num_type, precision)

        if upper_bound is not None and number > upper_bound:
            raise ValueError(
                f"Number {number} is greater than the upper bound of {upper_bound}."
            )

        if lower_bound is not None and number < lower_bound:
            raise ValueError(
                f"Number {number} is less than the lower bound of {lower_bound}."
            )

        return number

    @staticmethod
    def strip_lower(input_: Any) -> str:
        """
        Converts the input to a lowercase string with leading and trailing whitespace removed.

        Args:
            input_ (Any): The input value to convert and process.

        Returns:
            str: The processed string.

        Raises:
            ValueError: If the input cannot be converted to a string.
        """
        try:
            return str(input_).strip().lower()
        except Exception as e:
            raise ValueError(
                f"Could not convert input_ to string: {input_}, Error: {e}"
            )

    @staticmethod
    def _extract_first_number(input_: str) -> str | None:
        match = number_regex.search(input_)
        return match.group(0) if match else None

    @staticmethod
    def _convert_to_num(
            number_str: str, num_type: Type[int | float] = int,
            precision: int | None = None
    ) -> int | float:
        if num_type is int:
            return int(float(number_str))
        elif num_type is float:
            number = float(number_str)
            return round(number, precision) if precision is not None else number
        else:
            raise ValueError(f"Invalid number type: {num_type}")

    @staticmethod
    def is_homogeneous(iterables: List[Any] | Dict[Any, Any], type_check: type) -> bool:
        if isinstance(iterables, list):
            return all(isinstance(it, type_check) for it in iterables)
        return isinstance(iterables, type_check)

    @staticmethod
    def to_readable_dict(input_: Dict[Any, Any] | List[Any]) -> str | List[Any]:
        try:
            dict_ = to_dict(input_)
            return json.dumps(dict_, indent=4) if isinstance(input_, dict) else input_
        except Exception as e:
            raise ValueError(f"Could not convert given input to readable dict: {e}") from e

def dropna_iterator(lst_: List[Any]) -> iter:
    return (item for item in lst_ if item is not None)


def flatten_list(lst_: List[Any], dropna: bool = True) -> List[Any]:
    """
    flatten a nested list, optionally removing None values.

    Args:
        lst_ (List[Any]): A nested list to flatten.
        dropna (bool): If True, None values are removed. default is True.

    Returns:
        List[Any]: A flattened list.

    examples:
        >>> flatten_list([[1, 2], [3, None]], dropna=True)
        [1, 2, 3]
        >>> flatten_list([[1, [2, None]], 3], dropna=False)
        [1, 2, None, 3]
    """
    flattened_list = list(_flatten_list_generator(lst_, dropna))
    return list(dropna_iterator(flattened_list)) if dropna else flattened_list


def _flatten_list_generator(
        lst_: List[Any], dropna: bool = True
) -> Generator[Any, None, None]:
    """
    Generator for flattening a nested list.

    Args:
        lst_ (List[Any]): A nested list to flatten.
        dropna (bool): If True, None values are omitted. Default is True.

    Yields:
        Generator[Any, None, None]: A generator yielding flattened elements.

    Examples:
        >>> list(_flatten_list_generator([[1, [2, None]], 3], dropna=False))
        [1, 2, None, 3]
    """
    for i in lst_:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        else:
            yield i
