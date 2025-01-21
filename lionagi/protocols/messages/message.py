# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""Core message class implementation for LionAGI's message system.

This module provides the RoledMessage base class, which serves as the foundation
for all message types in the system (system messages, user instructions,
assistant responses, etc.). It includes:

- RoledMessage: Base class with role, content, and template support
- Jinja2 environment setup for message templating
- Serialization helpers for message content
- Clone/copy functionality for message forking

The RoledMessage class combines Node (for graph integration) and Sendable
(for message passing) to create a versatile base for all message types.
"""

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import Field, PrivateAttr, field_serializer

from .._concepts import Sendable
from ..generic.element import Element, IDType
from ..generic.log import Log
from ..graph.node import Node
from .base import (
    MessageFlag,
    MessageRole,
    SenderRecipient,
    validate_sender_recipient,
)

template_path = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(template_path))

__all__ = ("RoledMessage",)


class RoledMessage(Node, Sendable):
    """Base class for all role-based messages in LionAGI.

    This class provides the foundation for all message types in the system,
    combining structured content, role-based identification, and template-based
    rendering. It supports:
    - Role-based message identification (system/user/assistant)
    - Structured content storage with template rendering
    - Sender/recipient tracking for message routing
    - Message cloning and serialization
    - Integration with the graph system via Node inheritance
    - Message passing via Sendable inheritance

    Attributes:
        content (dict): The structured content of the message
        role (MessageRole): The role this message plays (system/user/etc.)
        template (str | Template): Optional Jinja template for rendering
        sender (SenderRecipient): Who sent this message
        recipient (SenderRecipient): Who should receive this message

    Example:
        >>> msg = RoledMessage(
        ...     content={"text": "Hello"},
        ...     role=MessageRole.USER,
        ...     sender="user_123",
        ...     recipient=MessageRole.ASSISTANT
        ... )
        >>> print(msg.rendered)  # Renders content using template
    """

    content: dict = Field(
        default_factory=dict,
        description="The content of the message.",
    )

    role: MessageRole | None = Field(
        None,
        description="The role of the message in the conversation.",
    )

    _flag: MessageFlag | None = PrivateAttr(None)

    template: str | Template | None = None

    sender: SenderRecipient | None = Field(
        default=MessageRole.UNSET,
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: SenderRecipient | None = Field(
        default=MessageRole.UNSET,
        title="Recipient",
        description="The ID of the recipient node or a role.",
    )

    @field_serializer("sender", "recipient")
    def _serialize_sender_recipient(self, value: SenderRecipient) -> str:
        if isinstance(value, MessageRole | MessageFlag):
            return value.value
        if isinstance(value, str):
            return value
        if isinstance(value, Element):
            return str(value.id)
        if isinstance(value, IDType):
            return str(value)
        return str(value)

    @property
    def image_content(self) -> list[dict[str, Any]] | None:
        """Extract image data from message content.

        If the message content contains a chat message array with image
        data (e.g., from a multimodal model), this extracts the image
        information into a structured format.

        Returns:
            list[dict[str,Any]] | None: List of image data dictionaries,
                each containing type and URL information. Returns None if
                no images are found.

        Example:
            >>> msg.image_content
            [{'type': 'image_url',
              'image_url': {'url': 'data:image/jpeg;base64,...'}}]
        """
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]
        return None

    @property
    def chat_msg(self) -> dict[str, Any] | None:
        """Get a chat-compatible representation of this message.

        Converts the message into a format suitable for chat-based LLM
        interactions, following the common {"role": ..., "content": ...}
        pattern used by most LLM providers.

        Returns:
            dict[str, Any]: Dictionary with 'role' and 'content' keys,
                where content is the template-rendered message text.

        Example:
            >>> msg.chat_msg
            {'role': 'user', 'content': 'Hello, how are you?'}
        """
        try:
            return {"role": str(self.role), "content": self.rendered}
        except Exception:
            return None

    @property
    def rendered(self) -> str:
        """
        Attempt to format the message with a Jinja template (if provided).
        If no template, fallback to JSON.

        Returns:
            str: The final formatted string.
        """
        try:
            if isinstance(self.template, str):
                return self.template.format(**self.content)
            if isinstance(self.template, Template):
                return self.template.render(**self.content)
        except Exception:
            return json.dumps(self.content)

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("create() must be implemented in subclass.")

    @classmethod
    def from_dict(cls, dict_: dict):
        """
        Deserialize a dictionary into a RoledMessage or subclass.

        Args:
            dict_ (dict): The raw data.

        Returns:
            RoledMessage: A newly constructed instance.
        """
        try:
            self: RoledMessage = super().from_dict(
                {k: v for k, v in dict_.items() if v}
            )
            self._flag = MessageFlag.MESSAGE_LOAD
            return self
        except Exception as e:
            raise ValueError(f"Invalid RoledMessage data: {e}")

    def is_clone(self) -> bool:
        """
        Check if this message is flagged as a clone.

        Returns:
            bool: True if flagged `MESSAGE_CLONE`.
        """
        return self._flag == MessageFlag.MESSAGE_CLONE

    def clone(self, keep_role: bool = True) -> "RoledMessage":
        """
        Create a shallow copy of this message, possibly resetting the role.

        Args:
            keep_role (bool): If False, set the new message's role to `UNSET`.

        Returns:
            RoledMessage: The new cloned message.
        """
        instance = self.__class__(
            content=self.content,
            role=self.role if keep_role else MessageRole.UNSET,
            metadata={"clone_from": self},
        )
        instance._flag = MessageFlag.MESSAGE_CLONE
        return instance

    def to_log(self) -> Log:
        """
        Convert this message into a `Log`, preserving all current fields.

        Returns:
            Log: An immutable log entry derived from this message.
        """
        return Log.create(self)

    @field_serializer("role")
    def _serialize_role(self, value: MessageRole):
        if isinstance(value, MessageRole):
            return value.value
        return str(value)

    @field_serializer("metadata")
    def _serialize_metadata(self, value: dict):
        if "clone_from" in value:
            origin_obj: RoledMessage = value.pop("clone_from")
            origin_info = origin_obj.to_dict()
            value["clone_from_info"] = {
                "clone_from_info": {
                    "original_id": origin_info["id"],
                    "original_created_at": origin_info["created_at"],
                    "original_sender": origin_info["sender"],
                    "original_recipient": origin_info["recipient"],
                    "original_lion_class": origin_info["metadata"][
                        "lion_class"
                    ],
                    "original_role": origin_info["role"],
                }
            }
        return value

    @field_serializer("template")
    def _serialize_template(self, value: Template | str):
        # We do not store or transmit the raw Template object.
        if isinstance(value, Template):
            return None
        return value

    def update(self, sender, recipient, template, **kwargs):
        """
        Generic update mechanism for customizing the message in place.

        Args:
            sender (SenderRecipient):
                New sender or role.
            recipient (SenderRecipient):
                New recipient or role.
            template (Template | str):
                New jinja Template or format string.
            **kwargs:
                Additional content to merge into self.content.
        """
        if sender:
            self.sender = validate_sender_recipient(sender)
        if recipient:
            self.recipient = validate_sender_recipient(recipient)
        if kwargs:
            self.content.update(kwargs)
        if template:
            if not isinstance(template, Template | str):
                raise ValueError("Template must be a Jinja2 Template or str")
            self.template = template

    def __str__(self) -> str:

        content_preview = (
            f"{str(self.content)[:75]}..."
            if len(str(self.content)) > 75
            else str(self.content)
        )
        return (
            f"Message(role={self.role}, sender={self.sender}, "
            f"content='{content_preview}')"
        )


# File: lionagi/protocols/messages/message.py
