import json
from typing import Any, Type, Callable, Literal, TypeVar
from typing_extensions import deprecated

from lion_core import CoreLib
import pandas as pd

T = TypeVar("T")


def to_list(
    input_: Any, /, *, flatten: bool = False, dropna: bool = False
) -> list[Any]:
    """
    Convert various input types to a list.

    This function handles different input types and converts them to a list,
    with options for flattening nested structures and removing None values.

    Accepted input types and their behaviors:
    1. None or LionUndefined: Returns an empty list [].
    2. str, bytes, bytearray: Returns a single-item list containing the input.
    3. Mapping (dict, OrderedDict, etc.): Returns a single-item list containing the input.
    4. BaseModel: Returns a single-item list containing the input.
    5. Sequence (list, tuple, etc.):
       - If flatten=False, returns the sequence as a flat list.
       - If flatten=True, flattens nested sequences.
    6. Other Iterables: Converts to a list, then applies flattening if specified.
    7. Any other type: Returns a single-item list containing the input.

    Args:
        input_: The input to be converted to a list.
        flatten: If True, flattens nested list structures.
        dropna: If True, removes None values from the result.

    Returns:
        A list derived from the input, processed according to the specified options.

    Examples:
        >>> to_list(1)
        [1]
        >>> to_list([1, [2, 3]], flatten=True)
        [1, 2, 3]
        >>> to_list([1, None, 2], dropna=True)
        [1, 2]
    """
    return CoreLib.to_list(input_, flatten=flatten, dropna=dropna)


def to_dict(
    input_: Any,
    /,
    *,
    use_model_dump: bool = False,
    str_type: Literal["json", "xml"] | None = None,
    parser: Callable[[str], dict[str, Any]] | None = None,
    **kwargs: Any,
) -> T:
    """
    Convert various input types to a dictionary or list of dictionaries.

    Accepted input types and their behaviors:
    1. None or LionUndefined: Returns an empty dictionary {}.
    2. Mapping (dict, OrderedDict, etc.): Returns a dict representation.
    3. Sequence (list, tuple, etc.):
       - Returns a list of converted items.
       - If the sequence contains only one dict, returns that dict.
    4. set: Converts to a list.
    5. str:
       - If empty, returns {}.
       - If str_type is "json", attempts to parse as JSON.
       - If str_type is "xml", attempts to parse as XML.
       - For invalid JSON, returns the original string.
    6. Objects with .model_dump() method (if use_model_dump is True):
       Calls .model_dump() and returns the result.
    7. Objects with .to_dict(), .dict(), or .json() methods:
       Calls the respective method and returns the result.
    8. Objects with .__dict__ attribute: Returns the .__dict__.
    9. Any other object that can be converted to a dict.

    Args:
        input_: The input to be converted.
        use_model_dump: If True, use model_dump method when available.
        str_type: The type of string to parse ("json" or "xml").
        parser: A custom parser function for string inputs.
        **kwargs: Additional keyword arguments for conversion methods.

    Returns:
        A dictionary, list of dictionaries, or list, depending on the input.

    Raises:
        ValueError: If the input cannot be converted to a dictionary.
    """
    return CoreLib.to_dict(
        input_,
        use_model_dump=use_model_dump,
        str_type=str_type,
        parser=parser,
        **kwargs,
    )


