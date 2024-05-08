from enum import Enum

from pydantic import Field
from lionagi.libs.ln_convert import to_str
from ..generic import Mail, Node


# Enums for defining message fields and roles
class MessageField(str, Enum):
    """
    Enum to store message fields for consistent referencing.
    """

    LION_ID = "lion_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"


class MessageRole(str, Enum):
    """
    Enum for possible roles a message can assume in a conversation.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# Base class for messages
class RoledMessage(Node, Mail):
    """
    A base class representing a message with validators and properties.
    """

    role: MessageRole | None = Field(
        default=None,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

    @property
    def chat_msg(self) -> dict | None:
        """return message in chat representation"""
        try:
            return self._check_chat_msg()
        except:
            return None

    def _check_chat_msg(self):
        if self.role is None:
            raise ValueError("Message role not set")

        role = self.role.value if isinstance(self.role, Enum) else self.role
        if role not in [i.value for i in MessageRole]:
            raise ValueError(f"Invalid message role: {role}")

        try:
            content_str = to_str(self.content)
        except Exception as e:
            raise ValueError(
                f"Failed to convert {self.content} into a string value"
            ) from e

        return {role: content_str}

    def __str__(self):
        """
        Provides a string representation of the message with content preview.
        """
        content_preview = (
            f"{self.content[:75]}..."
            if len(str(self.content)) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"
