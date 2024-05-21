"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import typing
from enum import Enum
from typing import Any

# from pydantic._internal._utils import AbstractSetIntStr, MappingIntStrAny
# from pydantic.main import Model

from lionagi.libs.ln_convert import to_str

from lionagi.core.collections.abc import Sendable, Field
from lionagi.core.generic.node import Node


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
class RoledMessage(Node, Sendable):
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

        return {"role": role, "content": content_str}

    def __str__(self):
        """
        Provides a string representation of the message with content preview.
        """
        content_preview = (
            f"{str(self.content)[:75]}..."
            if len(str(self.content)) > 75
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"
