"""Base module for logging in the Lion framework."""

from typing import Any

from lionabc import ImmutableRecord
from lionabc.exceptions import LionAccessError
from lionfuncs import to_dict
from pydantic import Field, PrivateAttr, field_serializer
from typing_extensions import Self

from lion_core.generic.element import Element
from lion_core.generic.note import Note


class Log(Element, ImmutableRecord):
    content: Note = Field(
        default_factory=Note,
        title="Log Content",
        description="The content of the log entry.",
    )

    loginfo: Note = Field(
        default_factory=Note,
        title="Log Info",
        description="Metadata about the log entry.",
    )

    _immutable: bool = PrivateAttr(False)

    def __init__(self, content: Note, loginfo: Note, **kwargs) -> None:
        super().__init__(**kwargs)
        self.content = self._validate_note(content)
        self.loginfo = self._validate_note(loginfo)

    @classmethod
    def _validate_load_data(cls, data: dict, /) -> dict:
        try:
            data["ln_id"] = data.pop("log_id")
            data["timestamp"] = data.pop("log_timestamp")
            data["lion_class"] = data.pop("log_class")
            return data
        except Exception as e:
            raise LionAccessError(
                "Log can only be loaded from a previously saved log entries.",
            ) from e

    @classmethod
    def from_dict(cls, data: dict, /) -> Self:
        data = cls._validate_load_data(data)
        self = cls(**data)
        self._immutable = True
        return self

    def __setattr__(self, name: str, value: Any, /) -> None:
        if self._immutable:
            raise AttributeError("Cannot modify immutable log entry.")
        super().__setattr__(name, value)

    def _validate_note(cls, value: Any, /) -> Note:
        if not value:
            return Note()
        if isinstance(value, Note):
            return value
        if isinstance(value, dict):
            return Note(**value)
        try:
            return Note(**to_dict(value))
        except Exception as e:
            raise e

    @field_serializer("content", "loginfo")
    def _serialize_note(self, value: Note) -> dict:
        return value.to_dict()

    def to_dict(self) -> dict:
        dict_ = super().to_dict()
        dict_["log_id"] = dict_.pop("ln_id")
        dict_["log_class"] = dict_.pop("lion_class")
        dict_["log_timestamp"] = dict_.pop("timestamp")
        return dict_

    def to_note(self) -> Note:
        return Note(**self.to_dict())


__all__ = ["Log"]
# File: lion_core/generic/log.py
