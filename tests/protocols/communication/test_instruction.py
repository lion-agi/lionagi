import pytest
from pydantic import BaseModel

from lionagi.protocols.types import Instruction, MessageRole


class RequestModel(BaseModel):
    """Model for testing request fields"""

    name: str
    age: int
    optional: str | None = None


def test_instruction_basic_initialization():
    """Test basic initialization of Instruction"""
    instruction = Instruction.create(
        instruction="Test instruction", sender="user", recipient="assistant"
    )

    assert instruction.role == MessageRole.USER
    assert instruction.instruction == "Test instruction"
    assert instruction.sender == "user"
    assert instruction.recipient == "assistant"


def test_instruction_with_context():
    """Test Instruction with context"""
    context = {"key": "value"}
    instruction = Instruction.create(
        instruction="Test",
        context=context,
        sender="user",
        recipient="assistant",
    )

    assert instruction.context == [context]
    instruction.extend_context({"additional": "context"})
    assert len(instruction.context) == 2


def test_instruction_with_guidance():
    """Test Instruction with guidance"""
    guidance = "Test guidance"
    instruction = Instruction.create(
        instruction="Test",
        guidance=guidance,
        sender="user",
        recipient="assistant",
    )

    assert instruction.guidance == guidance
    instruction.guidance = "New guidance"
    assert instruction.guidance == "New guidance"


def test_instruction_with_request_fields():
    """Test Instruction with request fields"""
    fields = {"field1": "type1", "field2": "type2"}
    instruction = Instruction.create(
        instruction="Test",
        request_fields=fields,
        sender="user",
        recipient="assistant",
    )

    assert instruction.request_fields == fields
    assert "request_response_format" in instruction.content


def test_instruction_with_request_model():
    """Test Instruction with request model"""
    instruction = Instruction.create(
        instruction="Test",
        response_format=RequestModel,
        sender="user",
        recipient="assistant",
    )

    assert instruction.response_format == RequestModel
    assert instruction.request_fields
    assert "name" in instruction.request_fields
    assert "age" in instruction.request_fields


def test_instruction_with_images():
    """Test Instruction with images"""
    images = ["image1", "image2"]
    instruction = Instruction.create(
        instruction="Test",
        images=images,
        image_detail="low",
        sender="user",
        recipient="assistant",
    )

    assert instruction.images == images
    assert instruction.image_detail == "low"

    # Test extending images
    instruction.extend_images(["image3"], image_detail="high")
    assert len(instruction.images) == 3
    assert instruction.image_detail == "high"


def test_instruction_with_plain_content():
    """Test Instruction with plain content"""
    content = "Plain text content"
    instruction = Instruction.create(
        instruction="Test",
        plain_content=content,
        sender="user",
        recipient="assistant",
    )

    assert instruction.plain_content == content
    instruction.plain_content = "New content"
    assert instruction.plain_content == "New content"


def test_instruction_update():
    """Test Instruction update method"""
    instruction = Instruction.create(
        instruction="Initial", sender="user", recipient="assistant"
    )

    new_context = {"new": "context"}
    instruction.extend_context(new_context)
    instruction.update(
        guidance="New guidance", instruction="Updated instruction"
    )

    assert instruction.guidance == "New guidance"
    assert instruction.instruction == "Updated instruction"
    assert new_context in instruction.context


def test_instruction_content_format():
    """Test Instruction content formatting"""
    instruction = Instruction.create(
        instruction="Test instruction",
        guidance="Test guidance",
        context={"context": "value"},
        sender="user",
        recipient="assistant",
    )

    formatted = instruction.chat_msg
    assert formatted["role"] == MessageRole.USER.value
    assert isinstance(formatted["content"], str)
    assert "Test instruction" in formatted["content"]
    assert "Test guidance" in formatted["content"]
    assert "context" in formatted["content"]


def test_instruction_with_tool_schemas():
    """Test Instruction with tool schemas"""
    schemas = {
        "tool1": {"type": "object", "properties": {}},
        "tool2": {"type": "object", "properties": {}},
    }
    instruction = Instruction.create(
        instruction="Test",
        tool_schemas=schemas,
        sender="user",
        recipient="assistant",
    )

    assert instruction.tool_schemas == schemas


def test_instruction_clone():
    """Test cloning an Instruction"""
    original = Instruction.create(
        instruction="Test instruction",
        guidance="Test guidance",
        context={"test": "context"},
        sender="user",
        recipient="assistant",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.instruction == original.instruction
    assert cloned.guidance == original.guidance
    assert cloned.context == original.context
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_instruction_validation():
    """Test Instruction validation"""
    # Test that request_model and request_fields cannot be used together
    with pytest.raises(ValueError):
        Instruction.create(
            instruction="Test",
            response_format=RequestModel,
            request_fields={"field": "type"},
            sender="user",
            recipient="assistant",
        )


def test_instruction_str_representation():
    """Test string representation of Instruction"""
    instruction = Instruction.create(
        instruction="Test instruction",
        guidance="Test guidance",
        sender="user",
        recipient="assistant",
    )

    str_repr = str(instruction)
    assert "Message" in str_repr
    assert "role=user" in str_repr
    assert instruction.instruction in instruction.content["instruction"]
