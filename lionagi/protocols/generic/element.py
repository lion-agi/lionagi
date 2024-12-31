# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Generic, TypeAlias, TypeVar
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from lionagi._class_registry import get_class
from lionagi.settings import Settings
from lionagi.utils import UNDEFINED, content_to_sha256, time, to_dict

from .._concepts import Collective, Observable, Ordering

__all__ = (
    "IDError",
    "IDType",
    "Element",
    "ID",
    "validate_order",
)


class IDError(Exception):
    pass


class IDType:
    """Represents a UUID4-based identifier."""

    __slots__ = ("_id",)

    def __init__(self, id: UUID):
        self._id = id

    @classmethod
    def validate(cls, value: str | UUID | IDType) -> IDType:
        if isinstance(value, IDType):
            return value
        try:
            return cls(UUID(str(value), version=4))
        except ValueError:
            raise IDError(f"Invalid ID: {value}")

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


class Element(BaseModel, Observable):
    """Basic identifiable, timestamped element."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
        extra="forbid",
    )

    id: IDType = Field(
        default_factory=IDType.create,
        title="ID",
        description="Unique identifier for this element.",
        frozen=True,
    )
    created_at: float = Field(
        default_factory=lambda: time(
            tz=Settings.Config.TIMEZONE, type_="timestamp"
        ),
        title="Creation Timestamp",
        description="Timestamp of element creation.",
        frozen=True,
    )
    metadata: dict = Field(
        default_factory=dict,
        title="Metadata",
        description="Additional data for this element.",
    )

    @field_validator("metadata", mode="before")
    def _validate_meta_integrity(cls, val: dict) -> dict:
        if not val:
            return {}
        if not isinstance(val, dict):
            val = to_dict(val, recursive=True, suppress=True)
        if "lion_class" in val and val["lion_class"] != cls.class_name(
            full=True
        ):
            raise ValueError("Metadata class mismatch.")
        if not isinstance(val, dict):
            raise ValueError("Invalid metadata.")
        return val

    @field_validator("created_at", mode="before")
    def _coerce_created_at(cls, val: float | datetime | None) -> float:
        if val is None:
            return float(datetime.now(timezone.utc).timestamp())
        if isinstance(val, float):
            return val
        if isinstance(val, datetime):
            return val.timestamp()
        try:
            return float(val)
        except Exception:
            raise ValueError(f"Invalid created_at: {val}")

    @field_validator("id", mode="before")
    def _ensure_idtype(cls, val: IDType | UUID | str) -> IDType:
        return IDType.validate(val)

    @field_serializer("id")
    def _serialize_id_type(self, val: IDType) -> str:
        return str(val)

    @field_serializer("metadata")
    def _serialize_metadata(self, val: dict) -> dict:
        dict_ = val.copy()
        dict_["lion_class"] = self.class_name(full=True)
        return dict_

    @property
    def content_sha256(self) -> str:
        return content_to_sha256(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Element):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __bool__(self) -> bool:
        return True

    @classmethod
    def class_name(cls, full: bool = False) -> str:
        if full:
            return str(cls).split("'")[1]
        return cls.__name__

    def to_dict(self) -> dict:
        dict_ = self.model_dump()
        dict_["metadata"]["content_sha256"] = self.content_sha256
        return {k: v for k, v in dict_.items() if v is not UNDEFINED}

    @classmethod
    def from_dict(cls, data: dict, /) -> Element:
        metadata = data.pop("metadata", {})
        if "lion_class" in metadata:
            subcls = metadata.pop("lion_class")
            if subcls != cls.class_name(full=True):
                try:
                    subcls = get_class(subcls.split(".")[-1])
                    if hasattr(subcls, "from_dict") and subcls is not cls:
                        return subcls.from_dict(data)

                except Exception:
                    from lionagi.libs.package.imports import import_module

                    mod, imp = subcls.rsplit(".", 1)
                    subcls = import_module(mod, import_name=imp)
                    data["metadata"] = metadata
                    if hasattr(subcls, "from_dict") and subcls is not cls:
                        return subcls.from_dict(data)
        return cls.model_validate(data)


def validate_order(order: Any) -> list[IDType]:
    """Validate and flatten an ordering into a list of IDType objects."""
    if isinstance(order, Element):
        return [order.id]
    if isinstance(order, Mapping):
        order = list(order.keys())

    stack = [order]
    out = []
    while stack:
        cur = stack.pop()
        if cur is None:
            continue
        if isinstance(cur, Element):
            out.append(cur.id)
        elif isinstance(cur, IDType):
            out.append(cur)
        elif isinstance(cur, UUID):
            out.append(IDType.validate(cur))
        elif isinstance(cur, str):
            out.append(IDType.validate(cur))
        elif isinstance(cur, (list, tuple, set)):
            stack.extend(reversed(cur))
        else:
            raise ValueError("Invalid item in order.")

    if not out:
        return []
    first_type = type(out[0])
    if first_type is IDType:
        for item in out:
            if not isinstance(item, IDType):
                raise ValueError("Mixed types in order.")
        return out
    raise ValueError("Unrecognized type(s) in order.")


E = TypeVar("E", bound=Element)


class ID(Generic[E]):
    """Utility for working with IDType."""

    ID: TypeAlias = IDType
    Item: TypeAlias = E | Element  # type: ignore
    Ref: TypeAlias = IDType | E | str  # type: ignore
    ItemSeq: TypeAlias = Sequence[E] | Collective[E]  # type: ignore
    RefSeq: TypeAlias = ItemSeq | Sequence[Ref] | Ordering[E]  # type: ignore

    @staticmethod
    def get_id(item: E) -> IDType:
        if isinstance(item, Element):
            return item.id
        if isinstance(item, (IDType, UUID, str)):
            return IDType.validate(item)
        raise ValueError("Cannot get ID from item.")

    @staticmethod
    def is_id(item: Any) -> bool:
        try:
            IDType.validate(item)
            return True
        except:
            return False


# File: protocols/generic/element.py
