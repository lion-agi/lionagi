# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import Field, field_serializer, field_validator
from typing_extensions import Self

from lionagi._errors import ItemNotFoundError

from .._concepts import Ordering
from .element import ID, Element, IDError, IDType, validate_order

E = TypeVar("E", bound=Element)


__all__ = (
    "Progression",
    "prog",
)


class Progression(Element, Ordering[E], Generic[E]):
    """Tracks an ordered sequence of item IDs, with optional naming.

    This class extends `Element` and implements `Ordering`, providing
    list-like operations for managing item IDs (based on `IDType`). It
    supports insertion, removal, slicing, and more. Items are stored in
    `order`, which is a simple list of IDs, and an optional `name`
    attribute can be assigned for identification.

    Attributes:
        order (list[ID[E].ID]):
            The sequence of item IDs representing the progression.
        name (str | None):
            An optional human-readable identifier for the progression.
    """

    order: list[ID[E].ID] = Field(
        default_factory=list,
        title="Order",
        description="A sequence of IDs representing the progression.",
    )
    name: str | None = Field(
        None,
        title="Name",
        description="A human-readable identifier for the progression.",
    )

    @field_validator("order", mode="before")
    def _validate_ordering(cls, value: Any) -> list[IDType]:
        """Ensures `order` is a valid list of IDTypes.

        Args:
            value (Any): Input sequence (could be elements, IDs, etc.).

        Returns:
            list[IDType]: The list of validated IDType objects.
        """
        return validate_order(value)

    @field_serializer("order")
    def _serialize_order(self, value: list[IDType]) -> list[str]:
        """Serializes IDs in `order` to string form.

        Args:
            value (list[IDType]): The order list of ID objects.

        Returns:
            list[str]: A list of stringified IDs.
        """
        return [str(x) for x in self.order]

    def __len__(self) -> int:
        """Returns the number of items in this progression."""
        return len(self.order)

    def __bool__(self) -> bool:
        """Indicates if this progression has any items."""
        return bool(self.order)

    def __contains__(self, item: Any) -> bool:
        """Checks if one or more IDs exist in the progression.

        Args:
            item (Any): Could be an `Element`, `IDType`, `UUID`, string,
                or a sequence of these.

        Returns:
            bool: True if all IDs in `item` exist in this progression;
                otherwise False.
        """
        try:
            refs = validate_order(item)
            return all(ref in self.order for ref in refs)
        except Exception:
            return False

    def __getitem__(self, key: int | slice) -> IDType | list[IDType]:
        """Gets one or more items by index or slice.

        Args:
            key (int | slice): The index or slice.

        Returns:
            IDType | list[IDType]:
                A single ID if `key` is an int; a new `Progression`
                if `key` is a slice.

        Raises:
            ItemNotFoundError: If the index or slice is invalid.
            TypeError: If `key` is neither an int nor a slice.
        """
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
                # Return a new Progression for slices
                return self.__class__(order=a)
            else:
                return a
        except IndexError:
            raise ItemNotFoundError(f"index {key} item not found")

    def __setitem__(self, key: int | slice, value: Any) -> None:
        """Sets items by index or slice.

        Args:
            key (int | slice):
                The position(s) to set.
            value (Any):
                One or more items to validate as IDs and assign.

        Raises:
            ValueError: If `value` can't be validated as IDs.
        """
        refs = validate_order(value)
        if isinstance(key, slice):
            self.order[key] = refs
        else:
            try:
                self.order[key] = refs[0]
            except IndexError:
                # If key is out of range, insertion occurs
                self.order.insert(key, refs[0])

    def __delitem__(self, key: int | slice) -> None:
        """Deletes item(s) by index or slice.

        Args:
            key (int | slice): The position(s) to delete.
        """
        del self.order[key]

    def __iter__(self):
        """Iterates over the IDs in this progression.

        Returns:
            Iterator[IDType]: An iterator over the ID elements.
        """
        return iter(self.order)

    def __next__(self) -> IDType:
        """Returns the next item if used as an iterator.

        Returns:
            IDType: The next item in the iteration.

        Raises:
            StopIteration: If there are no more items.
        """
        try:
            return next(iter(self.order))
        except StopIteration:
            raise StopIteration("No more items in the progression")

    def __list__(self) -> list[IDType]:
        """Returns a copy of all IDs in the progression.

        Returns:
            list[IDType]: A shallow copy of the ID list.
        """
        return self.order[:]

    def clear(self) -> None:
        """Removes all items from the progression."""
        self.order.clear()

    def include(self, item: Any, /) -> bool:
        """Adds new IDs at the end if they are not already present.

        Args:
            item (Any): Could be a single ID/Element or a list/tuple
                of them.

        Returns:
            bool: True if at least one new ID was appended; otherwise
                False.
        """
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
        """Removes occurrences of the specified IDs.

        Args:
            item (Any):
                Could be a single ID/Element or a list/tuple of them.

        Returns:
            bool: True if one or more items were removed; otherwise False.
        """
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
        """Appends one or more IDs at the end of the progression.

        Args:
            item (Any):
                A single ID/Element or multiple items.
        """
        if isinstance(item, Element):
            self.order.append(item.id)
            return
        refs = validate_order(item)
        self.order.extend(refs)

    def pop(self, index: int = -1) -> IDType:
        """Removes and returns one ID by index.

        Args:
            index (int):
                Position of the item to pop (default is the last item).

        Returns:
            IDType: The removed ID.

        Raises:
            ItemNotFoundError: If the index is invalid or out of range.
        """
        try:
            return self.order.pop(index)
        except Exception as e:
            raise ItemNotFoundError(str(e)) from e

    def popleft(self) -> IDType:
        """Removes and returns the first ID.

        Returns:
            IDType: The ID at the front of the progression.

        Raises:
            ItemNotFoundError: If the progression is empty.
        """
        if not self.order:
            raise ItemNotFoundError("No items in progression.")
        return self.order.pop(0)

    def remove(self, item: Any, /) -> None:
        """Removes the first occurrence of each specified ID.

        Args:
            item (Any):
                One or more IDs/Elements to remove.

        Raises:
            ItemNotFoundError:
                If any ID is not present in the progression.
        """
        try:
            refs = validate_order(item)
        except IDError:
            raise ItemNotFoundError("Invalid ID(s) provided.")

        if not refs:
            return
        missing = [r for r in refs if r not in self.order]
        if missing:
            raise ItemNotFoundError(str(missing))
        self.order = [x for x in self.order if x not in refs]

    def count(self, item: Any, /) -> int:
        """Counts the number of occurrences of an ID.

        Args:
            item (Any): An ID/Element to count.

        Returns:
            int: Number of times the ID occurs in the progression.
        """
        ref = ID.get_id(item)
        return self.order.count(ref)

    def index(self, item: Any, start: int = 0, end: int | None = None) -> int:
        """Finds the index of the first occurrence of an ID.

        Args:
            item (Any):
                The ID/Element whose index is sought.
            start (int):
                Starting index for the search.
            end (int | None):
                Ending index (non-inclusive) for the search.

        Returns:
            int: The index of the item.

        Raises:
            ValueError: If the item is not found in that range.
        """
        ref = ID.get_id(item)
        if end is not None:
            return self.order.index(ref, start, end)
        return self.order.index(ref, start)

    def extend(self, other: Progression) -> None:
        """Appends all IDs from another Progression to this one.

        Args:
            other (Progression): Another progression to merge.

        Raises:
            ValueError: If `other` is not a Progression.
        """
        if not isinstance(other, Progression):
            raise ValueError("Can only extend with another Progression.")
        self.order.extend(other.order)

    def __add__(self, other: Any) -> Progression[E]:
        """Returns a new Progression with IDs from both this and `other`.

        Args:
            other (Any):
                Item(s) that can be validated via `validate_order`.

        Returns:
            Progression[E]: A new progression with combined IDs.
        """
        new_refs = validate_order(other)
        return Progression(order=self.order + new_refs)

    def __radd__(self, other: Any) -> Progression[E]:
        """Returns a new Progression with IDs from `other` + this.

        Args:
            other (Any):
                Item(s) that can be validated via `validate_order`.

        Returns:
            Progression[E]: A new progression with combined IDs.
        """
        new_refs = validate_order(other)
        return Progression(order=new_refs + self.order)

    def __iadd__(self, other: Any) -> Self:
        """In-place addition of IDs.

        Args:
            other (Any): One or more items to append.

        Returns:
            Self: The updated progression.
        """
        self.append(other)
        return self

    def __sub__(self, other: Any) -> Progression[E]:
        """Returns a new Progression excluding specified IDs.

        Args:
            other (Any): One or more items to remove.

        Returns:
            Progression[E]: A new progression with the IDs removed.
        """
        refs = validate_order(other)
        remove_set = set(refs)
        new_order = [x for x in self.order if x not in remove_set]
        return Progression(order=new_order)

    def __isub__(self, other: Any) -> Self:
        """In-place exclusion of specified IDs.

        Args:
            other (Any):
                One or more items to remove.

        Returns:
            Self: The updated progression.
        """
        self.remove(other)
        return self

    def insert(self, index: int, item: ID.RefSeq, /) -> None:
        """Inserts one or more IDs at a specified index.

        Args:
            index (int): Position to insert at.
            item (ID.RefSeq):
                One or more items to validate as IDs and insert.
        """
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, ID.get_id(i))

    def __reverse__(self) -> Progression[E]:
        """Returns a new reversed Progression.

        Returns:
            Progression[E]: A reversed copy of the current progression.
        """
        return Progression(order=list(reversed(self.order)))

    def __eq__(self, other: object) -> bool:
        """Checks equality with another Progression.

        Args:
            other (object): Another progression to compare.

        Returns:
            bool: True if both `order` and `name` match; otherwise False.
        """
        if not isinstance(other, Progression):
            return NotImplemented
        return (self.order == other.order) and (self.name == other.name)

    def __gt__(self, other: Progression[E]) -> bool:
        """Compares if this progression is "greater" by ID order."""
        return self.order > other.order

    def __lt__(self, other: Progression[E]) -> bool:
        """Compares if this progression is "less" by ID order."""
        return self.order < other.order

    def __ge__(self, other: Progression[E]) -> bool:
        """Compares if this progression is >= the other by ID order."""
        return self.order >= other.order

    def __le__(self, other: Progression[E]) -> bool:
        """Compares if this progression is <= the other by ID order."""
        return self.order <= other.order

    def __repr__(self) -> str:
        """Returns a string representation of the progression.

        Returns:
            str: A formatted string showing name and order contents.
        """
        return f"Progression(name={self.name}, order={self.order})"


def prog(order: Any, name: str = None, /) -> Progression:
    """Convenience function to quickly create a new Progression.

    Args:
        order (Any):
            A sequence of IDs or items convertible to IDs via
            `validate_order`.
        name (str | None):
            An optional name for this progression.

    Returns:
        Progression: A new Progression instance with the given order
        and name.
    """
    return Progression(order=order, name=name)


# File: lionagi/protocols/generic/progression.py
