# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from typing import Any, Self

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import Field, PrivateAttr, field_serializer, field_validator
from typing_extensions import override

from lionagi._class_registry import get_class
from lionagi.protocols.types import (
    ID,
    Component,
    Element,
    IDType,
    Log,
    MessageFlag,
    MessageRole,
    Sendable,
    validate_sender_recipient,
)
from lionagi.utils import to_dict

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(base_dir, "templates")
env = Environment(loader=FileSystemLoader(templates_path))


__all__ = ("RoledMessage",)


class RoledMessage(Component, Sendable):

    sender: ID.SenderRecipient = Field(
        default=MessageRole.UNSPECIFIED,
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: ID.SenderRecipient = Field(
        default=MessageRole.UNSPECIFIED,
        title="Recipient",
        description="The ID of the recipient node or a role.",
    )

    content: dict = Field(
        default_factory=dict,
        description="The content of the message.",
    )

    role: MessageRole = Field(
        default=MessageRole.UNSPECIFIED,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

    _immutable: bool = PrivateAttr(
        False, description="Whether the message is immutable"
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value) -> ID.SenderRecipient:
        return validate_sender_recipient(value)

    @field_serializer("sender", "recipient")
    def _serialize_sender_recipient(self, value: ID.SenderRecipient) -> str:
        if isinstance(value, IDType):
            return str(value)
        if isinstance(value, Element):
            return str(value.id)
        if isinstance(value, MessageRole | MessageFlag):
            return value.value

    @field_validator("role")
    def _validate_role(cls, v: Any) -> MessageRole | None:

        if v in [r.value for r in MessageRole]:
            return MessageRole(v)
        raise ValueError(f"Invalid message role: {v}")

    @field_serializer("role")
    def _serialize_role(self, value: MessageRole):
        return value.value

    @field_validator("content", mode="before")
    def _validate_content(cls, value: Any) -> dict:
        return to_dict(value, suppress=True, fuzzy_parse=True)

    @property
    def image_content(self) -> list[dict[str, Any]] | None:
        """
        Return image content if present in the message.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of image content
                dictionaries, or None if no images are present.
        """
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]
        return None

    @property
    def chat_msg(self) -> dict[str, Any] | None:
        """
        Return message in chat representation format.

        Returns:
            Optional[Dict[str, Any]]: The message formatted for chat use,
                or None if formatting fails.
        """
        try:

            return self._format_content()
        except Exception:
            return None

    @property
    def rendered(self) -> str:
        """
        Render the message content using the template.

        Returns:
            str: The rendered message content.
        """
        if self.template:
            return self.template.render(self.content)
        return str(self.content)

    def clone(self) -> RoledMessage:
        """
        Creates a copy of the current RoledMessage object.

        Creates a new instance with the same attributes as the current one,
        but with a new identity. The original message is referenced in the
        clone's metadata.

        Returns:
            RoledMessage: A new instance with copied attributes.
        """

        original_info = self.to_dict()
        for i in ["role", "content", "metadata", "template"]:
            original_info.pop(i)

        params = {
            "template": self.template,
            "role": self.role,
            "sender": MessageFlag.MESSAGE_CLONE,
            "recipient": MessageFlag.MESSAGE_CLONE,
            "content": self.content,
            "metadata": {
                "clone_from": original_info,
            },
        }

        return self.from_dict(params)

    @override
    @classmethod
    def from_dict(cls, data: dict, /) -> Self:
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))

        if any(i not in data for i in cls.model_fields):
            raise ValueError(
                "Invalid RoledMessage data, must come from RoledMessage.to_dict()"
            )

        if cls.class_name() != "RoledMessage":
            self = cls.model_validate(data)
            self._immutable = True
            return self
        raise NotImplementedError(
            "Method from_dict only implemented for subclasses of RoledMessage."
        )

    @override
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

    def to_log(self) -> Log:
        return Log.create(self)

    def _format_content(self) -> dict[str, Any]:
        raise NotImplementedError(
            "Method _format_content must be implemented."
        )
