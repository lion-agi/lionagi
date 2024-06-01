import re
from typing import Type, Any, List

# Comprehensive regex to capture decimal numbers, fractions, scientific notation, and complex numbers
number_regex = re.compile(
    r"[-+]?\d+\.\d+|"  # Decimal numbers with optional sign
    r"[-+]?\d+/\d+|"  # Fractions
    r"[-+]?\d+\.\d*[eE][-+]?\d+|"  # Scientific notation with decimal point
    r"[-+]?\d+[eE][-+]?\d+|"  # Scientific notation without decimal point
    r"[-+]?\d+\+\d+j|"  # Complex numbers with positive imaginary part
    r"[-+]?\d+-\d+j|"  # Complex numbers with negative imaginary part
    r"[-+]?\d+j|"  # Pure imaginary numbers
    r"[-+]?\d+"  # Integers with optional sign
)


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: int | float | None = None,
    lower_bound: int | float | None = None,
    num_type: Type[int | float | complex] = float,
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | List[int | float | complex]:
    """
    Convert an input to a numeric type (int, float, or complex).

    Args:
        input_ (Any): The input to convert to a number.
        upper_bound (int | float | None, optional): The upper bound for the
            number. Raises ValueError if the number exceeds this bound.
            Defaults to None.
        lower_bound (int | float | None, optional): The lower bound for the
            number. Raises ValueError if the number is below this bound.
            Defaults to None.
        num_type (Type[int | float | complex], optional): The type of the number
            (int, float, or complex). Defaults to float.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.
        num_count (int, optional): The number of numeric values to return. Defaults to 1.

    Returns:
        int | float | complex | List[int | float | complex]: The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
    """
    if isinstance(input_, list):
        raise TypeError("Input cannot be a list.")

    str_ = str(input_)
    if str_.startswith(("0x", "0b")):
        raise ValueError("Hexadecimal and binary formats are not supported.")

    return str_to_num(str_, upper_bound, lower_bound, num_type, precision, num_count)


def str_to_num(
    input_: str,
    upper_bound: float | None = None,
    lower_bound: float | None = None,
    num_type: Type[int | float | complex] = float,
    precision: int | None = None,
    num_count: int = 1,
) -> int | float | complex | List[int | float | complex]:
    """
    Convert a string to a numeric type (int, float, or complex).

    Args:
        input_ (str): The input string to convert to a number.
        upper_bound (float | None, optional): The upper bound for the number.
            Raises ValueError if the number exceeds this bound. Defaults to
            None.
        lower_bound (float | None, optional): The lower bound for the number.
            Raises ValueError if the number is below this bound. Defaults to
            None.
        num_type (Type[int | float | complex], optional): The type of the number
            (int, float, or complex). Defaults to float.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.
        num_count (int, optional): The number of numeric values to return. Defaults to 1.

    Returns:
        int | float | complex | List[int | float | complex]: The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.
    """
    number_strs = _extract_numbers(input_)
    if not number_strs:
        raise ValueError(f"No numeric values found in the string: {input_}")

    numbers = [_convert_to_num(num_str, num_type, precision) for num_str in number_strs]

    for number in numbers:
        if isinstance(number, (int, float)):
            if upper_bound is not None and number > upper_bound:
                raise ValueError(
                    f"Number {number} is greater than the upper bound of {upper_bound}."
                )
            if lower_bound is not None and number < lower_bound:
                raise ValueError(
                    f"Number {number} is less than the lower bound of {lower_bound}."
                )

    return numbers[0] if num_count == 1 else numbers[:num_count]


def _extract_numbers(input_: str) -> List[str]:
    """
    Extract all numeric values from a string.

    Args:
        input_ (str): The input string to search for numeric values.

    Returns:
        List[str]: The list of numeric values found in the string.
    """
    return number_regex.findall(input_)


def _convert_to_num(
    number_str: str,
    num_type: Type[int | float | complex] = float,
    precision: int | None = None,
) -> int | float | complex:
    """
    Convert a numeric string to a specified numeric type.

    Args:
        number_str (str): The numeric string to convert.
        num_type (Type[int | float | complex], optional): The type to convert the
            string to (int, float, or complex). Defaults to float.
        precision (int | None, optional): The number of decimal places to
            round to if num_type is float. Defaults to None.

    Returns:
        int | float | complex: The converted number.

    Raises:
        ValueError: If the specified number type is invalid.
    """
    if "/" in number_str:
        numerator, denominator = map(float, number_str.split("/"))
        number = numerator / denominator
    elif "j" in number_str:
        number = complex(number_str)
    else:
        number = float(number_str)

    if num_type is int:
        return int(number)
    elif num_type is float:
        return round(number, precision) if precision is not None else number
    elif num_type is complex:
        return number
    else:
        raise ValueError(f"Invalid number type: {num_type}")
