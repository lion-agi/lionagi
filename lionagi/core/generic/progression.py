"""
The `Progression` class extends `Element` and implements ordering 
functionalities to manage a sequence of `Element` instances, identified
by their Lion IDs. Efficiently handles ordered collections where elements
need to be accessed, modified, or iterated in a specific sequence.

Attributes:
   name (str | None): Optional descriptive name for progression.
   order (list): List maintaining sequence of Lion IDs.

Methods:
   __getitem__: Access elements by index, providing list-like access.
   __setitem__: Assign new value to position at specified index.
   __len__: Return number of elements in progression.
   append: Add single element to end of progression.
   extend: Add multiple elements to end of progression.
   include: Add elements only if not already included.
   remove: Remove element by Lion ID, raises ItemNotFoundError if not found.
   pop: Remove and return element by index, defaulting to last item.
   popleft: Remove and return first element in progression.
   clear: Remove all elements from progression.
   __contains__: Check if specific item(s) present in progression.
   __iter__, __next__, __reversed__: Support iteration in different orders.
   __add__, __radd__, __iadd__, __sub__, __isub__: Support arithmetic ops.
   __str__, __repr__, __list__: Provide string and list representations.

Versatile, supporting list-like operations with type checks and validation. 
Suitable for scenarios requiring reliable and orderly manipulation.
"""

import contextlib
from lionagi.libs import SysUtil
from pydantic import Field, field_validator
from .abc import Ordering, get_lion_id, ItemNotFoundError, LionIDable, Element
from .util import _validate_order


class Progression(Element, Ordering):

    name: str | None = Field(
        None,
        title="Name",
        description="The name of the progression.",
    )
    order: list = Field(
        default_factory=list,
        title="Order",
        description="The order of the progression.",
    )

    @field_validator("order", mode="before")
    def _validate_order(cls, value) -> list[str]:
        """Validate and convert the order field."""
        return _validate_order(value)

    def __contains__(self, item):
        """Check if an item or items are in the progression."""
        if not item:
            return False
        if isinstance(item, Progression):
            return all([i in self.order for i in item.order])
        if isinstance(item, LionIDable) and len(a := get_lion_id(item)) == 32:
            return a in self.order
        item = self._validate_order(item)
        return all([i in self.order for i in item])

    def __len__(self):
        """Return the number of elements in the progression."""
        return len(self.order)

    def keys(self):
        yield from range(len(self))

    def values(self):
        """Yield the Lion IDs of the elements in the progression."""
        yield from self.order

    def items(self):
        """Yield index and Lion ID pairs for elements in the progression."""
        for idx, item in enumerate(self.order):
            yield idx, item

    def copy(self):
        """Create a deep copy of the progression."""
        return self.model_copy()

    def append(self, item):
        """Append an item, identified by its Lion ID, to end of progression."""
        id_ = get_lion_id(item)
        self.order.append(id_)

    def extend(self, item):
        """Extend the progression from the right with item(s)"""
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = self._validate_order(item)
        self.order.extend(order)

    def include(self, item) -> bool:
        """Include item(s) if not already present, return True if included."""
        if item not in self:
            self.extend(item)
        return item in self

    def __getitem__(self, key):
        """Retrieve an item by its index in the progression."""
        with contextlib.suppress(IndexError):
            return self.order[key]
        raise ItemNotFoundError(f"index {key}")

    def remove(self, item: LionIDable):
        """Remove the next occurrence of an item from the progression."""
        if item in self:
            item = self._validate_order(item)
            l_ = SysUtil.create_copy(self.order)

            with contextlib.suppress(Exception):
                for i in item:
                    l_.remove(i)
                self.order = l_
                return

        raise ItemNotFoundError(f"{item}")

    def __list__(self):
        return self.order

    def popleft(self):
        """Remove and return the leftmost item from the progression."""
        try:
            return self.order.pop(0)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def pop(self, index=None):
        """Remove and return an item from the progression."""
        try:
            return self.order.pop(index)
        except IndexError as e:
            raise ItemNotFoundError("None") from e

    def exclude(self, item) -> bool:
        """Exclude an item or items from the progression."""
        if isinstance(item, int) and item > 0:
            if item > len(self):
                raise IndexError("Cannot remove more items than available.")
            for _ in range(item):
                self.popleft()
            return True
        if isinstance(item, Progression):
            for i in item:
                while i in self:
                    self.remove(i)
            return True
        for i in (a := self._validate_order(item)):
            while i in self:
                self.remove(i)
        return a not in self

    def __add__(self, other):
        """Add an item or items to the end of the progression."""
        _copy = progression(self.order, self.name)
        _copy.include(other)
        return _copy

    def __radd__(self, other):
        if not isinstance(other, Progression):
            _copy = self.copy()
            l_ = SysUtil.create_copy(_copy.order)
            l_.insert(0, get_lion_id(other))
            _copy.order = l_
            return _copy

        return other + self

    def __setitem__(self, key, value):
        a = self._validate_order(value)
        self.order[key] = a

    def __iadd__(self, other):
        """Add an item or items to the end of the progression."""
        return self + other

    def __isub__(self, other):
        """Remove an item or items from the beginning of the progression."""
        p = progression(self.order, self.name)
        p.exclude(other)
        return p

    def __sub__(self, other):
        """Remove an item or items from the progression."""
        p = progression(self.order, self.name)
        p.exclude(other)
        return p

    def __len__(self):
        """Return the length of the progression."""
        return len(self.order)

    def __iter__(self):
        """Iterate over the items in the progression."""
        return iter(self.order)

    def __next__(self):
        """Return the next item in the progression."""
        return self.popleft()

    def __repr__(self):
        """Return a string representation of the progression."""
        return f"Progression({self.order})"

    def __str__(self):
        """Return a string representation of the progression."""
        return f"Progression({self.order})"

    def __list__(self):
        """Return a list representation of the progression."""
        return SysUtil.create_copy(self.order)

    def __reversed__(self):
        """Return a reversed progression."""
        return reversed(self.order)

    def clear(self):
        """Clear the progression."""
        self.order = []


def progression(order=None, name=None, /) -> Progression:
    return Progression(order=order, name=name)
