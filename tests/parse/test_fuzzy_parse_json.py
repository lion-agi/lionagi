import pytest

from lionagi.libs.parse.fuzzy_parse_json import (
    _assemble,
    _check_valid_str,
    _clean_json_string,
    _fix_braces,
    fix_json_string,
    fuzzy_parse_json,
)


def test_fuzzy_parse_json_valid():
    json_str = '{"key": "value"}'
    result = fuzzy_parse_json(json_str)
    assert result == {"key": "value"}


def test_fuzzy_parse_json_single_quotes():
    json_str = "{'key': 'value'}"
    result = fuzzy_parse_json(json_str)
    assert result == {"key": "value"}


def test_fuzzy_parse_json_missing_quotes():
    json_str = "{key: 'value'}"
    result = fuzzy_parse_json(json_str)
    assert result == {"key": "value"}


def test_fuzzy_parse_json_missing_braces():
    json_str = "key: 'value'"
    with pytest.raises(ValueError, match="Invalid JSON string"):
        fuzzy_parse_json(json_str)


def test_fuzzy_parse_json_unclosed_braces():
    json_str = '{"key": "value"'
    result = fuzzy_parse_json(json_str)
    assert result == {"key": "value"}


def test_fuzzy_parse_json_trailing_comma():
    json_str = '{"key": "value",}'
    result = fuzzy_parse_json(json_str)
    assert result == {"key": "value"}


def test_fuzzy_parse_json_invalid():
    with pytest.raises(ValueError, match="Invalid JSON string"):
        fuzzy_parse_json("not a json string at all")


def test_fuzzy_parse_json_empty():
    with pytest.raises(ValueError, match="Input string is empty"):
        fuzzy_parse_json("")


def test_fuzzy_parse_json_wrong_type():
    with pytest.raises(TypeError, match="Input must be a string"):
        fuzzy_parse_json(123)


def test_clean_json_string():
    json_str = "{ key : 'value' }"
    result = _clean_json_string(json_str)
    assert result == '{ key : "value" }'


def test_clean_json_string_multiple_spaces():
    json_str = "{   key   :    'value'    }"
    result = _clean_json_string(json_str)
    assert result == '{ key : "value" }'


def test_clean_json_string_escaped_quotes():
    json_str = "{ key: 'value with \\'quote\\'' }"
    result = _clean_json_string(json_str)
    assert result == '{"key": "value with \\\'quote\\\'" }'


def test_fix_json_string_valid():
    json_str = '{"key": "value"}'
    result = fix_json_string(json_str)
    assert result == '{"key": "value"}'


def test_fix_json_string_unclosed_brace():
    json_str = '{"key": "value"'
    result = fix_json_string(json_str)
    assert result == '{"key": "value"}'


def test_fix_json_string_unclosed_bracket():
    json_str = '{"array": ['
    result = fix_json_string(json_str)
    assert result == '{"array": []}'


def test_fix_json_string_nested():
    json_str = '{"obj": {"key": "value"'
    result = fix_json_string(json_str)
    assert result == '{"obj": {"key": "value"}}'


def test_fix_json_string_empty():
    with pytest.raises(ValueError, match="Input string is empty"):
        fix_json_string("")


def test_fix_json_string_mismatched():
    with pytest.raises(ValueError, match="Mismatched bracket"):
        fix_json_string('{"key": ]')


def test_fix_json_string_extra_closing():
    with pytest.raises(ValueError, match="Extra closing bracket"):
        fix_json_string('{"key": "value"}}')


def test_check_valid_str():
    _check_valid_str('{"key": "value"}')  # Should not raise


def test_check_valid_str_empty():
    with pytest.raises(ValueError, match="Input string is empty"):
        _check_valid_str("")


def test_check_valid_str_wrong_type():
    with pytest.raises(TypeError, match="Input must be a string"):
        _check_valid_str(123)


def test_fix_braces():
    json_str = 'key: "value"'
    result = _fix_braces(json_str)
    assert result == '{key: "value"}'


def test_fix_braces_trailing_comma():
    json_str = '{"key": "value",}'
    result = _fix_braces(json_str)
    assert result == '{"key": "value"}'


def test_fix_braces_already_valid():
    json_str = '{"key": "value"}'
    result = _fix_braces(json_str)
    assert result == '{"key": "value"}'


def test_assemble():
    json_str = 'key: "value" other_key: "other_value"'
    result = _assemble(json_str)
    assert result == '{key:"value" other_key,"other_value":}'


def test_assemble_with_spaces():
    json_str = 'key : "value" other_key : "other_value"'
    result = _assemble(json_str)
    assert result == '{key:"value" other_key,"other_value":}'


def test_assemble_with_braces():
    json_str = '{"key": "value" other_key: "other_value"}'
    result = _assemble(json_str)
    assert result == '{"key":"value" other_key,"other_value":}'


def test_fuzzy_parse_json_complex():
    json_str = """
    {
        string_key: 'string value',
        number_key: 42,
        array_key: ['item1', 'item2'],
        object_key: {
            nested_key: 'nested value'
        }
    """
    result = fuzzy_parse_json(json_str)
    assert result == {
        "string_key": "string value",
        "number_key": 42,
        "array_key": ["item1", "item2"],
        "object_key": {"nested_key": "nested value"},
    }


def test_fuzzy_parse_json_list():
    json_str = '[{"key1": "value1"}, {"key2": "value2"}]'
    result = fuzzy_parse_json(json_str)
    assert result == [{"key1": "value1"}, {"key2": "value2"}]
