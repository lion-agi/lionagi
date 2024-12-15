from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import BaseModel

from lionagi.libs.parse.validate_mapping import (
    KeysDict,
    validate_keys,
    validate_mapping,
)


# Test fixtures
class PydanticModel(BaseModel):
    name: str
    value: int


@dataclass
class DataClassModel:
    name: str
    value: int


# Test validate_keys function
def test_validate_keys_exact_match():
    d = {"name": "test", "value": 42}
    keys = ["name", "value"]
    result = validate_keys(d, keys)
    assert result == d


def test_validate_keys_fuzzy_match():
    d = {"Name": "test", "Value": 42}
    keys = ["name", "value"]
    result = validate_keys(d, keys, fuzzy_match=True)
    assert result == {"name": "test", "value": 42}


def test_validate_keys_handle_unmatched_ignore():
    d = {"name": "test", "extra": "value"}
    keys = ["name"]
    result = validate_keys(d, keys, handle_unmatched="ignore")
    assert result == d


def test_validate_keys_handle_unmatched_raise():
    d = {"name": "test", "extra": "value"}
    keys = ["name"]
    with pytest.raises(ValueError, match="Unmatched keys found"):
        validate_keys(d, keys, handle_unmatched="raise")


def test_validate_keys_handle_unmatched_remove():
    d = {"name": "test", "extra": "value"}
    keys = ["name"]
    result = validate_keys(d, keys, handle_unmatched="remove")
    assert result == {"name": "test"}


def test_validate_keys_handle_unmatched_fill():
    d = {"name": "test"}
    keys = ["name", "value"]
    result = validate_keys(d, keys, handle_unmatched="fill", fill_value=None)
    assert result == {"name": "test", "value": None}


def test_validate_keys_handle_unmatched_force():
    d = {"name": "test", "extra": "value"}
    keys = ["name", "value"]
    result = validate_keys(d, keys, handle_unmatched="force", fill_value=None)
    assert result == {"name": "test", "value": None}


def test_validate_keys_fill_mapping():
    d = {"name": "test"}
    keys = ["name", "value"]
    fill_mapping = {"value": 42}
    result = validate_keys(
        d, keys, handle_unmatched="fill", fill_mapping=fill_mapping
    )
    assert result == {"name": "test", "value": 42}


def test_validate_keys_strict():
    d = {"name": "test"}
    keys = ["name", "value"]
    with pytest.raises(ValueError, match="Missing required keys"):
        validate_keys(d, keys, strict=True)


def test_validate_keys_invalid_input():
    # Test non-dict input
    with pytest.raises(TypeError, match="must be a dictionary"):
        validate_keys("not a dict", ["key"])

    # Test None keys
    with pytest.raises(TypeError, match="cannot be None"):
        validate_keys({}, None)

    # Test invalid similarity threshold
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        validate_keys({}, ["key"], similarity_threshold=2.0)


# Test validate_mapping function
def test_validate_mapping_dict_input():
    d = {"name": "test", "value": 42}
    keys = ["name", "value"]
    result = validate_mapping(d, keys)
    assert result == d


def test_validate_mapping_json_string():
    json_str = '{"name": "test", "value": 42}'
    keys = ["name", "value"]
    result = validate_mapping(json_str, keys)
    assert result == {"name": "test", "value": 42}


def test_validate_mapping_pydantic_model():
    model = PydanticModel(name="test", value=42)
    keys = ["name", "value"]
    result = validate_mapping(model, keys)
    assert result == {"name": "test", "value": 42}


def test_validate_mapping_dataclass():
    data = DataClassModel(name="test", value=42)
    keys = ["name", "value"]
    result = validate_mapping(data, keys)
    assert result == {"name": "test", "value": 42}


def test_validate_mapping_xml_string():
    xml_str = "<root><name>test</name><value>42</value></root>"
    keys = ["name", "value"]
    result = validate_mapping(xml_str, keys)
    assert result == {"name": "test", "value": "42"}


def test_validate_mapping_suppress_errors():
    # Test with invalid input but suppressed errors
    result = validate_mapping(
        object(), ["key"], suppress_conversion_errors=True
    )
    assert result == {}

    # Test without suppression
    with pytest.raises(ValueError, match="Failed to convert input"):
        validate_mapping(object(), ["key"])


def test_validate_mapping_none_input():
    with pytest.raises(TypeError, match="Input cannot be None"):
        validate_mapping(None, ["key"])


def test_validate_mapping_complex_structure():
    d = {
        "user_info": {
            "Name": "test",
            "Age": 25,
        },
        "settings": {
            "Enabled": True,
        },
    }
    keys = ["user_info", "settings"]
    result = validate_mapping(d, keys)
    assert result == d


def test_validate_mapping_with_keysdict():
    keys_dict: KeysDict = {
        "name": str,
        "value": int,
    }
    d = {"name": "test", "value": "42"}
    result = validate_mapping(d, keys_dict)
    assert result == {"name": "test", "value": "42"}


def test_validate_mapping_markdown_codeblock():
    markdown = """
    ```json
    {
        "name": "test",
        "value": 42
    }
    ```
    """
    keys = ["name", "value"]
    result = validate_mapping(markdown, keys)
    assert result == {"name": "test", "value": 42}


def test_validate_mapping_fuzzy_match_threshold():
    d = {"Name": "test", "Value": 42}
    keys = ["name", "value"]

    # Should match with default threshold
    result = validate_mapping(d, keys, similarity_threshold=0.85)
    assert result == {"name": "test", "value": 42}

    # Should not match with high threshold
    result = validate_mapping(d, keys, similarity_threshold=0.99)
    assert result == {"Name": "test", "Value": 42}


def test_validate_mapping_mixed_case_sensitivity():
    d = {"NAME": "test", "value": 42}
    keys = ["name", "VALUE"]

    # Test with fuzzy matching
    result = validate_mapping(d, keys, fuzzy_match=True)
    assert "name" in result or "NAME" in result
    assert "value" in result or "VALUE" in result

    # Test without fuzzy matching
    result = validate_mapping(d, keys, fuzzy_match=False)
    assert result == d


def test_validate_mapping_empty_input():
    # Test empty dict
    result = validate_mapping(
        {}, ["key"], handle_unmatched="fill", fill_value=None
    )
    assert result == {"key": None}

    # Test empty string
    result = validate_mapping(
        "", ["key"], handle_unmatched="fill", fill_value=None
    )
    assert result == {"key": None}


def test_validate_mapping_special_characters():
    d = {"name@123": "test", "value#456": 42}
    keys = ["name@123", "value#456"]
    result = validate_mapping(d, keys)
    assert result == d
