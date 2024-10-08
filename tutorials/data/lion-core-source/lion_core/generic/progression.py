import contextlib
from collections.abc import Iterator
from typing import Any

from lionabc import Ordering
from lionabc.exceptions import ItemNotFoundError, LionTypeError
from lionfuncs import to_list
from pydantic import Field, field_validator
from typing_extensions import override

from lion_core.generic.element import Element
from lion_core.generic.utils import to_list_type, validate_order
from lion_core.sys_utils import SysUtil


class Progression(Element, Ordering):
    """A flexible, ordered sequence container for Lion IDs."""

    name: str | None = Field(
        None,
        title="Name",
        description="The name of the progression.",
    )

    order: list[str] = Field(
        default_factory=list,
        title="Order",
        description="The order of the progression.",
    )

    @field_validator("order", mode="before")
    def _validate_order(cls, value):
        return validate_order(value)

    def __contains__(self, item: Any) -> bool:
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

    def __list__(self) -> list[str]:
        """Return a copy of the order."""
        return self.order[:]

    def __len__(self) -> int:
        """Get the length of the progression."""
        return len(self.order)

    def __getitem__(self, key: int | slice) -> str | list[str]:
        """Get an item or slice of items from the progression."""
        if not isinstance(key, int | slice):
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
        """Set an item or slice of items in the progression."""
        a = validate_order(value)
        self.order[key] = a
        self.order = to_list(self.order, flatten=True)

    def __delitem__(self, key: int | slice) -> None:
        """Delete an item or slice of items from the progression."""
        del self.order[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over the items in the progression."""
        return iter(self.order)

    def __next__(self) -> str:
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

    def append(self, item: Any, /) -> None:
        """Append an item to the end of the progression."""
        item_ = validate_order(item)
        self.order.extend(item_)

    def pop(self, index: int | None = None, /) -> str:
        """Remove and return an item from the progression."""
        try:
            if index is None:
                return self.order.pop()
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("pop index out of range") from e

    def include(self, item: Any, /) -> None:
        """Include item(s) in the progression."""
        item_ = validate_order(item)
        for i in item_:
            if i not in self.order:
                self.order.append(i)

    def exclude(self, item: int | Any, /) -> None:
        """Exclude an item or items from the progression."""
        for i in validate_order(item):
            while i in self:
                self.remove(i)

    def is_empty(self) -> bool:
        """Check if the progression is empty."""
        return not self.order

    def __reverse__(self) -> Iterator[str]:
        """Return a reversed progression."""
        return self.__class__(reversed(self.order), name=self.name)

    @override
    def __eq__(self, other: object, /) -> bool:
        """Compare two Progression instances for equality."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(
        self, item: Any, /, start: int = 0, end: int | None = None
    ) -> int:
        """Return the index of an item in the progression."""
        return (
            self.order.index(SysUtil.get_id(item), start, end)
            if end
            else self.order.index(SysUtil.get_id(item), start)
        )

    def remove(self, item: Any, /) -> None:
        """Remove the next occurrence of an item from the progression."""
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
        """Remove and return the leftmost item from the progression."""
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError from e

    def extend(self, item: Any, /) -> None:
        """Extend the progression from the right with anorher progression."""
        if not isinstance(item, Progression):
            raise LionTypeError(
                expected_type=Progression, actual_type=type(item)
            )
        self.order.extend(item.order)

    def count(self, item: Any, /) -> int:
        """Return the number of occurrences of an item"""
        if not self.order or item not in self:
            return 0
        return self.order.count(SysUtil.get_id(item))

    @override
    def __bool__(self) -> bool:
        """Check if the container is not empty."""
        return not self.is_empty()

    def __add__(self, other: Any) -> "Progression":
        """returns a new progression with items added to the end"""
        other = validate_order(other)
        new_order = list(self)
        new_order.extend(other)
        return self.__class__(order=new_order)

    def __radd__(self, other: Any) -> "Progression":
        return self + other

    def __iadd__(self, other: Any) -> "Progression":
        """Add an item to the end of the progression in-place."""
        self.append(other)
        return self

    def __isub__(self, other: Any) -> "Progression":
        """Remove an item from the progression in-place."""
        self.remove(other)
        return self

    def __sub__(self, other: Any) -> "Progression":
        """Remove an item or items from the progression."""
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

    def insert(self, index: int, item: Any, /) -> None:
        """Insert an item at the specified index."""
        item_ = validate_order(item)
        for i in reversed(item_):
            self.order.insert(index, SysUtil.get_id(i))

    def __hash__(self) -> int:
        return hash(self.ln_id)


def progression(
    order: Any = None,
    name: str | None = None,
    /,
) -> Progression:
    """Create a new Progression instance."""
    return Progression(order=order, name=name)


# File: lion_core/generic/progression.py
