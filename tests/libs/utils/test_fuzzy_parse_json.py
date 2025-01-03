"""Tests for JSON parsing utilities."""

import pytest

from lionagi.utils import fix_json_string, fuzzy_parse_json


def test_fuzzy_parse_json_basic():
    """Test basic JSON parsing functionality."""
    # Valid JSON
    assert fuzzy_parse_json('{"key": "value"}') == {"key": "value"}
    assert fuzzy_parse_json('{"num": 42}') == {"num": 42}
    assert fuzzy_parse_json('{"bool": true}') == {"bool": True}

    # Nested structures
    nested = '{"outer": {"inner": "value"}}'
    assert fuzzy_parse_json(nested) == {"outer": {"inner": "value"}}


def test_fuzzy_parse_json_fixes():
    """Test automatic fixing of common JSON issues."""
    # Single quotes
    assert fuzzy_parse_json("{'key': 'value'}") == {"key": "value"}

    # Unquoted keys
    assert fuzzy_parse_json("{key: 'value'}") == {"key": "value"}

    # Mixed quotes
    assert fuzzy_parse_json("{\"key\": 'value'}") == {"key": "value"}

    # Missing closing brackets
    assert fuzzy_parse_json('{"key": "value"') == {"key": "value"}


def test_fuzzy_parse_json_whitespace():
    """Test handling of various whitespace patterns."""
    # Extra whitespace
    assert fuzzy_parse_json('  {  "key"  :  "value"  }  ') == {"key": "value"}

    # Newlines
    assert fuzzy_parse_json('{\n"key":\n"value"\n}') == {"key": "value"}

    # Tabs
    assert fuzzy_parse_json('{\t"key":\t"value"\t}') == {"key": "value"}


def test_fuzzy_parse_json_errors():
    """Test error handling for invalid inputs."""
    # Non-string input
    with pytest.raises(TypeError, match="Input must be a string"):
        fuzzy_parse_json(123)

    # Empty string
    with pytest.raises(ValueError, match="Input string is empty"):
        fuzzy_parse_json("")

    # Invalid JSON
    with pytest.raises(ValueError, match="Invalid JSON string"):
        fuzzy_parse_json("{invalid json}")


def test_fix_json_string_basic():
    """Test basic bracket fixing functionality."""
    # Add missing closing bracket
    assert fix_json_string('{"key": "value"') == '{"key": "value"}'

    # Add multiple missing brackets
    assert (
        fix_json_string('{"outer": {"inner": "value"')
        == '{"outer": {"inner": "value"}}'
    )


def test_fix_json_string_errors():
    """Test error handling in bracket fixing."""
    # Empty string
    with pytest.raises(ValueError, match="Input string is empty"):
        fix_json_string("")

    # Extra closing bracket
    with pytest.raises(ValueError, match="Extra closing bracket"):
        fix_json_string('{"key": "value"}}')

    # Mismatched brackets
    with pytest.raises(ValueError, match="Mismatched bracket"):
        fix_json_string('{"key": "value"]')


def test_fix_json_string_nested():
    """Test fixing nested structures."""
    # Multiple nested objects
    nested = '{"a": {"b": {"c": "value"'
    expected = '{"a": {"b": {"c": "value"}}}'
    assert fix_json_string(nested) == expected

    # Mixed brackets
    mixed = '{"array": ["item1", {"key": "value"'
    expected = '{"array": ["item1", {"key": "value"}]}'
    assert fix_json_string(mixed) == expected


def test_fix_json_string_escaped():
    """Test handling of escaped characters."""
    # Escaped quotes
    assert (
        fix_json_string('{"key": "value \\"quote\\"')
        == '{"key": "value \\"quote\\"}'
    )

    # Escaped brackets
    assert (
        fix_json_string('{"key": "\\{not a bracket"')
        == '{"key": "\\{not a bracket"}'
    )


def test_fuzzy_parse_json_complex():
    """Test parsing of complex JSON structures."""
    # Mixed types
    complex_json = """{
        "string": "value",
        "number": 42,
        "float": 3.14,
        "boolean": true,
        "null": null,
        "array": [1, 2, 3],
        "object": {"nested": "value"}
    }"""
    expected = {
        "string": "value",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "array": [1, 2, 3],
        "object": {"nested": "value"},
    }
    assert fuzzy_parse_json(complex_json) == expected


def test_fuzzy_parse_json_edge_cases():
    """Test handling of edge cases."""
    # Empty object
    assert fuzzy_parse_json("{}") == {}

    # Single character values
    assert fuzzy_parse_json('{"k":"v"}') == {"k": "v"}

    # Unicode characters
    assert fuzzy_parse_json('{"key":"值"}') == {"key": "值"}
