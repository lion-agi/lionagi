import pytest

from lionagi.libs.parse.to_json import to_json


def test_to_json_direct_parsing():
    # Test direct JSON string
    json_str = '{"key": "value"}'
    result = to_json(json_str)
    assert result == {"key": "value"}


def test_to_json_list_input():
    # Test list of strings
    json_list = ['{"key":', '"value"}']
    result = to_json(json_list)
    assert result == {"key": "value"}


def test_to_json_markdown_single():
    # Test single JSON block in markdown
    markdown = """
    Some text
    ```json
    {"key": "value"}
    ```
    More text
    """
    result = to_json(markdown)
    assert result == {"key": "value"}


def test_to_json_markdown_multiple():
    # Test multiple JSON blocks in markdown
    markdown = """
    First block:
    ```json
    {"key1": "value1"}
    ```
    Second block:
    ```json
    {"key2": "value2"}
    ```
    """
    result = to_json(markdown)
    assert result == [{"key1": "value1"}, {"key2": "value2"}]


def test_to_json_fuzzy_parse():
    # Test fuzzy parsing of malformed JSON
    json_str = "{key: 'value'}"
    result = to_json(json_str, fuzzy_parse=True)
    assert result == {"key": "value"}


def test_to_json_fuzzy_parse_markdown():
    # Test fuzzy parsing in markdown blocks
    markdown = """
    ```json
    {key: 'value1'}
    ```
    ```json
    {key: 'value2'}
    ```
    """
    result = to_json(markdown, fuzzy_parse=True)
    assert result == [{"key": "value1"}, {"key": "value2"}]


def test_to_json_invalid_input():
    # Test invalid JSON without fuzzy parsing
    invalid_json = "{invalid: json}"
    result = to_json(invalid_json)
    assert result == []


def test_to_json_empty_input():
    # Test empty string
    assert to_json("") == []
    # Test empty list
    assert to_json([]) == []


def test_to_json_no_code_blocks():
    # Test markdown without JSON code blocks
    markdown = """
    Some text
    ```python
    print("Hello")
    ```
    """
    result = to_json(markdown)
    assert result == []


def test_to_json_nested_structures():
    # Test nested JSON structures
    json_str = """
    ```json
    {
        "key": {
            "nested": [1, 2, 3],
            "object": {"a": "b"}
        }
    }
    ```
    """
    result = to_json(json_str)
    assert result == {"key": {"nested": [1, 2, 3], "object": {"a": "b"}}}


def test_to_json_mixed_content():
    # Test markdown with both valid and invalid JSON blocks
    markdown = """
    Valid block:
    ```json
    {"valid": true}
    ```
    Invalid block:
    ```json
    {invalid: json}
    ```
    """
    with pytest.raises(Exception):
        to_json(markdown)


def test_to_json_whitespace_handling():
    # Test handling of various whitespace in JSON blocks
    markdown = """
    ```json
    {
        "key"    :    "value"   ,
        "array"  : [ 1, 2, 3 ]
    }
    ```
    """
    result = to_json(markdown)
    assert result == {"key": "value", "array": [1, 2, 3]}


def test_to_json_special_characters():
    # Test JSON with special characters
    json_str = """
    ```json
    {
        "special": "\\n\\t\\r",
        "unicode": "\\u0041"
    }
    ```
    """
    result = to_json(json_str)
    assert result == {"special": "\n\t\r", "unicode": "A"}


def test_to_json_empty_blocks():
    # Test empty JSON code blocks
    markdown = """
    ```json
    ```
    ```json
    ```
    """
    with pytest.raises(Exception):
        to_json(markdown)
