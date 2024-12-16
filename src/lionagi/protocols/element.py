# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections import deque
from collections.abc import Generator
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import override

from lionagi._class_registry import LION_CLASS_REGISTRY, get_class
from lionagi.settings import Settings
from lionagi.utils import time

from .base import ID, IDError, IDType, Observable, T

__all__ = ("Element",)


class Element(BaseModel, Observable):
    """Base class in the Lion framework."""

    id: IDType = Field(
        default_factory=ID.generate,
        title="Lion ID",
        description="Unique identifier for the element",
        frozen=True,
    )

    timestamp: float = Field(
        default_factory=lambda: time(
            tz=Settings.Config.TIMEZONE, type_="timestamp"
        ),
        title="Creation Timestamp",
        frozen=True,
        alias="created",
    )

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize and register subclasses in the global class registry."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @property
    def created_datetime(self) -> datetime:
        """Get the creation datetime of the Element."""
        return datetime.fromtimestamp(
            self.timestamp, tz=Settings.Config.TIMEZONE
        )

    @field_validator("id", mode="before")
    def _validate_id(cls, value: IDType) -> IDType:
        try:
            return ID.get_id(value)
        except Exception:
            raise IDError(f"Invalid lion id: {value}")

    @field_validator("timestamp", mode="before")
    def _validate_timestamp(cls, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, datetime):
            return value.timestamp()
        try:
            if isinstance(value, str):
                try:
                    return float(value)
                except Exception:
                    return datetime.fromisoformat(value).timestamp()
            raise ValueError
        except Exception as e:
            raise ValueError(f"Invalid datetime string format: {value}") from e

    @override
    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> T:
        """create an instance of the Element or its subclass"""
        if "lion_class" in data:
            cls = get_class(class_name=data.pop("lion_class"))
        if cls.from_dict.__func__ != Element.from_dict.__func__:
            return cls.from_dict(data, **kwargs)
        return cls.model_validate(data, **kwargs)

    @override
    def to_dict(self, **kwargs: Any) -> dict:
        """Convert the Element to a dictionary representation."""
        dict_ = self.model_dump(**kwargs)
        dict_["lion_class"] = self.class_name()
        return dict_

    @override
    def __str__(self) -> str:
        timestamp_str = self.created_datetime.isoformat(timespec="minutes")
        return (
            f"{self.class_name()}(id={self.id[:6]}.., "
            f"timestamp={timestamp_str})"
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __bool__(self) -> bool:
        """Always True"""
        return True

    def __len__(self) -> int:
        """Return the length of the Element."""
        return 1


# File: lionagi/protocols/element.py
