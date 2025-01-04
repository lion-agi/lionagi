# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

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
            return {"role": str(self.role), "content": self.rendered}
        except Exception:
            return None

    @property
    def rendered(self) -> str:
        try:
            if isinstance(self.template, str):
                return self.template.format(**self.content)
            if isinstance(self.template, Template):
                return self.template.render(**self.content)
        except Exception:
            return json.dumps(self.content)

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError(
            "create method must be implemented in subclass"
        )

    @classmethod
    def from_dict(cls, dict_: dict):
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
        Check if the message is a clone of another message.

        Returns:
            bool: True if the message is a clone, False otherwise.
        """
        return self._flag == MessageFlag.MESSAGE_CLONE

    def clone(self, keep_role: bool = True) -> "RoledMessage":
        instance = self.__class__(
            content=self.content,
            role=self.role if keep_role else MessageRole.UNSET,
            metadata={"clone_from": self},
        )
        instance._flag = MessageFlag.MESSAGE_CLONE
        return instance

    def to_log(self) -> Log:
        """
        Convert the message to a Log object.

        Creates a Log instance containing the message content and additional
        information as loginfo.

        Returns:
            Log: A Log object representing the message.
        """
        return Log.create(self)

    @field_serializer("role")
    def _serialize_role(self, value: MessageRole):
        """
        Serialize the role for storage or transmission.

        Args:
            value: The MessageRole to serialize

        Returns:
            str: The string value of the role
        """
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
        if isinstance(value, Template):
            return None
        return value

    def update(self, sender, recipient, template, **kwargs):
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
