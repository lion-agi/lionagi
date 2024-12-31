# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Generic, Self, TypeVar

from pydantic import Field, field_serializer, field_validator

from lionagi._errors import ItemNotFoundError

from .._concepts import Ordering
from .element import ID, Element, IDType, validate_order

E = TypeVar("E", bound=Element)


__all__ = (
    "Progression",
    "prog",
)


class Progression(Element, Ordering[E], Generic[E]):

    order: list[ID[E].ID] = Field(
        default_factory=list,
        title="Order",
        description="A sequence of IDs representing the progression.",
    )
    name: str | None = Field(
        None,
        title="Name",
        description="An optional human readable identifier for the progression.",
    )

    @field_validator("order", mode="before")
    def _validate_ordering(cls, value: Any) -> list[IDType]:
        return validate_order(value)

    @field_serializer("order")
    def _serialize_order(self, value: list[IDType]) -> list[str]:
        return [str(x) for x in self.order]

    def __len__(self) -> int:
        return len(self.order)

    def __bool__(self) -> bool:
        return bool(self.order)

    def __contains__(self, item: Any) -> bool:
        """Check if one or more IDs exist in the progression."""
        try:
            refs = validate_order(item)
            return all(ref in self.order for ref in refs)
        except Exception:
            return False

    def __getitem__(self, key: int | slice) -> IDType | list[IDType]:
        """Return one ID or a list of IDs at the given index or slice."""
        if not isinstance(key, (int, slice)):
            key_cls = key.__class__.__name__
            raise TypeError(
                f"indices must be integers or slices, not {key_cls}"
            )
        try:
            a = self.order[key]
            if not a:
                raise ItemNotFoundError(f"index {key} item not found")
            if isinstance(key, slice):
                return self.__class__(order=a)
            else:
                return a
        except IndexError:
            raise ItemNotFoundError(f"index {key} item not found")

    def __setitem__(self, key: int | slice, value: Any) -> None:
        refs = validate_order(value)
        if isinstance(key, slice):
            self.order[key] = refs
        else:
            try:
                self.order[key] = refs[0]
            except IndexError:
                self.order.insert(key, refs[0])

    def __delitem__(self, key: int | slice) -> None:
        del self.order[key]

    def __iter__(self):
        return iter(self.order)

    def __next__(self) -> IDType:
        """Return the next item in the progression."""
        try:
            return next(iter(self.order))
        except StopIteration:
            raise StopIteration("No more items in the progression")

    def __list__(self) -> list[IDType]:
        """Return a shallow copy of all IDs in the progression."""
        return self.order[:]

    def clear(self) -> None:
        """Remove all items."""
        self.order.clear()

    def include(self, item: Any, /) -> bool:
        """Add new IDs at the end if they aren't already present."""
        try:
            refs = validate_order(item)
        except ValueError:
            return False
        if not refs:
            return True

        existing = set(self.order)
        appended = False
        for ref in refs:
            if ref not in existing:
                self.order.append(ref)
                existing.add(ref)
                appended = True
        return appended

    def exclude(self, item: Any, /) -> bool:
        """Remove occurrences of specified IDs."""
        try:
            refs = validate_order(item)
        except ValueError:
            return False
        if not refs:
            return True

        before = len(self.order)
        rset = set(refs)
        self.order = [x for x in self.order if x not in rset]
        return len(self.order) < before

    def append(self, item: Any, /) -> None:
        """Append one or more IDs at the end."""
        if isinstance(item, Element):
            self.order.append(item.id)
            return
        refs = validate_order(item)
        self.order.extend(refs)

    def pop(self, index: int = -1) -> IDType:
        """Remove and return one ID by index."""
        try:
            return self.order.pop(index)
        except Exception as e:
            raise ItemNotFoundError(str(e)) from e

    def popleft(self) -> IDType:
        """Remove and return the first ID."""
        if not self.order:
            raise ItemNotFoundError("No items in progression.")
        return self.order.pop(0)

    def remove(self, item: Any, /) -> None:
        """Remove the first occurrence of each specified ID."""
        refs = validate_order(item)
        if not refs:
            return
        missing = [r for r in refs if r not in self.order]
        if missing:
            raise ItemNotFoundError(str(missing))
        self.order = [x for x in self.order if x not in refs]

    def count(self, item: Any, /) -> int:
        ref = ID.get_id(item)
        return self.order.count(ref)

    def index(self, item: Any, start: int = 0, end: int | None = None) -> int:
        """Get the index of the first occurrence of an ID."""
        ref = ID.get_id(item)
        if end is not None:
            return self.order.index(ref, start, end)
        return self.order.index(ref, start)

    def extend(self, other: Progression) -> None:
        """Append IDs from another Progression."""
        if not isinstance(other, Progression):
            raise ValueError("Can only extend with another Progression.")
        self.order.extend(other.order)

    def __add__(self, other: Any) -> Progression[E]:
        """Return a new Progression combining this + other."""
        new_refs = validate_order(other)
        return Progression(order=self.order + new_refs)

    def __radd__(self, other: Any) -> Progression[E]:
        """Return a new Progression combining other + this."""
        new_refs = validate_order(other)
        return Progression(order=new_refs + self.order)

    def __iadd__(self, other: Any) -> Self:
        """In-place addition of IDs."""
        self.append(other)
        return self

    def __sub__(self, other: Any) -> Progression[E]:
        """Return a new Progression excluding specified IDs."""
        refs = validate_order(other)
        remove_set = set(refs)
        new_order = [x for x in self.order if x not in remove_set]
        return Progression(order=new_order)

    def __isub__(self, other: Any) -> Self:
        """In-place exclusion of IDs."""
        self.remove(other)
        return self

    def insert(self, index: int, item: ID.RefSeq, /) -> None:
        """Insert an item at the specified index.

        Args:
            index: Position to insert at.
            item: Item or sequence to insert.
        """
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, ID.get_id(i))

    def __reverse__(self) -> Progression[E]:
        """Return a new reversed Progression."""
        return Progression(order=list(reversed(self.order)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Progression):
            return NotImplemented
        return (self.order == other.order) and (self.name == other.name)

    def __gt__(self, other: Progression[E]) -> bool:
        return self.order > other.order

    def __lt__(self, other: Progression[E]) -> bool:
        return self.order < other.order

    def __ge__(self, other: Progression[E]) -> bool:
        return self.order >= other.order

    def __le__(self, other: Progression[E]) -> bool:
        return self.order <= other.order

    def __repr__(self) -> str:
        return f"Progression(name={self.name}, order={self.order})"


def prog(order: Any, name: str = None, /) -> Progression:
    """Convenience function to quickly create a new Progression."""
    return Progression(order=order, name=name)


# File: protocols/generic/progression.py
