"""Tests for readable JSON conversion utilities."""

import json

import pytest

from lionagi.libs.parse.json.as_readable import as_readable_json


# Updated test for list handling
def test_as_readable_json_list():
    """Test list conversion."""
    data = [{"a": 1}, {"b": 2}]
    result = as_readable_json(data)

    # Each item should be on a new line with blank line between
    items = result.strip().split("\n\n")
    assert len(items) == len(data)

    # Each item should be valid JSON matching original
    for item_str, expected in zip(items, data):
        parsed = json.loads(item_str)
        assert parsed == expected


# Updated empty input test
def test_as_readable_json_empty():
    """Test empty input handling."""
    # Empty dict returns empty object
    assert as_readable_json({}) == "{}"
    # Empty list returns empty string
    assert as_readable_json([]) == ""
    # None returns empty object
    assert as_readable_json(None) == "{}"


# Updated Unicode handling test
def test_as_readable_json_kwargs():
    """Test handling of additional kwargs."""
    data = {"name": "测试"}  # Chinese characters

    # Test ASCII encoding
    result = as_readable_json(data, ensure_ascii=True)
    assert "\\u" in result  # Should contain Unicode escapes

    # Test native character output
    result = as_readable_json(data, ensure_ascii=False)
    assert "测试" in result  # Should contain actual characters


# Additional test for custom kwarg handling
def test_as_readable_json_custom_kwargs():
    """Test passing custom kwargs to JSON encoder."""
    data = {"name": "test"}

    # Test custom indentation
    result = as_readable_json(data, indent=2)
    assert "  " in result  # Should use 2-space indent


if __name__ == "__main__":
    pytest.main([__file__])
