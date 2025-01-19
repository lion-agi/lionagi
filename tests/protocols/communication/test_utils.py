import pytest
from pydantic import BaseModel

from lionagi.protocols.generic.element import Element
from lionagi.protocols.messages.base import validate_sender_recipient
from lionagi.protocols.messages.instruction import (
    format_image_content,
    format_image_item,
    format_text_content,
    format_text_item,
    prepare_instruction_content,
    prepare_request_response_format,
)
from lionagi.protocols.messages.system import format_system_content


@pytest.fixture
def sample_element():
    class SampleElement(Element):
        """Sample element class for ID testing"""

        pass

    return SampleElement()


def test_format_system_content():
    """Test formatting system content"""
    message = "Test system message"

    # Without datetime
    content = format_system_content(None, message)
    assert isinstance(content, dict)
    assert content["system_message"] == message
    assert "system_datetime" not in content

    # With datetime boolean
    content = format_system_content(True, message)
    assert "system_datetime" in content
    assert isinstance(content["system_datetime"], str)

    # With custom datetime string
    custom_datetime = "2023-01-01"
    content = format_system_content(custom_datetime, message)
    assert content["system_datetime"] == custom_datetime


def test_prepare_request_response_format():
    """Test preparing request response format"""
    fields = {"name": "string", "age": "integer"}
    format_str = prepare_request_response_format(fields)

    assert "MUST RETURN JSON-PARSEABLE RESPONSE" in format_str
    assert "```json" in format_str
    assert str(fields) in format_str


def test_format_image_item():
    """Test formatting image items"""
    image_id = "test_image_base64"
    detail = "low"

    result = format_image_item(image_id, detail)

    assert result["type"] == "image_url"
    assert "data:image/jpeg;base64" in result["image_url"]["url"]
    assert result["image_url"]["detail"] == detail


def test_format_text_item():
    """Test formatting text items"""
    # Test with string
    text = "Test text"
    result = format_text_item(text)
    assert text in result

    # Test with dictionary
    dict_item = {"key": "value"}
    result = format_text_item(dict_item)
    assert "key: value" in result

    # Test with list
    list_items = ["item1", "item2"]
    result = format_text_item(list_items)
    assert "item1" in result
    assert "item2" in result


def test_format_image_content():
    """Test formatting image content"""
    text = "Test text"
    images = ["image1_base64", "image2_base64"]
    detail = "low"

    result = format_image_content(text, images, detail)

    assert isinstance(result, list)
    assert result[0]["type"] == "text"
    assert result[0]["text"] == text
    assert all(item["type"] == "image_url" for item in result[1:])
    assert len(result) == len(images) + 1


def test_prepare_instruction_content():
    """Test preparing instruction content"""
    # Test basic content
    result = prepare_instruction_content(
        guidance="Test guidance",
        instruction="Test instruction",
        context={"test": "context"},
    )

    assert isinstance(result, dict)
    assert result["guidance"] == "Test guidance"
    assert result["instruction"] == "Test instruction"
    assert {"test": "context"} in result["context"]

    # Test with request model
    class RequestModel(BaseModel):
        name: str
        age: int

    result = prepare_instruction_content(
        instruction="Test", request_model=RequestModel
    )

    assert result["request_model"] == RequestModel
    assert "request_fields" in result
    assert "name" in result["request_fields"]
    assert "age" in result["request_fields"]

    # Test with images
    result = prepare_instruction_content(
        instruction="Test", images=["image1"], image_detail="low"
    )

    assert result["images"] == ["image1"]
    assert result["image_detail"] == "low"


def test_validate_sender_recipient(sample_element):
    """Test sender/recipient validation"""
    # Test valid system roles
    valid_roles = ["system", "user", "assistant", "action", "unset"]
    for role in valid_roles:
        assert validate_sender_recipient(role) == role

    # Test None value
    assert validate_sender_recipient(None) == "unset"

    # Test with valid Element instance
    assert validate_sender_recipient(sample_element) == sample_element.id

    # Test invalid values
    with pytest.raises(ValueError):
        validate_sender_recipient(123)

    with pytest.raises(ValueError):
        validate_sender_recipient({"invalid": "type"})
