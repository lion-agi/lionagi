from __future__ import annotations

from typing import Any, Generic, Self

from pydantic import Field, field_serializer, field_validator

from ..errors import ItemNotFoundError
from .element import ID, Element, IDType, T, validate_order

__all__ = ("Progression",)


class Progression(Element, Generic[T]):
    """An ordered sequence of element IDs with support for progression operations.

    Manages ordered sequences of element IDs with methods for manipulation and
    comparison. Supports both single IDs and sequences of IDs.

    Attributes:
        name: Optional identifier for the progression
        order: List of element IDs in sequence
    """

    name: str | None = Field(default=None)
    order: list[IDType] = Field(default_factory=list)

    @field_validator("order", mode="before")
    def _validate_order(cls, order: Any) -> list[IDType]:
        return validate_order(order)

    @field_serializer("order")
    def _serialize_order(self, order: list[IDType]) -> list[str]:
        return [str(item) for item in order]

    @classmethod
    def create(cls, order: Any, name: str = None) -> Self:
        """Create a new progression instance."""
        return cls(order=order, name=name)

    def __len__(self) -> int:
        """Return number of items in progression."""
        return len(self.order)

    def __bool__(self) -> bool:
        """Return True if progression contains any items."""
        return bool(self.order)

    def __contains__(self, item: Any) -> bool:
        """Check if item(s) exist in progression."""
        item_list = validate_order(item)
        order_set = set(self.order)
        return all(ref in order_set for ref in item_list)

    def __getitem__(self, key: int | slice) -> IDType | list[IDType]:
        """Get item(s) at specified index or slice."""
        return self.order[key]

    def __setitem__(self, key: int | slice, value: Any):
        """Set item(s) at specified index or slice."""
        value_list = validate_order(value)
        if isinstance(key, slice):
            self.order[key] = value_list
        else:
            self.order[key] = value_list[0]

    def __delitem__(self, key: int | slice) -> None:
        """Remove item(s) at specified index or slice."""
        del self.order[key]

    def __iter__(self) -> Any:
        """Iterate over items in progression."""
        return iter(self.order)

    def include(self, item: Any, /) -> bool:
        """Add items to end of progression if not present.

        Returns:
            bool: True if any items were added
        """
        try:
            items = validate_order(item)
        except ValueError:
            return False

        if not items:
            return True

        # Using a set for O(1) membership checks
        order_set = set(self.order)
        appended = False
        for ref in items:
            if ref not in order_set:
                self.order.append(ref)
                order_set.add(ref)
                appended = True
        return appended

    def exclude(self, item: Any, /) -> bool:
        """Remove all occurrences of items from progression.

        Returns:
            bool: True if any items were removed
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
        """Add item(s) to end of progression."""
        if isinstance(item, Element):
            self.order.append(item.id)
            return
        items = validate_order(item)
        self.order.extend(items)

    def pop(self, index: int = -1) -> IDType:
        """Remove and return item at index (default last)."""
        return self.order.pop(index)

    def popleft(self) -> IDType:
        """Remove and return first item."""
        return self.order.pop(0)

    def __reverse__(self) -> Progression:
        return self.__class__(order=list(reversed(self.order)), name=self.name)

    def __eq__(self, other: Progression) -> bool:
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def index(self, item: Any, /, start: int = 0, end: int = None) -> int:
        # Convert to IDType if needed
        ref = ID.get_id(item)
        if end is not None:
            return self.order.index(ref, start, end)
        return self.order.index(ref, start)

    def remove(self, item: Any, /) -> None:
        """Remove first occurrence of each item.

        Raises:
            ItemNotFoundError: If any item not found
        """
        items = validate_order(item)
        if not items:
            return

        order_set = set(self.order)
        if any(ref not in order_set for ref in items):
            raise ItemNotFoundError(f"{items}")

        remove_set = set(items)
        self.order = [x for x in self.order if x not in remove_set]

    def count(self, item: Any, /) -> int:
        """Return number of occurrences of item."""
        ref = ID.get_id(item)
        return self.order.count(ref)

    def extend(self, other: Progression) -> None:
        """Add items from other progression to end."""
        if not isinstance(other, Progression):
            raise ValueError(
                "Can only extend with another Progression instance."
            )
        self.order.extend(other.order)

    def __add__(self, other: Any) -> Progression:
        """Return new progression with concatenated items."""
        items = validate_order(other)
        return self.__class__(order=self.order + items, name=self.name)

    def __radd__(self, other: Any) -> Progression:
        items = validate_order(other)
        return self.__class__(order=items + self.order, name=self.name)

    def __iadd__(self, other: Any) -> Self:
        self.append(other)
        return self

    def __sub__(self, other: Any) -> Progression:
        items = validate_order(other)
        remove_set = set(items)
        new_order = [x for x in self.order if x not in remove_set]
        return self.__class__(order=new_order, name=self.name)

    def __isub__(self, other: Any) -> Self:
        self.remove(other)
        return self

    def __str__(self) -> str:
        return f"Progression({self.order})"

    def __gt__(self, other: Progression) -> bool:
        return self.order > other.order

    def __lt__(self, other: Progression) -> bool:
        return self.order < other.order

    def __ge__(self, other: Progression) -> bool:
        return self.order >= other.order

    def __le__(self, other: Progression) -> bool:
        return self.order <= other.order

    def insert(self, index: int, item: Any, /) -> None:
        """Insert item(s) at specified index."""
        items = validate_order(item)
        self.order[index:index] = items

    def __list__(self) -> list[IDType]:
        return self.order[:]

    def clear(self) -> None:
        self.order.clear()

    __repr__ = __str__


def prog(order: Any, name: str = None, /) -> Progression:
    """Create new progression with given order and optional name."""
    return Progression.create(order=order, name=name)


# Path: lionagi/protocols/progression.py
