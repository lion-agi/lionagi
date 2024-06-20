"""
Module for converting various input types into numeric values.

Provides functions to convert input data to numeric types (int, float,
or complex), with options for bounding values, specifying numeric type,
and controlling precision.

Functions:
    to_num: Convert an input to a numeric type (int, float, or complex).
    str_to_num: Convert a string to a numeric type (int, float, or complex).
    _extract_numbers: Extract all numeric values from a string.
    _convert_to_num: Convert a numeric string to a specified numeric type.
"""

import re
from typing import Type, Any, List, Union

# Comprehensive regex to capture decimal numbers, fractions, scientific
# notation, and complex numbers
NUMBER_REGEX = re.compile(
    r"[-+]?\d+\.\d+|"  # Decimal numbers with optional sign
    r"[-+]?\d+/\d+|"  # Fractions
    r"[-+]?\d+\.\d*[eE][-+]?\d+|"  # Scientific notation with decimal point
    r"[-+]?\d+[eE][-+]?\d+|"  # Scientific notation without decimal point
    r"[-+]?\d+\+\d+j|"  # Complex numbers with positive imaginary part
    r"[-+]?\d+-\d+j|"  # Complex numbers with negative imaginary part
    r"[-+]?\d+j|"  # Pure imaginary numbers
    r"[-+]?\d+"  # Integers with optional sign
)

# Mapping of string types to Python types
TYPE_MAP = {
    "int": int,
    "float": float,
    "complex": complex,
}


def to_num(
    input_: Any,
    /,
    *,
    upper_bound: Union[int, float, None] = None,
    lower_bound: Union[int, float, None] = None,
    num_type: Union[Type[Union[int, float, complex]], str] = "float",
    precision: Union[int, None] = None,
    num_count: int = 1,
) -> Union[int, float, complex, List[Union[int, float, complex]]]:
    """
    Convert an input to a numeric type (int, float, or complex).

    Args:
        input_: The input to convert to a number.
        upper_bound: The upper bound for the number. Raises ValueError if
            the number exceeds this bound. Defaults to None.
        lower_bound: The lower bound for the number. Raises ValueError if
            the number is below this bound. Defaults to None.
        num_type: The type of the number (int, float, or complex).
            Defaults to float.
        precision: The number of decimal places to round to if num_type
            is float. Defaults to None.
        num_count: The number of numeric values to return. Defaults to 1.

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
    if isinstance(input_, list):
        raise TypeError("Input cannot be a list.")

    str_ = str(input_)
    if str_.startswith(("0x", "0b")):
        raise ValueError("Hexadecimal and binary formats are not supported.")

    # Map string types to actual Python types
    if isinstance(num_type, str):
        if num_type not in TYPE_MAP:
            raise ValueError(f"Invalid number type string: {num_type}")
        num_type = TYPE_MAP[num_type]

    return str_to_num(
        str_, upper_bound, lower_bound, num_type, precision, num_count
    )


def str_to_num(
    input_: str,
    upper_bound: Union[float, None] = None,
    lower_bound: Union[float, None] = None,
    num_type: Type[Union[int, float, complex]] = float,
    precision: Union[int, None] = None,
    num_count: int = 1,
) -> Union[int, float, complex, List[Union[int, float, complex]]]:
    """
    Convert a string to a numeric type (int, float, or complex).

    Args:
        input_: The input string to convert to a number.
        upper_bound: The upper bound for the number. Raises ValueError if
            the number exceeds this bound. Defaults to None.
        lower_bound: The lower bound for the number. Raises ValueError if
            the number is below this bound. Defaults to None.
        num_type: The type of the number (int, float, or complex).
            Defaults to float.
        precision: The number of decimal places to round to if num_type
            is float. Defaults to None.
        num_count: The number of numeric values to return. Defaults to 1.

    Returns:
        The converted number or list of numbers.

    Raises:
        ValueError: If no numeric value is found in the input or if the
            number is out of the specified bounds.

    Examples:
        >>> str_to_num("42")
        42.0
        >>> str_to_num("3.14", num_type=float)
        3.14
        >>> str_to_num("2/3", num_type=float)
        0.6666666666666666
    """
    number_strs = _extract_numbers(input_)
    if not number_strs:
        raise ValueError(f"No numeric values found in the string: {input_}")

    numbers = [
        _convert_to_num(num_str, num_type, precision)
        for num_str in number_strs
    ]

    for number in numbers:
        if isinstance(number, (int, float, complex)):
            if upper_bound is not None and number > upper_bound:
                raise ValueError(
                    f"Number {number} is greater than the upper bound of "
                    f"{upper_bound}."
                )
            if lower_bound is not None and number < lower_bound:
                raise ValueError(
                    f"Number {number} is less than the lower bound of "
                    f"{lower_bound}."
                )

    return numbers[0] if num_count == 1 else numbers[:num_count]


def _extract_numbers(input_: str) -> List[str]:
    """
    Extract all numeric values from a string.

    Args:
        input_: The input string to search for numeric values.

    Returns:
        The list of numeric values found in the string.

    Examples:
        >>> _extract_numbers("42 and 3.14 and 2/3")
        ['42', '3.14', '2/3']
    """
    return NUMBER_REGEX.findall(input_)


def _convert_to_num(
    number_str: str,
    num_type: Type[Union[int, float, complex]] = float,
    precision: Union[int, None] = None,
) -> Union[int, float, complex]:
    """
    Convert a numeric string to a specified numeric type.

    Args:
        number_str: The numeric string to convert.
        num_type: The type to convert the string to (int, float, or
            complex). Defaults to float.
        precision: The number of decimal places to round to if num_type
            is float. Defaults to None.

    Returns:
        The converted number.

    Raises:
        ValueError: If the specified number type is invalid.

    Examples:
        >>> _convert_to_num('42', int)
        42
        >>> _convert_to_num('3.14', float)
        3.14
        >>> _convert_to_num('2/3', float)
        0.6666666666666666
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
    if num_type is float:
        return round(number, precision) if precision is not None else number
    if num_type is complex:
        return number
    raise ValueError(f"Invalid number type: {num_type}")


