# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Implements the `RoledMessage` base for system, user, assistant,
and action messages, plus Jinja2 environment and template loading.
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
    """
    A base class for all messages that have a `role` and carry structured
    `content`. Subclasses might be `Instruction`, `ActionRequest`, etc.
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
        """
        Extract structured image data from the message content if it is
        represented as a chat message array.

        Returns:
            list[dict[str,Any]] | None: If no images found, None.
        """
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]
        return None

    @property
    def chat_msg(self) -> dict[str, Any] | None:
        """
        A dictionary representation typically used in chat-based contexts.

        Returns:
            dict: `{"role": <role>, "content": <rendered content>}`
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
