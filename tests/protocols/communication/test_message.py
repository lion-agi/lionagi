from enum import Enum

import pytest
from pydantic import ConfigDict

from lionagi.protocols.types import (
    MESSAGE_FIELDS,
    MessageField,
    MessageFlag,
    MessageRole,
    RoledMessage,
)


class CustomMessage(RoledMessage):
    """Custom implementation of RoledMessage for testing"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def _format_content(self):
        if isinstance(self.content, list):
            return {"role": self.role.value, "content": self.content}
        return {"role": self.role.value, "content": str(self.content)}


def test_message_role_enum():
    """Test MessageRole enumeration"""
    assert isinstance(MessageRole.SYSTEM, Enum)
    assert isinstance(MessageRole.USER, Enum)
    assert isinstance(MessageRole.ASSISTANT, Enum)

    assert MessageRole.SYSTEM.value == "system"
    assert MessageRole.USER.value == "user"
    assert MessageRole.ASSISTANT.value == "assistant"


def test_message_flag_enum():
    """Test MessageFlag enumeration"""
    assert isinstance(MessageFlag.MESSAGE_CLONE, Enum)
    assert isinstance(MessageFlag.MESSAGE_LOAD, Enum)

    assert MessageFlag.MESSAGE_CLONE.value == "MESSAGE_CLONE"
    assert MessageFlag.MESSAGE_LOAD.value == "MESSAGE_LOAD"


def test_roled_message_initialization():
    """Test basic initialization of RoledMessage"""
    message = CustomMessage(
        role=MessageRole.USER, sender="user", recipient="assistant"
    )

    assert message.role == MessageRole.USER
    assert isinstance(message.content, dict)
    assert message.sender == "user"
    assert message.recipient == "assistant"


def test_roled_message_role_validation():
    """Test role validation in RoledMessage"""
    # Valid roles
    for role in MessageRole:
        message = CustomMessage(
            role=role, sender="user", recipient="assistant"
        )
        assert message.role == role

    # Invalid role
    with pytest.raises(ValueError):
        CustomMessage(
            role="invalid_role", sender="user", recipient="assistant"
        )


def test_roled_message_clone():
    """Test cloning functionality of RoledMessage"""
    original = CustomMessage(
        role=MessageRole.USER,
        content={"test": "content"},
        sender="user",
        recipient="assistant",
    )

    cloned = original.clone()

    assert cloned.role == original.role
    assert cloned.content == original.content
    assert cloned.metadata["clone_from"] == original


def test_roled_message_from_dict():
    """Test creating RoledMessage from dictionary"""
    data = {
        "role": MessageRole.USER.value,
        "content": {"test": "content"},
        "sender": "user",
        "recipient": "assistant",
        "metadata": {"key": "value"},
    }

    message = CustomMessage.model_validate(data)

    assert message.role == MessageRole.USER
    assert message.content["test"] == "content"
    assert message.sender == "user"
    assert message.recipient == "assistant"
    assert message.metadata["key"] == "value"


def test_roled_message_str_representation():
    """Test string representation of RoledMessage"""
    message = CustomMessage(
        role=MessageRole.USER,
        content={"test": "content"},
        sender="user",
        recipient="assistant",
    )

    str_repr = str(message)
    assert "Message" in str_repr
    assert "role=user" in str_repr
    assert "sender=user" in str_repr
    assert "content" in str_repr


def test_roled_message_to_log():
    """Test conversion of RoledMessage to Log"""
    message = CustomMessage(
        role=MessageRole.USER,
        content={"test": "content"},
        sender="user",
        recipient="assistant",
    )

    log = message.to_log()

    assert log.content == message.to_dict()


def test_roled_message_serialization():
    """Test serialization of RoledMessage"""
    message = CustomMessage(
        role=MessageRole.USER,
        content={"test": "content"},
        sender="user",
        recipient="assistant",
    )

    serialized = message.model_dump()

    assert serialized["role"] == MessageRole.USER.value
    assert serialized["content"]["test"] == "content"


def test_roled_message_protected_init():
    """Test protected initialization of RoledMessage"""
    data = {
        "role": MessageRole.USER.value,
        "content": {"test": "content"},
        "sender": "user",
        "recipient": "assistant",
    }

    message = CustomMessage.model_validate(data)

    assert message.role == MessageRole.USER
    assert message.content["test"] == "content"
    assert message.sender == "user"
    assert message.recipient == "assistant"
