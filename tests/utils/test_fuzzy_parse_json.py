from typing import Any, Dict, List

import pytest

from lionagi.utils.fuzzy_parse_json import fix_json_string, fuzzy_parse_json


def test_valid_json():
    data = '{"name": "John", "age": 30}'
    parsed = fuzzy_parse_json(data)
    assert parsed == {"name": "John", "age": 30}


def test_trailing_commas():
    data = '{"name": "John", "age": 30,}'
    # Step 2 (clean) might fix trailing commas by normalizing spacing and keys,
    # but trailing commas are invalid. The parser won't fix trailing commas by default.
    # Since we didn't code a trailing comma fix specifically, let's see what fix_json_string does:
    # Actually, fix_json_string won't remove trailing commas. Let's add a test that should fail.
    with pytest.raises(ValueError):
        fuzzy_parse_json(data)


def test_single_quotes():
    data = "{'name': 'John', 'age': 30}"
    # Should replace single quotes with double
    parsed = fuzzy_parse_json(data)
    assert parsed == {"name": "John", "age": 30}


def test_unmatched_brackets():
    # Missing closing bracket
    data = '{"name": "John", "age": 30'
    parsed = fuzzy_parse_json(data)
    assert parsed == {"name": "John", "age": 30}


def test_extra_closing_bracket():
    data = '{"name": "John"}]'
    # fix_json_string will raise ValueError due to extra closing bracket
    with pytest.raises(ValueError):
        fuzzy_parse_json(data)


def test_non_string_input():
    with pytest.raises(TypeError):
        fuzzy_parse_json(123)


def test_empty_string():
    with pytest.raises(ValueError):
        fuzzy_parse_json("")


def test_invalid_json():
    # Completely invalid JSON can't be fixed by these heuristics
    data = "Just some random text, not json"
    with pytest.raises(ValueError):
        fuzzy_parse_json(data)


def test_array_of_objects():
    data = '[{"name":"John"}, {"name":"Jane"}]'
    parsed = fuzzy_parse_json(data)
    assert parsed == [{"name": "John"}, {"name": "Jane"}]


def test_complex_fixes():
    # Missing quote around a key and single quotes
    data = "{name: 'John', 'age':30}"
    parsed = fuzzy_parse_json(data)
    assert parsed == {"name": "John", "age": 30}


def test_fix_json_string():
    # Just test the fix_json_string function
    data = '{"name":"John","items":[{"id":1}'
    fixed = fix_json_string(data)
    # Should close the missing brackets: ']}'
    assert fixed == '{"name":"John","items":[{"id":1}]}'
    parsed = fuzzy_parse_json(fixed)
    assert parsed == {"name": "John", "items": [{"id": 1}]}
