import pytest

from lionagi.protocols.messages.system import MessageRole, System


def test_system_initialization():
    """Test basic initialization of System"""
    system_msg = "Test system message"
    system = System(system=system_msg)

    assert system.role == MessageRole.SYSTEM
    assert system.system_info == system_msg
    assert system.sender == "system"
    assert system.recipient == "N/A"


def test_system_with_datetime():
    """Test System with datetime information"""
    system_msg = "Test system message"
    system = System(system=system_msg, system_datetime=True)

    assert "System datetime:" in system.system_info
    assert system_msg in system.system_info
    assert "system_datetime" in system.content


def test_system_with_custom_datetime():
    """Test System with custom datetime string"""
    custom_datetime = "2023-01-01 12:00:00"
    system = System(system="Test", system_datetime=custom_datetime)

    assert custom_datetime in system.content["system_datetime"]
    assert custom_datetime in system.system_info


def test_system_update():
    """Test updating System message"""
    system = System(system="Initial message")

    # Update system message
    new_message = "Updated message"
    system.update(system=new_message)
    assert system.system_info == new_message

    # Update sender and recipient
    system.update(sender="system", recipient="user")
    assert system.sender == "system"
    assert system.recipient == "user"

    # Update with datetime
    system.update(system="Test", system_datetime=True)
    assert "System datetime:" in system.system_info


def test_system_content_format():
    """Test System content formatting"""
    system = System(system="Test message")

    formatted = system._format_content()
    assert formatted["role"] == MessageRole.SYSTEM.value
    assert formatted["content"] == system.system_info


def test_system_with_default_message():
    """Test System with default message"""
    system = System()

    assert "You are a helpful AI assistant" in system.system_info
    assert "Let's think step by step" in system.system_info


def test_system_clone():
    """Test cloning a System message"""
    original = System(
        system="Test message",
        system_datetime=True,
        sender="system",
        recipient="user",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.system_info == original.system_info
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_system_str_representation():
    """Test string representation of System"""
    system = System(system="Test message")

    str_repr = str(system)
    assert "Message" in str_repr
    assert "role=MessageRole.SYSTEM" in str_repr
    assert "Test message" in str_repr


def test_system_message_load():
    """Test loading System from protected parameters"""
    protected_params = {
        "role": MessageRole.SYSTEM.value,
        "content": {"system": "Test message"},
        "sender": "system",
        "recipient": "user",
    }

    system = System.from_dict(protected_params)

    assert system.role == MessageRole.SYSTEM
    assert "Test message" in system.system_info
    assert system.sender == "system"
    assert system.recipient == "user"


def test_system_validation():
    """Test System validation"""
    # Test with invalid sender/recipient
    with pytest.raises(ValueError):
        System(system="Test", sender=123)

    with pytest.raises(ValueError):
        System(system="Test", recipient=123)


def test_system_serialization():
    """Test System serialization"""
    system = System(system="Test message", system_datetime=True)

    serialized = system.model_dump()

    assert serialized["role"] == MessageRole.SYSTEM.value
    assert isinstance(serialized["content"], dict)
    assert "system" in serialized["content"]
    assert "system_datetime" in serialized["content"]


def test_system_chat_message():
    """Test System chat message format"""
    system = System(system="Test message")

    chat_msg = system.chat_msg
    assert chat_msg["role"] == "system"
    assert chat_msg["content"] == system.system_info
