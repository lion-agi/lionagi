# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
from collections.abc import Iterator
from typing import Any, Self

from pydantic import field_validator
from typing_extensions import override

from lionagi.core.typing import ID, Field, ItemNotFoundError, LnID, Ordering
from lionagi.libs.parse import to_list

from .element import Element
from .utils import to_list_type, validate_order


class Progression(Element, Ordering):
    """A flexible, ordered sequence container for Lion IDs.

    The Progression class provides an ordered sequence of Lion IDs with support
    for standard sequence operations, ID validation, and element containment
    checks. It maintains order while ensuring ID validity and uniqueness.

    Key Features:
        - Ordered sequence operations
        - ID validation and uniqueness
        - Element containment checks
        - Memory efficient storage
        - Slice operations

    Attributes:
        name (str | None): Optional name for the progression
        order (list[ID.ID]): Ordered list of Lion IDs
    """

    name: str | None = Field(
        None,
        title="Name",
        description="The name of the progression.",
    )

    order: list[ID.ID] = Field(
        default_factory=list,
        title="Order",
        description="The order of the progression.",
    )

    @field_validator("order", mode="before")
    def _validate_order(cls, value: ID.RefSeq) -> list[LnID]:
        if not value:
            return []
        try:
            return validate_order(value)
        except Exception as e:
            raise ValueError(f"Invalid order: {e}")

    def __contains__(self, item: ID.RefSeq | ID.Ref) -> bool:
        """Check if item(s) are in the progression."""
        if item is None or not self.order:
            return False

        item = to_list_type(item) if not isinstance(item, list) else item

        check = False
        for i in item:
            check = False
            if isinstance(i, str):
                check = i in self.order
            elif isinstance(i, Element):
                check = i.ln_id in self.order
            if not check:
                return False
        return check

    def __list__(self) -> list[LnID]:
        """Return a copy of the order."""
        return self.order[:]

    def __len__(self) -> int:
        """Get the length of the progression."""
        return len(self.order)

    def __getitem__(self, key: int | slice) -> ID.IDSeq:
        """Get an item or slice of items from the progression.

        Args:
            key: Integer index or slice object.

        Returns:
            Single ID for integer key, new Progression for slice.

        Raises:
            TypeError: If key is not int or slice.
            ItemNotFoundError: If index out of range.
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
                return self.__class__(order=a)
            else:
                return a
        except IndexError:
            raise ItemNotFoundError(f"index {key} item not found")

    def __setitem__(self, key: int | slice, value: ID.RefSeq) -> None:
        """Set an item or slice of items in the progression.

        Args:
            key: Integer index or slice object.
            value: Item(s) to set.
        """
        a = validate_order(value)
        self.order[key] = a if isinstance(key, int) else a
        self.order = to_list(self.order, flatten=True)

    def __delitem__(self, key: int | slice) -> None:
        """Delete an item or slice of items from the progression."""
        del self.order[key]

    def __iter__(self) -> Iterator[LnID]:
        """Iterate over the items in the progression."""
        return iter(self.order)

    def __next__(self) -> LnID:
        """Return the next item in the progression."""
        try:
            return next(iter(self.order))
        except StopIteration:
            raise StopIteration("No more items in the progression")

    def size(self) -> int:
        """Get the size of the progression."""
        return len(self)

    def clear(self) -> None:
        """Clear the progression."""
        self.order.clear()

    def append(self, item: ID.RefSeq, /) -> None:
        """Append an item to the end of the progression.

        Args:
            item: Item or sequence to append.
        """
        item_ = validate_order(item)
        self.order.extend(item_)

    def pop(self, index: int = None, /) -> str:
        """Remove and return an item from the progression.

        Args:
            index: Optional index to pop from. Default is last item.

        Returns:
            The removed item's ID.

        Raises:
            ItemNotFoundError: If progression is empty or index invalid.
        """
        try:
            if index is None:
                return self.order.pop()
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("pop index out of range") from e

    def include(self, item: ID.RefSeq, /) -> None:
        """Include item(s) in the progression if not already present.

        Args:
            item: Item or sequence to include.
        """
        item_ = validate_order(item)
        for i in item_:
            if i not in self.order:
                self.order.append(i)

    def exclude(self, item: int | ID.RefSeq, /) -> None:
        """Exclude an item or items from the progression.

        Args:
            item: Item or sequence to exclude.
        """
        for i in validate_order(item):
            while i in self:
                self.remove(i)

    def is_empty(self) -> bool:
        """Check if the progression is empty."""
        return not self.order

    def reverse(self) -> "Progression":
        """Return a reversed progression."""
        return self.__class__(order=list(reversed(self.order)), name=self.name)

    def __reverse__(self) -> "Progression":
        """Return a reversed progression."""
        return self.reverse()

    @override
    def __eq__(self, other: "Progression", /) -> bool:
        """Compare two Progression instances for equality."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(self, item: Any, /, start: int = 0, end: int = None) -> int:
        """Return the index of an item in the progression.

        Args:
            item: Item to find.
            start: Start index for search.
            end: Optional end index for search.

        Returns:
            Index of the item.

        Raises:
            ValueError: If item not found.
        """
        return (
            self.order.index(ID.get_id(item), start, end)
            if end
            else self.order.index(ID.get_id(item), start)
        )

    def remove(self, item: ID.RefSeq, /) -> None:
        """Remove the next occurrence of an item from the progression.

        Args:
            item: Item or sequence to remove.

        Raises:
            ItemNotFoundError: If item not found.
        """
        if item in self:
            item = validate_order(item)
            l_ = list(self.order)

            with contextlib.suppress(ValueError):
                for i in item:
                    l_.remove(i)
                self.order = l_
                return

        raise ItemNotFoundError(f"{item}")

    def popleft(self) -> str:
        """Remove and return the leftmost item from the progression.

        Returns:
            The first item's ID.

        Raises:
            ItemNotFoundError: If progression is empty.
        """
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError from e

    def extend(self, item: "Progression", /) -> None:
        """Extend the progression from the right with another progression.

        Args:
            item: Progression to extend with.

        Raises:
            TypeError: If item is not a Progression.
        """
        if not isinstance(item, Progression):
            raise TypeError(expected_type=Progression, actual_type=type(item))
        self.order.extend(item.order)

    def count(self, item: ID.Ref, /) -> int:
        """Return the number of occurrences of an item.

        Args:
            item: Item to count.

        Returns:
            Number of occurrences.
        """
        if not self.order or item not in self:
            return 0
        return self.order.count(ID.get_id(item))

    @override
    def __bool__(self) -> bool:
        """Check if the container is not empty."""
        return not self.is_empty()

    def __add__(self, other: ID.RefSeq) -> "Progression":
        """Returns a new progression with items added to the end.

        Args:
            other: Items to add.

        Returns:
            New Progression with added items.
        """
        other = validate_order(other)
        new_order = list(
            self.order
        )  # Create a new list to avoid modifying original
        new_order.extend(other)
        return self.__class__(order=new_order)

    def __radd__(self, other: ID.RefSeq) -> "Progression":
        """Reverse add operation."""
        return self + other

    def __iadd__(self, other: ID.RefSeq) -> Self:
        """Add an item to the end of the progression in-place."""
        self.append(other)
        return self

    def __isub__(self, other: ID.RefSeq) -> Self:
        """Remove an item from the progression in-place."""
        self.remove(other)
        return self

    def __sub__(self, other: ID.RefSeq) -> "Progression":
        """Remove an item or items from the progression.

        Args:
            other: Items to remove.

        Returns:
            New Progression with items removed.
        """
        other = validate_order(other)
        new_order = list(self)
        for i in other:
            new_order.remove(i)
        return self.__class__(order=new_order)

    @override
    def __repr__(self) -> str:
        return f"Progression({self.order})"

    @override
    def __str__(self) -> str:
        """Return a string representation of the progression."""
        if len(a := str(self.order)) > 50:
            a = a[:50] + "..."
        return f"Progression(name={self.name}, size={len(self)}, items={a})"

    def insert(self, index: int, item: ID.RefSeq, /) -> None:
        """Insert an item at the specified index.

        Args:
            index: Position to insert at.
            item: Item or sequence to insert.
        """
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, ID.get_id(i))

    def __hash__(self) -> int:
        return hash(self.ln_id)


def progression(
    order: ID.RefSeq = None,
    name: str = None,
    /,
) -> Progression:
    """Create a new Progression instance.

    Args:
        order: Initial order of items.
        name: Optional name for the progression.

    Returns:
        New Progression instance.
    """
    return Progression(order=order, name=name)
