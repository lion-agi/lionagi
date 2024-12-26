import json

import pytest

from lionagi.utils import to_json


def test_direct_json():
    data = '{"name": "Alice", "age": 30}'
    result = to_json(data)
    assert result == {"name": "Alice", "age": 30}


def test_direct_json_invalid_no_fuzzy():
    data = '{name: "Bob"}'  # invalid JSON keys
    result = to_json(data)
    # Attempt fails, no code blocks, returns empty list
    assert result == []


def test_direct_json_fuzzy():
    data = '{name: "Bob"}'
    # With fuzzy_parse=True, fuzzy parser might fix missing quotes around keys
    result = to_json(data, fuzzy_parse=True)
    assert result == {"name": "Bob"}


def test_empty_string():
    result = to_json("")
    # Empty string cannot be parsed directly, no code blocks -> empty list
    assert result == []


def test_code_block_single():
    data = """
    Some text above
    ```json
    {"key": "value"}
    ```
    Some text below
    """
    result = to_json(data)
    assert result == {"key": "value"}


def test_code_block_multiple():
    data = """
    ```json
    {"key1": "value1"}
    ```
    Some text
    ```json
    {"key2": "value2"}
    ```
    """
    result = to_json(data)
    # Multiple code blocks should return a list
    assert isinstance(result, list)
    assert result == [{"key1": "value1"}, {"key2": "value2"}]


def test_code_block_fuzzy():
    data = """
    ```json
    {key: "val"}
    ```
    """
    # With fuzzy_parse=True, parse the block as fuzzy JSON
    result = to_json(data, fuzzy_parse=True)
    assert result == {"key": "val"}


def test_no_json_anywhere():
    data = "Just some random text without JSON"
    result = to_json(data)
    # No direct parse and no code blocks found
    assert result == []


def test_list_input():
    data_list = ["```json", '{"nested": {"inner": [1,2,3]}}', "```"]
    result = to_json(data_list)
    assert result == {"nested": {"inner": [1, 2, 3]}}


def test_complex_json():
    data = '{"arr":[{"x":10},{"y":20}],"flag":true}'
    result = to_json(data)
    assert result == {"arr": [{"x": 10}, {"y": 20}], "flag": True}


def test_invalid_blocks_no_fuzzy():
    data = """
    ```json
    {invalidJson: "yes"}
    ```
    """
    # Without fuzzy, cannot parse invalid JSON in code block
    # Should raise json.JSONDecodeError internally => no except => raise from function?
    # Actually currently we do not suppress code block parse errors, they raise exceptions directly.
    # In that case we might want to handle or test that we get a ValueError or empty list.
    # The current code tries json.loads and it fails => so it raises. No code suggests suppression?
    # The function: no try/except around block parsing separately. If load fails => error raised.
    with pytest.raises(json.JSONDecodeError):
        to_json(data)


def test_invalid_blocks_with_fuzzy():
    data = """
    ```json
    {notQuoted: "hello"}
    ```
    """
    # fuzzy_parse=True may fix the key
    result = to_json(data, fuzzy_parse=True)
    assert result == {"notQuoted": "hello"}


def test_multiple_blocks_some_invalid():
    data = """
    ```json
    {"ok": true}
    ```
    ```json
    {missingQuotes: "no"}
    ```
    """
    # Without fuzzy, second block invalid
    with pytest.raises(json.JSONDecodeError):
        to_json(data, fuzzy_parse=False)

    # With fuzzy parse, both should parse
    result = to_json(data, fuzzy_parse=True)
    assert result == [{"ok": True}, {"missingQuotes": "no"}]


def test_no_json_blocks_but_markdown():
    data = "```something else``` not json"
    result = to_json(data)
    assert result == []
