import inspect
from enum import Enum
from typing import Any

from lionabc import Relational
from lionfuncs import copy
from pydantic import Field, field_validator
from typing_extensions import override

from lion_core._class_registry import get_class
from lion_core.communication.base_mail import BaseMail
from lion_core.generic.component import Component
from lion_core.generic.log import Log
from lion_core.generic.note import Note


class MessageField(str, Enum):
    """Enum to store message fields for consistent referencing."""

    LION_ID = "lion_id"
    TIMESTAMP = "timestamp"
    ROLE = "role"
    SENDER = "sender"
    RECIPIENT = "recipient"
    CONTENT = "content"


class MessageRole(str, Enum):
    """Enum for possible roles a message can assume in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageFlag(str, Enum):
    """Enum to signal constructing a clone Message"""

    MESSAGE_CLONE = "MESSAGE_CLONE"
    MESSAGE_LOAD = "MESSAGE_LOAD"


class RoledMessage(Relational, Component, BaseMail):
    """A base class representing a message with roles and properties."""

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
        """Return image content if present in the message."""
        msg_ = self.chat_msg
        if isinstance(msg_, dict) and isinstance(msg_["content"], list):
            return [i for i in msg_["content"] if i["type"] == "image_url"]
        return None

    @property
    def chat_msg(self) -> dict[str, Any] | None:
        """Return message in chat representation."""
        try:
            return self._format_content()
        except Exception:
            return None

    @field_validator("role")
    def _validate_role(cls, v: Any) -> MessageRole | None:
        """Validates the role of the message."""
        if v in [r.value for r in MessageRole]:
            return MessageRole(v)
        raise ValueError(f"Invalid message role: {v}")

    def _format_content(self) -> dict[str, Any]:
        """Format the message content for chat representation."""
        if self.content.get("images", None):
            content = self.content.to_dict()
        else:
            content = str(self.content.to_dict())
        return {"role": self.role.value, "content": content}

    def clone(self) -> "RoledMessage":
        """Creates a copy of the current RoledMessage object."""
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
        """Loads a RoledMessage object from a dictionary."""
        data = copy(data)
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
        """Provides a string representation of the message."""
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
        dict_ = self.to_dict()
        content = dict_.pop("content")
        _log = Log(
            content=content,
            loginfo=dict_,
        )
        return _log


# File: lion_core/communication/message.py
