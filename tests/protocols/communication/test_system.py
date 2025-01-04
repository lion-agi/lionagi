import pytest

from lionagi.protocols.types import MessageRole, System


def test_system_initialization():
    """Test basic initialization of System"""
    system_msg = "Test system message"
    system = System.create(system_message=system_msg)

    assert system.role == MessageRole.SYSTEM
    assert system_msg in system.rendered
    assert system.sender == "system"
    assert system.recipient == "assistant"


def test_system_with_datetime():
    """Test System with datetime information"""
    system_msg = "Test system message"
    system = System.create(system_message=system_msg, system_datetime=True)

    assert "System datetime:" in system.rendered
    assert system_msg in system.rendered
    assert "system_datetime" in system.content


def test_system_with_custom_datetime():
    """Test System with custom datetime string"""
    custom_datetime = "2023-01-01 12:00:00"
    system = System.create(
        system_message="Test", system_datetime=custom_datetime
    )

    assert custom_datetime in system.content["system_datetime"]
    assert custom_datetime in system.rendered


def test_system_update():
    """Test updating System message"""
    system = System.create(system_message="Initial message")

    # Update system message
    new_message = "Updated message"
    system.update(system_message=new_message)
    assert new_message in system.rendered

    # Update sender and recipient
    system.update(sender="system", recipient="user")
    assert system.sender == "system"
    assert system.recipient == "user"

    # Update with datetime
    system.update(system_message="Test", system_datetime=True)
    assert "System datetime:" in system.rendered


def test_system_content_format():
    """Test System content formatting"""
    system = System.create(system_message="Test message")

    formatted = system.chat_msg
    assert formatted["role"] == MessageRole.SYSTEM.value
    assert formatted["content"] == system.rendered


def test_system_with_default_message():
    """Test System with default message"""
    system = System.create()

    assert "You are a helpful AI assistant" in system.rendered
    assert "Let's think step by step" in system.rendered


def test_system_clone():
    """Test cloning a System message"""
    original = System.create(
        system_message="Test message",
        system_datetime=True,
        sender="system",
        recipient="user",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.rendered == original.rendered
    assert original.content == cloned.content
    assert cloned.metadata["clone_from"] == original


def test_system_str_representation():
    """Test string representation of System"""
    system = System.create(system_message="Test message")

    str_repr = str(system)
    assert "Message" in str_repr
    assert "role=system" in str_repr
    assert "Test message" in str_repr


def test_system_message_load():
    """Test loading System from protected parameters"""
    protected_params = {
        "role": MessageRole.SYSTEM,
        "content": {"system_message": "Test message"},
        "sender": "system",
        "recipient": "user",
    }

    system = System.from_dict(protected_params)

    assert system.role == MessageRole.SYSTEM
    assert "Test message" in system.rendered
    assert system.sender == "system"
    assert system.recipient == "user"


def test_system_validation():
    """Test System validation"""
    # Test with invalid sender/recipient
    with pytest.raises(ValueError):
        System.create(system_message="Test", sender=123)

    with pytest.raises(ValueError):
        System.create(system_message="Test", recipient=123)


def test_system_serialization():
    """Test System serialization"""
    system = System.create(system_message="Test message", system_datetime=True)

    serialized = system.model_dump()

    assert serialized["role"] == MessageRole.SYSTEM.value
    assert isinstance(serialized["content"], dict)
    assert "system_message" in serialized["content"]
    assert "system_datetime" in serialized["content"]


def test_system_chat_message():
    """Test System chat message format"""
    system = System.create(system_message="Test message")

    chat_msg = system.chat_msg
    assert chat_msg["role"] == "system"
    assert chat_msg["content"] == system.rendered
