# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import inspect

from lionagi.core._class_registry import get_class
from lionagi.core.generic.types import Component, Log
from lionagi.core.typing import (
    Any,
    Communicatable,
    Enum,
    Field,
    Note,
    field_serializer,
    field_validator,
    override,
)
from lionagi.libs.utils import copy

from .base_mail import BaseMail


class MessageRole(str, Enum):
    """
    Enum for possible roles a message can assume in a conversation.

    These roles define the nature and purpose of messages in the system:
    - SYSTEM: System-level messages providing context or instructions
    - USER: Messages from users making requests or providing input
    - ASSISTANT: Messages from AI assistants providing responses
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageFlag(str, Enum):
    """
    Enum to signal special message construction modes.

    These flags are used internally to control message instantiation:
    - MESSAGE_CLONE: Signal to create a clone of an existing message
    - MESSAGE_LOAD: Signal to load a message from stored data
    """

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class MessageField(str, Enum):
    """
    Enum for standard message fields.

    Defines the standard fields that can be present in a message:
    - TIMESTAMP: Message creation timestamp
    - LION_CLASS: Class identifier for LION system
    - ROLE: Message role (system/user/assistant)
    - CONTENT: Message content
    - ln_id: Unique message identifier
    - SENDER: Message sender
    - RECIPIENT: Message recipient
    - METADATA: Additional message metadata
    """

    TIMESTAMP = "timestamp"
    LION_CLASS = "lion_class"
    ROLE = "role"
    CONTENT = "content"
    ln_id = "ln_id"
    SENDER = "sender"
    RECIPIENT = "recipient"
    METADATA = "metadata"


MESSAGE_FIELDS = [i.value for i in MessageField.__members__.values()]


class RoledMessage(Component, BaseMail):
    """
    A base class representing a message with roles and properties.

    This class combines functionality from Component and BaseMail to create
    a versatile message object with role-based behavior. It serves as the
    foundation for all specific message types in the system.

    Attributes:
        content (Note): The content of the message, stored in a Note object
        role (MessageRole): The role of the message in the conversation
            (system, user, or assistant)

    Example:
        >>> msg = RoledMessage(role=MessageRole.USER, content="Hello")
        >>> print(msg.role)
        MessageRole.USER
    """

    content: Note = Field(
        default_factory=Note,
        description="The content of the message.",
    )

    role: MessageRole | None = Field(
        default=None,
        description="The role of the message in the conversation.",
        examples=["system", "user", "assistant"],
    )

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
        dict_ = self.to_dict()
        content = dict_.pop("content")
        _log = Log(
            content=content,
            loginfo=dict_,
        )
        return _log

    @field_serializer("content")
    def _serialize_content(self, value: Note) -> dict[str, Any]:

        output_dict = copy(value.content, deep=True)
        origin_obj = output_dict.pop("clone_from", None)

        if origin_obj and isinstance(origin_obj, Communicatable):
            info_dict = {
                "clone_from_info": {
                    "original_ln_id": origin_obj.ln_id,
                    "original_timestamp": origin_obj.timestamp,
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
        """
        Format the message content for chat representation.

        Handles both text and image content appropriately.

        Returns:
            dict[str, Any]: The formatted content with role and content fields
        """
        if self.content.get("images", None):
            content = self.content.to_dict()
        else:
            content = str(self.content.to_dict())
        return {"role": self.role.value, "content": content}
