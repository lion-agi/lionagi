# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
import inspect
import os
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import Field, field_serializer, field_validator
from typing_extensions import override

from lionagi.utils import copy

from ..base import (
    Communicatable,
    IDType,
    MessageFlag,
    MessageRole,
    validate_sender_recipient,
)
from ..component import Component
from ..log import Log
from ..models import get_class

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(base_dir, "templates")
env = Environment(loader=FileSystemLoader(templates_path))


class RoledMessage(Component, Communicatable):
    """
    A base class representing a message with roles and properties.

    This class combines functionality from Component and BaseMail to create
    a versatile message object with role-based behavior. It serves as the
    foundation for all specific message types in the system.

    Attributes:
        content (dict): The content of the message, stored in a dict
        role (MessageRole): The role of the message in the conversation
            (system, user, or assistant)

    Example:
        >>> msg = RoledMessage(role=MessageRole.USER, content="Hello")
        >>> print(msg.role)
        MessageRole.USER
    """

    sender: IDType | MessageRole | MessageFlag = Field(
        default=MessageRole.UNSPECIFIED,
        title="Sender",
        description="The ID of the sender node or a role.",
    )

    recipient: IDType | MessageRole | MessageFlag = Field(
        default=MessageRole.UNSPECIFIED,
        title="Recipient",
        description="The ID of the recipient node or a role.",
    )

    content: dict = Field(
        default_factory=dict,
        description="The content of the message.",
    )

    role: MessageRole | None = Field(
        default=None,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

    @field_validator("sender", "recipient", mode="before")
    def _validate_sender_recipient(cls, value) -> IDType | MessageRole:
        return validate_sender_recipient(value)

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

    @field_validator("role")
    def _validate_role(cls, v: Any) -> MessageRole | None:

        if v in [r.value for r in MessageRole]:
            return MessageRole(v)
        raise ValueError(f"Invalid message role: {v}")

    def clone(self) -> "RoledMessage":
        """
        Creates a copy of the current RoledMessage object.

        Creates a new instance with the same attributes as the current one,
        but with a new identity. The original message is referenced in the
        clone's metadata.

        Returns:
            RoledMessage: A new instance with copied attributes.
        """
        cls = self.__class__
        signature = inspect.signature(cls.__init__)
        param_num = len(signature.parameters) - 2

        init_args = [MessageFlag.MESSAGE_CLONE] * param_num

        obj = cls(*init_args)
        obj.role = self.role
        obj.content = self.content
        obj.metadata.set("clone_from", self)

        return obj

    @override
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> "RoledMessage":
        """
        Loads a RoledMessage object from a dictionary.

        Creates a new instance from serialized data, handling both standard
        fields and any extra fields that might be present.

        Args:
            data: The dictionary containing the message data
            **kwargs: Additional keyword arguments to override data

        Returns:
            RoledMessage: An instance created from the dictionary
        """
        data = copy(data)
        if kwargs:
            data.update(kwargs)
        if "lion_class" in data:
            cls = get_class(data.pop("lion_class"))
        signature = inspect.signature(cls.__init__)
        param_num = len(signature.parameters) - 2

        init_args = [MessageFlag.MESSAGE_LOAD] * param_num

        extra_fields = {}
        for k, v in list(data.items()):
            if k not in cls.model_fields:
                extra_fields[k] = data.pop(k)

        obj = cls(*init_args, protected_init_params=data)

        for k, v in extra_fields.items():
            obj.add_field(name=k, value=v)

        metadata = data.get("metadata", {})
        last_updated = metadata.get("last_updated", None)
        if last_updated is not None:
            obj.metadata.set(["last_updated"], last_updated)
        return obj

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
        """
        Convert the message to a Log object.

        Creates a Log instance containing the message content and additional
        information as loginfo.

        Returns:
            Log: A Log object representing the message.
        """
        return Log(self)

    @field_serializer("content")
    def _serialize_content(self, value: dict) -> dict[str, Any]:

        output_dict = copy(value, deep=True)
        origin_obj = output_dict.pop("clone_from", None)

        if origin_obj and isinstance(origin_obj, RoledMessage):
            info_dict = {
                "clone_from_info": {
                    "original_id": origin_obj.id,
                    "original_timestamp": origin_obj.created_timestamp,
                    "original_sender": origin_obj.sender,
                    "original_recipient": origin_obj.recipient,
                }
            }
            output_dict.update(info_dict)
        return output_dict

    @field_serializer("role")
    def _serialize_role(self, value: MessageRole):
        """
        Serialize the role for storage or transmission.

        Args:
            value: The MessageRole to serialize

        Returns:
            str: The string value of the role
        """
        return value.value

    def _format_content(self) -> dict[str, Any]:
        raise NotImplementedError(
            "Method _format_content must be implemented."
        )
