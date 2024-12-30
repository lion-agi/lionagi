# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Generic, Self

from pydantic import Field, field_serializer, field_validator

from lionagi._errors import ItemNotFoundError

from ._id import ID, Ordering, validate_order
from .element import E, Element, IDType

__all__ = ("Progression",)


class Progression(Element, Ordering, Generic[E]):
    """An ordered sequence of element IDs with progression operations.

    This class manages an ordered sequence of element IDs with methods for
    manipulation and comparison. It supports both single IDs and sequences
    of IDs.

    Attributes:
        name (str | None): An optional identifier for the progression.
        order (list[IDType]): A list of element IDs in sequence.
    """

    name: str | None = Field(default=None)
    order: list[IDType] = Field(default_factory=list)

    @field_validator("order", mode="before")
    def _validate_order(cls, order: Any) -> list[IDType]:
        """Validate the `order` field as a list of valid IDType objects.

        Args:
            order (Any):
                The raw order data to validate.

        Returns:
            list[IDType]: A list of valid IDType objects.
        """
        return validate_order(order)

    @field_serializer("order")
    def _serialize_order(self, order: list[IDType]) -> list[str]:
        """Serialize the `order` field to a list of string representations.

        Args:
            order (list[IDType]):
                A list of valid IDType objects.

        Returns:
            list[str]: A list of string representations of the IDs.
        """
        return [str(item) for item in order]

    @classmethod
    def create(cls, order: Any, name: str = None) -> Self:
        """Create a new Progression instance.

        Args:
            order (Any):
                An object (or sequence of objects) that can be validated
                into a list of IDType objects.
            name (str | None):
                Optional identifier for the progression.

        Returns:
            Self: A new Progression instance.
        """
        return cls(order=order, name=name)

    def __len__(self) -> int:
        """Return the number of items in the progression."""
        return len(self.order)

    def __bool__(self) -> bool:
        """Return True if the progression contains any items."""
        return bool(self.order)

    def __contains__(self, item: Any) -> bool:
        """Check if item(s) exist in the progression.

        Args:
            item (Any):
                A single item or a sequence of items to check.

        Returns:
            bool: True if all items exist in the progression, False otherwise.
        """
        try:
            item_list = validate_order(item)
            order_set = set(self.order)
            return all(ref in order_set for ref in item_list)
        except Exception:
            return False

    def __getitem__(self, key: int | slice) -> IDType | list[IDType]:
        """Get the item(s) at the specified index or slice.

        Args:
            key (int | slice):
                The index or slice specifying the requested item(s).

        Returns:
            IDType | list[IDType]:
                A single IDType if `key` is an integer, or a list of
                IDType objects if `key` is a slice.

        Raises:
            ItemNotFoundError: If the index or slice is invalid.
        """
        try:
            return self.order[key]
        except Exception as e:
            raise ItemNotFoundError(f"{key}") from e

    def __setitem__(self, key: int | slice, value: Any) -> None:
        """Set the item(s) at the specified index or slice.

        Args:
            key (int | slice):
                The index or slice specifying the position.
            value (Any):
                The new item(s) to set.
        """
        value_list = validate_order(value)
        if isinstance(key, slice):
            self.order[key] = value_list
        else:
            self.order[key] = value_list[0]

    def __delitem__(self, key: int | slice) -> None:
        """Remove the item(s) at the specified index or slice.

        Args:
            key (int | slice):
                The index or slice specifying the item(s) to remove.
        """
        del self.order[key]

    def __iter__(self) -> Any:
        """Iterate over items in the progression.

        Yields:
            IDType: Each ID in the progression.
        """
        return iter(self.order)

    def __next__(self) -> IDType:
        """Get the next item in the progression.

        Returns:
            IDType: The next ID in the progression.

        Raises:
            StopIteration: If no more items remain.
        """
        return next(iter(self))

    def include(self, item: Any, /) -> bool:
        """Add items to the end of the progression if they are not present.

        Args:
            item (Any):
                A single item or a sequence of items to include.

        Returns:
            bool: True if at least one new item was added, False otherwise.
        """
        try:
            items = validate_order(item)
        except ValueError:
            return False

        if not items:
            return True

        order_set = set(self.order)
        appended = False
        for ref in items:
            if ref not in order_set:
                self.order.append(ref)
                order_set.add(ref)
                appended = True
        return appended

    def exclude(self, item: Any, /) -> bool:
        """Remove all occurrences of specified items from the progression.

        Args:
            item (Any):
                A single item or sequence of items to remove.

        Returns:
            bool: True if any item was removed, False otherwise.
        """
        try:
            items = validate_order(item)
        except ValueError:
            return False
        if not items:
            return True

        remove_set = set(items)
        original_len = len(self.order)
        self.order = [x for x in self.order if x not in remove_set]
        return len(self.order) < original_len

    def append(self, item: Any, /) -> None:
        """Append item(s) to the end of the progression.

        Args:
            item (Any):
                A single item or sequence of items to append.

        Raises:
            ValueError: If validation fails.
        """
        if isinstance(item, Element):
            self.order.append(item.id)
            return
        items = validate_order(item)
        self.order.extend(items)

    def pop(self, index: int = -1) -> IDType:
        """Remove and return the item at the given index.

        Args:
            index (int, optional):
                The index to pop from. Defaults to -1 (the last item).

        Returns:
            IDType: The ID that was removed.

        Raises:
            ItemNotFoundError: If the index is out of range.
        """
        try:
            return self.order.pop(index)
        except Exception as e:
            raise ItemNotFoundError(f"{index}") from e

    def popleft(self) -> IDType:
        """Remove and return the first item in the progression.

        Returns:
            IDType: The ID that was removed.

        Raises:
            ItemNotFoundError: If the progression is empty.
        """
        try:
            return self.order.pop(0)
        except Exception as e:
            raise ItemNotFoundError(
                "Cannot pop from empty progression."
            ) from e

    def __reverse__(self) -> Progression:
        """Return a new Progression with the order reversed.

        Returns:
            Progression: A new reversed Progression instance.
        """
        return self.__class__(order=list(reversed(self.order)), name=self.name)

    def __eq__(self, other: Progression) -> bool:
        """Check if two Progressions are equal by comparing `order` and `name`."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(self, item: Any, /, start: int = 0, end: int = None) -> int:
        """Find the index of an item in the progression.

        Args:
            item (Any):
                The item to locate.
            start (int, optional):
                Start index for the search. Defaults to 0.
            end (int | None, optional):
                End index for the search (non-inclusive).
                Defaults to None (search entire list).

        Returns:
            int: The index of the item in the progression.

        Raises:
            ValueError: If the item is not found.
        """
        ref = ID.get_id(item)
        if end is not None:
            return self.order.index(ref, start, end)
        return self.order.index(ref, start)

    def remove(self, item: Any, /) -> None:
        """Remove the first occurrence of each item.

        Args:
            item (Any):
                A single item or sequence of items to remove.

        Raises:
            ItemNotFoundError: If any item is not found in the progression.
        """
        try:
            items = validate_order(item)
        except Exception as e:
            raise ItemNotFoundError(f"{item}") from e
        if not items:
            return

        order_set = set(self.order)
        if any(ref not in order_set for ref in items):
            raise ItemNotFoundError(f"{items}")

        remove_set = set(items)
        self.order = [x for x in self.order if x not in remove_set]

    def count(self, item: Any, /) -> int:
        """Return the number of occurrences of an item.

        Args:
            item (Any):
                The item to count.

        Returns:
            int: The number of occurrences of the item in the progression.
        """
        ref = ID.get_id(item)
        return self.order.count(ref)

    def extend(self, other: Progression) -> None:
        """Add the items from another progression to the end of this one.

        Args:
            other (Progression):
                Another Progression instance.

        Raises:
            ValueError: If the argument is not a Progression.
        """
        if not isinstance(other, Progression):
            raise ValueError(
                "Can only extend with another Progression instance."
            )
        self.order.extend(other.order)

    def __add__(self, other: Any) -> Progression:
        """Return a new Progression with concatenated items.

        Args:
            other (Any):
                A single item or sequence of items to be concatenated.

        Returns:
            Progression: A new Progression instance containing
            concatenated items.
        """
        items = validate_order(other)
        return self.__class__(order=self.order + items, name=self.name)

    def __radd__(self, other: Any) -> Progression:
        """Return a new Progression with other items followed by this one.

        Args:
            other (Any):
                A single item or sequence of items to prepend.

        Returns:
            Progression: A new Progression instance.
        """
        items = validate_order(other)
        return self.__class__(order=items + self.order, name=self.name)

    def __iadd__(self, other: Any) -> Self:
        """In-place addition of item(s).

        Args:
            other (Any):
                A single item or sequence of items to append.

        Returns:
            Self: The updated Progression instance.
        """
        self.append(other)
        return self

    def __sub__(self, other: Any) -> Progression:
        """Return a new Progression excluding specified item(s).

        Args:
            other (Any):
                A single item or sequence of items to exclude.

        Returns:
            Progression: A new Progression with items removed.
        """
        items = validate_order(other)
        remove_set = set(items)
        new_order = [x for x in self.order if x not in remove_set]
        return self.__class__(order=new_order, name=self.name)

    def __isub__(self, other: Any) -> Self:
        """In-place subtraction (removal) of item(s).

        Args:
            other (Any):
                A single item or sequence of items to remove.

        Returns:
            Self: The updated Progression instance.
        """
        self.remove(other)
        return self

    def __str__(self) -> str:
        """str: A string representation of the Progression."""
        return f"Progression({self.order})"

    def __gt__(self, other: Progression) -> bool:
        """bool: Compare this progression to another by their `order`."""
        return self.order > other.order

    def __lt__(self, other: Progression) -> bool:
        """bool: Compare this progression to another by their `order`."""
        return self.order < other.order

    def __ge__(self, other: Progression) -> bool:
        """bool: Compare this progression to another by their `order`."""
        return self.order >= other.order

    def __le__(self, other: Progression) -> bool:
        """bool: Compare this progression to another by their `order`."""
        return self.order <= other.order

    def insert(self, index: int, item: Any, /) -> None:
        """Insert item(s) at the specified index.

        Args:
            index (int):
                The position at which to insert.
            item (Any):
                The item(s) to insert.
        """
        items = validate_order(item)
        self.order[index:index] = items

    def __list__(self) -> list[IDType]:
        """Convert the progression to a list of IDs.

        Returns:
            list[IDType]: A shallow copy of the progression's ID list.
        """
        return self.order[:]

    def clear(self) -> None:
        """Remove all items from the progression."""
        self.order.clear()

    __repr__ = __str__


def prog(order: Any, name: str = None, /) -> Progression:
    """Create a new Progression with the given order and optional name.

    Args:
        order (Any):
            A single item or sequence of items that can be validated
            into a list of IDType objects.
        name (str | None):
            An optional identifier for the progression.

    Returns:
        Progression: A new Progression instance.
    """
    return Progression.create(order=order, name=name)