import unittest

class TestToNumFunctions(unittest.TestCase):

    def test_to_num_with_integer_string(self):
        self.assertEqual(to_num("123"), 123)

    def test_to_num_with_float_string(self):
        self.assertEqual(to_num("123.45"), 123.45)

    def test_to_num_with_mixed_string(self):
        self.assertEqual(to_num("The price is 123.45 dollars"), 123.45)

    def test_to_num_with_negative_number(self):
        self.assertEqual(to_num("-123.45"), -123.45)

    def test_to_num_with_no_number(self):
        with self.assertRaises(ValueError):
            to_num("No numbers here")

    def test_to_num_with_upper_bound(self):
        with self.assertRaises(ValueError):
            to_num("123.45", upper_bound=100)

    def test_to_num_with_lower_bound(self):
        with self.assertRaises(ValueError):
            to_num("123.45", lower_bound=200)

    def test_to_num_with_bounds(self):
        self.assertEqual(to_num("150", lower_bound=100, upper_bound=200), 150)

    def test_to_num_with_int_type(self):
        self.assertEqual(to_num("123.45", num_type=int), 123)

    def test_to_num_with_float_type(self):
        self.assertEqual(to_num("123", num_type=float), 123.0)

    def test_to_num_with_precision(self):
        self.assertEqual(to_num("123.4567", precision=2), 123.46)

    def test_str_to_num_with_valid_string(self):
        self.assertEqual(str_to_num("123"), 123)

    def test_str_to_num_with_invalid_string(self):
        with self.assertRaises(ValueError):
            str_to_num("No numbers here")

    def test_str_to_num_with_upper_bound(self):
        with self.assertRaises(ValueError):
            str_to_num("123.45", upper_bound=100)

    def test_str_to_num_with_lower_bound(self):
        with self.assertRaises(ValueError):
            str_to_num("123.45", lower_bound=200)

    def test_str_to_num_with_bounds(self):
        self.assertEqual(str_to_num("150", lower_bound=100, upper_bound=200), 150)

    def test_str_to_num_with_int_type(self):
        self.assertEqual(str_to_num("123.45", num_type=int), 123)

    def test_str_to_num_with_float_type(self):
        self.assertEqual(str_to_num("123", num_type=float), 123.0)

    def test_str_to_num_with_precision(self):
        self.assertEqual(str_to_num("123.4567", precision=2, num_type=float), 123.46)

    def test_extract_first_number_with_valid_string(self):
        self.assertEqual(_extract_numbers("The price is 123.45 dollars"), ["123.45"])

    def test_extract_first_number_with_no_number(self):
        self.assertEqual(_extract_numbers("No numbers here"), [])

    def test_convert_to_num_with_int_type(self):
        self.assertEqual(_convert_to_num("123.45", num_type=int), 123)

    def test_convert_to_num_with_float_type(self):
        self.assertEqual(_convert_to_num("123.45", num_type=float), 123.45)

    def test_convert_to_num_with_invalid_type(self):
        with self.assertRaises(ValueError):
            _convert_to_num("123.45", num_type=str)

    def test_convert_to_num_with_precision(self):
        self.assertEqual(
            _convert_to_num("123.4567", num_type=float, precision=2), 123.46
        )

    def test_to_num_with_multiple_numbers(self):
        self.assertEqual(to_num("There are 123 apples and 45 oranges"), 123)

    def test_to_num_with_multiple_numbers_and_num_count(self):
        self.assertEqual(
            to_num("There are 123 apples and 45 oranges", num_count=2), [123, 45]
        )

    def test_to_num_with_large_number(self):
        self.assertEqual(to_num("123456789012345"), 123456789012345)

    def test_to_num_with_small_number(self):
        self.assertEqual(to_num("0.000000123"), 0.000000123)

    def test_to_num_with_special_characters(self):
        self.assertEqual(to_num("Price: $123.45!"), 123.45)

    def test_to_num_with_hexadecimal(self):
        with self.assertRaises(ValueError):
            to_num("0x1A")

    def test_to_num_with_binary(self):
        with self.assertRaises(ValueError):
            to_num("0b1101")

    def test_to_num_with_list(self):
        with self.assertRaises(TypeError):
            to_num([1, 2, 3])

    def test_to_num_with_dict(self):
        with self.assertRaises(ValueError):
            to_num({"key": "value"})

    def test_to_num_with_mixed_string(self):
        self.assertEqual(to_num("Value is 123 and 456"), 123)

    def test_to_num_with_fraction(self):
        self.assertEqual(to_num("1/6"), 1 / 6)

    def test_to_num_with_fraction_and_num_count(self):
        self.assertEqual(to_num("1/6 and 2/3", num_count=2), [1 / 6, 2 / 3])

    def test_to_num_with_upper_and_lower_bounds(self):
        with self.assertRaises(ValueError):
            to_num("150", lower_bound=100, upper_bound=140)

    def test_to_num_with_complex_number(self):
        self.assertEqual(to_num("1+2j", num_type=complex), 1 + 2j)

    def test_to_num_with_multiple_complex_numbers(self):
        self.assertEqual(
            to_num("1+2j and 3-4j", num_type=complex, num_count=2), [1 + 2j, 3 - 4j]
        )


if __name__ == "__main__":
    unittest.main()