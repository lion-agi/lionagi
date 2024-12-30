# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime
from typing import Any, Self, TypeVar
from uuid import UUID, uuid4

import pandas as pd
from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from lionagi._class_registry import LION_CLASS_REGISTRY, get_class
from lionagi._errors import IDError
from lionagi.settings import Settings
from lionagi.utils import UNDEFINED, time

from .concepts import Observable

__all__ = (
    "Element",
    "IDType",
    "E",
    "Observable",
)


class IDType:

    def __init__(self, id: UUID4) -> None:
        self._id = id

    @classmethod
    def validate(cls, value: UUID4 | str) -> IDType:
        if isinstance(value, IDType):
            return value
        try:
            return cls(id=UUID(str(value), version=4))
        except ValueError:
            raise IDError("Invalid ID format.")

    @classmethod
    def create(cls) -> IDType:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self._id)

    def __repr__(self) -> str:
        return f"IDType({self._id})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IDType):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    __slots__ = ("_id",)


class Element(BaseModel, Observable):
    """Base class for all uniquely identifiable and timestamped elements."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: IDType = Field(default_factory=IDType.create)
    created_at: float = Field(
        default_factory=lambda: time(type_="timestamp"),
        description="Creation timestamp",
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Register subclass upon creation."""
        super().__pydantic_init_subclass__(**kwargs)
        LION_CLASS_REGISTRY[cls.__name__] = cls

    @field_serializer("id")
    def _serialize_id(self, id: IDType) -> str:
        return str(id)

    @field_validator("id", mode="before")
    def _validate_id(cls, value: Any) -> IDType:
        """Avoid unnecessary parsing if already UUID4."""
        return IDType.validate(value)

    @field_validator("created_at", mode="before")
    def _validate_created_at(cls, value: Any) -> float:
        if isinstance(value, datetime):
            return value.timestamp()

        if isinstance(value, int | float):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).timestamp()
            except Exception as e:
                try:
                    value = float(value)
                except Exception:
                    raise ValueError(
                        f"Invalid datetime string format: {value}"
                    ) from e

        try:
            return datetime.fromtimestamp(value, tz=Settings.Config.TIMEZONE)

        except Exception as e:
            raise ValueError(f"Invalid datetime string format: {value}") from e

    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(
            self.created_at, tz=Settings.Config.TIMEZONE
        )

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Element):
            return NotImplemented
        return self.id == other.id

    def __str__(self) -> str:
        return f"{self.class_name()}({self.id})"

    def to_pd_series(
        self, index=..., dtype=..., copy: bool = ...
    ) -> pd.Series:
        return pd.Series(
            self.model_dump(), index=index, dtype=dtype, copy=copy
        )

    __repr__ = __str__

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 1

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> dict:
        dict_ = self.model_dump()
        dict_["lion_class"] = self.class_name()
        dict_ = self.model_dump()
        dict_["lion_class"] = self.class_name()
        for k in list(dict_.keys()):
            if dict_[k] is UNDEFINED:
                dict_.pop(k)
        return dict_

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        lion_class = dict_.pop("lion_class", None)
        if lion_class and lion_class != cls.__name__:
            subcls = get_class(lion_class)
            # Only delegate if the subclass defines a custom from_dict
            if subcls.from_dict.__func__ != Element.from_dict.__func__:
                return subcls.from_dict(dict_)
        return cls.model_validate(dict_)

    def __hash__(self) -> int:
        return hash(self.id)


E = TypeVar("E", bound=Element)
