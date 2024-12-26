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

__all__ = ("Element", "IDType", "E")


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
            raise ValueError("Value must be a UUID4 or a valid UUID4 string.")

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


class Element(BaseModel):
    """Base class for all uniquely identifiable and timestamped elements."""

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: IDType = Field(default_factory=IDType.create)
    created_at: datetime = Field(default_factory=datetime.now)

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

    @field_serializer("created_at")
    def _serialize_created_at(self, created_at: datetime) -> str:
        return created_at.isoformat()

    @field_validator("created_at", mode="before")
    def _validate_created_at(cls, value: datetime | str) -> datetime:
        """Skip parsing if it's already a datetime."""
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

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


E = TypeVar("E", bound=Element)
