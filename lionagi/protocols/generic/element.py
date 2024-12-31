# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar, Union
from uuid import UUID, uuid4

from lionagi._class_registry import get_class

from .concepts import Observable

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


class Element(Observable):
    """Basic identifiable, timestamped element."""

    def __init__(
        self,
        id: IDType | str | None = None,
        created_at: float | datetime | None = None,
    ):
        self.id = IDType.create() if id is None else IDType.validate(id)
        self.created_at = self._coerce_created_at(created_at)

    def _coerce_created_at(self, val: float | datetime | None) -> float:
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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Element):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __bool__(self) -> bool:
        return True

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def to_dict(self) -> dict:
        """
        need to be json serializable
        """
        return {
            "lion_class": self.class_name(),
            "id": str(self.id),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, dict_: dict) -> Element:
        lion_class = dict_.pop("lion_class", None)
        if lion_class and lion_class != cls.__name__:
            subcls = get_class(lion_class)
            # Only delegate if the subclass defines a custom from_dict
            if subcls.from_dict.__func__ != Element.from_dict.__func__:
                return subcls.from_dict(dict_)
        return cls(**dict_)


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