def to_str(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
    strip_lower: bool = False,
    chars: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Convert the input to a string representation.

    This function uses singledispatch to provide type-specific
    implementations for different input types. The base implementation
    handles Any type by converting it to a string using the str() function.

    Args:
        input_: The input to be converted to a string.
        use_model_dump: If True, use model_dump for Pydantic models.
        strip_lower: If True, strip and convert to lowercase.
        chars: Characters to strip from the result.
        **kwargs: Additional arguments for json.dumps.

    Returns:
        String representation of the input.

    Raises:
        ValueError: If conversion fails.

    Examples:
        >>> to_str(123)
        '123'
        >>> to_str("  HELLO  ", strip_lower=True)
        'hello'
        >>> to_str({"a": 1, "b": 2})
        '{"a": 1, "b": 2}'
    """
    return CoreLib.to_str(
        input_,
        use_model_dump=use_model_dump,
        strip_lower=strip_lower,
        chars=chars,
        **kwargs,
    )


def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Converts various input types to a pandas DataFrame, with options for
    handling missing data and resetting the index. This function is
    overloaded to handle specific data structures such as lists of
    dictionaries, lists of pandas objects (DataFrames or Series), and more.

    The base implementation attempts to directly convert the input to a
    DataFrame, applying dropna and reset_index as specified.

    Args:
        input_ (Any): The input data to convert into a DataFrame. Accepts a
            wide range of types thanks to overloads.
        drop_how (str): Specifies how missing values are dropped. Passed
            directly to DataFrame.dropna().
        drop_kwargs (Dict[str, Any] | None): Additional keyword arguments for
            DataFrame.dropna().
        reset_index (bool): If True, the DataFrame index will be reset,
            removing the index labels.
        **kwargs: Additional keyword arguments passed to the pandas DataFrame
            constructor.

    Returns:
        pd.DataFrame: A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Note:
        - This function is overloaded to provide specialized behavior for
          different input types, enhancing its flexibility.
    """

    from lionagi.app.Pandas.convert import to_df

    return to_df(
        input_,
        drop_how=drop_how,
        drop_kwargs=drop_kwargs,
        reset_index=reset_index,
        **kwargs,
    )


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: type[int | float | complex] | str = "float",
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | list[int | float | complex]:
    """
    Convert an input to a numeric type (int, float, or complex).

    Args:
        input_: The input to convert to a number.
        upper_bound: The upper bound for the number. Raises ValueError if
            the number exceeds this bound.
        lower_bound: The lower bound for the number. Raises ValueError if
            the number is below this bound.
        num_type: The type of the number (int, float, or complex).
        precision: The number of decimal places to round to if num_type is float.
        num_count: The number of numeric values to return.

    Returns:
        The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
        TypeError: If the input is a list.

    Examples:
        >>> to_num("42")
        42.0
        >>> to_num("3.14", num_type=float)
        3.14
        >>> to_num("2/3", num_type=float)
        0.6666666666666666
    """
    return CoreLib.to_num(
        input_,
        upper_bound=upper_bound,
        lower_bound=lower_bound,
        num_type=num_type,
        precision=precision,
        num_count=num_count,
    )


def as_readable_json(input_: Any, /, **kwargs) -> str:
    """
    Convert the input to a readable JSON string.

    This function attempts to convert the input to a dictionary and then
    to a formatted JSON string. If conversion to a dictionary fails, it
    returns the string representation of the input.

    Args:
        input_: The input to be converted to a readable JSON string.
        kwargs for to_dict

    Returns:
        A formatted JSON string if the input can be converted to a
        dictionary, otherwise the string representation of the input.

    Raises:
        ValueError: If the input cannot be converted to a readable dict.
    """
    return CoreLib.as_readable_json(input_, **kwargs)


@deprecated  # use as_readable_json instead, will be removed in v1.0.0
def to_readable_dict(input_: Any) -> str:
    """
    Converts a given input to a readable dictionary format
    """

    try:
        dict_ = to_dict(input_)
        return json.dumps(dict_, indent=4) if isinstance(input_, dict) else input_
    except Exception as e:
        raise ValueError(f"Could not convert given input to readable dict: {e}") from e


def is_same_dtype(
    input_: list | dict, dtype: Type | None = None, return_dtype: bool = False
) -> bool | tuple[bool, Type]:
    """Check if all elements in input have the same data type."""
    return CoreLib.is_same_dtype(input_, dtype=dtype, return_dtype=return_dtype)


# renamed parameter root to xml_string
def xml_to_dict(xml_string: str) -> dict[str, Any]:
    """
    Parse an XML string into a nested dictionary structure.

    This function converts an XML string into a dictionary where:
    - Element tags become dictionary keys
    - Text content is assigned directly to the tag key if there are no children
    - Attributes are stored in a '@attributes' key
    - Multiple child elements with the same tag are stored as lists

    Args:
        xml_string: The XML string to parse.

    Returns:
        A dictionary representation of the XML structure.

    Raises:
        ValueError: If the XML is malformed or parsing fails.
    """
    return CoreLib.xml_to_dict(xml_string)


def strip_lower(
    input_: Any,
    /,
    *,
    use_model_dump: bool = True,
    chars: str | None = None,
    **kwargs: Any,
) -> str:
    """
    Convert input to stripped and lowercase string representation.

    This function is a convenience wrapper around to_str that always
    applies stripping and lowercasing.

    Args:
        input_: The input to convert to a string.
        use_model_dump: If True, use model_dump for Pydantic models.
        chars: Characters to strip from the result.
        **kwargs: Additional arguments to pass to to_str.

    Returns:
        Stripped and lowercase string representation of the input.

    Raises:
        ValueError: If conversion fails.

    Example:
        >>> strip_lower("  HELLO WORLD  ")
        'hello world'
    """
    return CoreLib.strip_lower(
        input_, use_model_dump=use_model_dump, chars=chars, **kwargs
    )


def is_structure_homogeneous(
    structure: Any, return_structure_type: bool = False
) -> bool | tuple[bool, type | None]:
    """
    Check if a nested structure is homogeneous (no mix of lists and dicts).

    Args:
        structure: The nested structure to check.
        return_structure_type: If True, return the type of the homogeneous
            structure.

    Returns:
        If return_structure_type is False, returns True if the structure is
        homogeneous, False otherwise.
        If True, returns a tuple (bool, type | None).

    Examples:
        >>> is_structure_homogeneous({'a': {'b': 1}, 'c': {'d': 2}})
        True
        >>> is_structure_homogeneous({'a': {'b': 1}, 'c': [1, 2]})
        False
    """

    return CoreLib.is_structure_homogeneous(
        structure, return_structure_type=return_structure_type
    )


def is_homogeneous(iterables: list[Any] | dict[Any, Any], type_check: type) -> bool:
    """
    Check if all elements in a list or all values in a dict are of same type.

    Args:
        iterables: The list or dictionary to check.
        type_check: The type to check against.

    Returns:
        True if all elements/values are of the same type, False otherwise.
    """
    return CoreLib.is_homogeneous(iterables, type_check)


def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Converts various input types to a pandas DataFrame, with options for
    handling missing data and resetting the index. This function is
    overloaded to handle specific data structures such as lists of
    dictionaries, lists of pandas objects (DataFrames or Series), and more.

    The base implementation attempts to directly convert the input to a
    DataFrame, applying dropna and reset_index as specified.

    Args:
        input_ (Any): The input data to convert into a DataFrame. Accepts a
            wide range of types thanks to overloads.
        drop_how (str): Specifies how missing values are dropped. Passed
            directly to DataFrame.dropna().
        drop_kwargs (Dict[str, Any] | None): Additional keyword arguments for
            DataFrame.dropna().
        reset_index (bool): If True, the DataFrame index will be reset,
            removing the index labels.
        **kwargs: Additional keyword arguments passed to the pandas DataFrame
            constructor.

    Returns:
        pd.DataFrame: A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Note:
        - This function is overloaded to provide specialized behavior for
        different input types, enhancing its flexibility.
    """
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.to_df(
        input_,
        drop_how=drop_how,
        drop_kwargs=drop_kwargs,
        reset_index=reset_index,
        **kwargs,
    )
