import re
from typing import Type, Any
from ._to_str import to_str

number_regex = re.compile(r"-?\d+\.?\d*")


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: Type[int | float] = float,
    precision: int | None = None,
) -> int | float:
    """
    Convert an input to a numeric type (int or float).

    Args:
        input_ (Any): The input to convert to a number.
        upper_bound (int | float | None, optional): The upper bound for the
            number. Raises ValueError if the number exceeds this bound.
            Defaults to None.
        lower_bound (int | float | None, optional): The lower bound for the
            number. Raises ValueError if the number is below this bound.
            Defaults to None.
        num_type (Type[int | float], optional): The type of the number
            (int or float). Defaults to float.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.

    Returns:
        int | float: The converted number.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
    """
    str_ = to_str(input_)
    return str_to_num(str_, upper_bound, lower_bound, num_type, precision)


def str_to_num(
    input_: str,
    upper_bound: float | None = None,
    lower_bound: float | None = None,
    num_type: Type[int | float] = int,
    precision: int | None = None,
) -> int | float:
    """
    Convert a string to a numeric type (int or float).

    Args:
        input_ (str): The input string to convert to a number.
        upper_bound (float | None, optional): The upper bound for the number.
            Raises ValueError if the number exceeds this bound. Defaults to
            None.
        lower_bound (float | None, optional): The lower bound for the number.
            Raises ValueError if the number is below this bound. Defaults to
            None.
        num_type (Type[int | float], optional): The type of the number
            (int or float). Defaults to int.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.

    Returns:
        int | float: The converted number.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
    """
    number_str = _extract_first_number(input_)
    if number_str is None:
        raise ValueError(f"No numeric values found in the string: {input_}")

    number = _convert_to_num(number_str, num_type, precision)

    if upper_bound is not None and number > upper_bound:
        raise ValueError(
            f"Number {number} is greater than the upper bound of " f"{upper_bound}."
        )

    if lower_bound is not None and number < lower_bound:
        raise ValueError(
            f"Number {number} is less than the lower bound of {lower_bound}."
        )

    return number


def _extract_first_number(input_: str) -> str | None:
    """
    Extract the first numeric value from a string.

    Args:
        input_ (str): The input string to search for a numeric value.

    Returns:
        str | None: The first numeric value found in the string, or None if
            no numeric value is found.
    """
    match = number_regex.search(input_)
    return match.group(0) if match else None


def _convert_to_num(
    number_str: str, num_type: Type[int | float] = int, precision: int | None = None
) -> int | float:
    """
    Convert a numeric string to a specified numeric type.

    Args:
        number_str (str): The numeric string to convert.
        num_type (Type[int | float], optional): The type to convert the
            string to (int or float). Defaults to int.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.

    Returns:
        int | float: The converted number.

    Raises:
        ValueError: If the specified number type is invalid.
    """
    if num_type is int:
        return int(float(number_str))
    elif num_type is float:
        number = float(number_str)
        return round(number, precision) if precision is not None else number
    else:
        raise ValueError(f"Invalid number type: {num_type}")
