import pytest

from lionagi.libs.parse.validate_boolean import (
    FALSE_VALUES,
    TRUE_VALUES,
    validate_boolean,
)


def test_boolean_input():
    # Test direct boolean inputs
    assert validate_boolean(True) is True
    assert validate_boolean(False) is False


def test_numeric_input():
    # Test integer inputs
    assert validate_boolean(1) is True
    assert validate_boolean(0) is False
    assert validate_boolean(-1) is True
    assert validate_boolean(42) is True

    # Test float inputs
    assert validate_boolean(1.0) is True
    assert validate_boolean(0.0) is False
    assert validate_boolean(-1.5) is True
    assert validate_boolean(float("inf")) is True


def test_string_true_values():
    # Test all predefined true values
    for value in TRUE_VALUES:
        assert validate_boolean(value) is True
        # Test case insensitivity
        assert validate_boolean(value.upper()) is True
        assert validate_boolean(value.title()) is True
        # Test with whitespace
        assert validate_boolean(f"  {value}  ") is True


def test_string_false_values():
    # Test all predefined false values
    for value in FALSE_VALUES:
        assert validate_boolean(value) is False
        # Test case insensitivity
        assert validate_boolean(value.upper()) is False
        assert validate_boolean(value.title()) is False
        # Test with whitespace
        assert validate_boolean(f"  {value}  ") is False


def test_numeric_strings():
    # Test numeric strings
    assert validate_boolean("1") is True
    assert validate_boolean("0") is False


def test_error_cases():
    # Test None input
    with pytest.raises(TypeError, match="Cannot convert None to boolean"):
        validate_boolean(None)

    # Test empty string
    with pytest.raises(
        ValueError, match="Cannot convert empty string to boolean"
    ):
        validate_boolean("")
    with pytest.raises(
        ValueError, match="Cannot convert empty string to boolean"
    ):
        validate_boolean("   ")

    # Test invalid string values
    with pytest.raises(ValueError, match="Cannot convert .* to boolean"):
        validate_boolean("invalid")
    with pytest.raises(ValueError, match="Cannot convert .* to boolean"):
        validate_boolean("maybe")

    # Test unconvertible objects
    class Unconvertible:
        def __str__(self):
            raise Exception("Cannot convert to string")

    with pytest.raises(TypeError, match="Cannot convert .* to boolean"):
        validate_boolean(Unconvertible())


def test_object_conversion():
    # Test objects that can be converted to string
    class StringTrue:
        def __str__(self):
            return "true"

    class StringFalse:
        def __str__(self):
            return "false"

    class StringNumber:
        def __str__(self):
            return "1"

    assert validate_boolean(StringTrue()) is True
    assert validate_boolean(StringFalse()) is False
    assert validate_boolean(StringNumber()) is True


def test_edge_cases():

    # Mixed case and extra whitespace
    assert validate_boolean("  TrUe  ") is True
    assert validate_boolean("  FaLsE  ") is False

    # Unicode whitespace
    assert validate_boolean("\u2003true\u2003") is True
    assert validate_boolean("\u2003false\u2003") is False


def test_constant_sets():
    # Ensure no overlap between TRUE_VALUES and FALSE_VALUES
    assert not (
        TRUE_VALUES & FALSE_VALUES
    ), "TRUE_VALUES and FALSE_VALUES should not overlap"

    # Test that all values in TRUE_VALUES return True
    for value in TRUE_VALUES:
        assert validate_boolean(value) is True

    # Test that all values in FALSE_VALUES return False
    for value in FALSE_VALUES:
        assert validate_boolean(value) is False


def test_whitespace_handling():
    # Test various types of whitespace
    assert validate_boolean("  true  ") is True
    assert validate_boolean("\ttrue\t") is True
    assert validate_boolean("\ntrue\n") is True
    assert validate_boolean("\rtrue\r") is True
    assert validate_boolean(" \t\n\rtrue\r\n\t ") is True


def test_invalid_numeric_strings():
    # Test invalid numeric strings
    with pytest.raises(ValueError):
        validate_boolean("1.2.3")
    with pytest.raises(ValueError):
        validate_boolean("1e")
    with pytest.raises(ValueError):
        validate_boolean("e1")
    with pytest.raises(ValueError):
        validate_boolean("1+2+3j")
