import contextlib

import lionfuncs as ln
from pydantic import Field, field_validator

from .abc import Element, ItemNotFoundError, LionIDable, Ordering, get_lion_id
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
        return len(self.order)

    def keys(self):
        yield from range(len(self))

    def values(self):
        yield from self.order

    def items(self):
        yield from enumerate(self.order)

    def size(self):
        return len(self)

    def copy(self):
        """create a deep copy"""
        return self.model_copy()

    def append(self, item):
        """Append an item to the end of the progression."""
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
        """Include item(s) in the progression. return true if the item is included."""
        if item not in self:
            self.extend(item)
        return item in self

    def __getitem__(self, key):
        with contextlib.suppress(IndexError):
            a = self.order[key]
            if isinstance(a, list) and len(a) > 1:
                return Progression(order=a)
            elif isinstance(a, list) and len(a) == 1:
                return a[0]
            return a

        raise ItemNotFoundError(f"index {key}")

    def remove(self, item: LionIDable):
        """Remove the next occurrence of an item from the progression."""
        if item in self:
            item = self._validate_order(item)
            l_ = ln.copy(self.order)

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
        for i in (a := self._validate_order(item)):
            while i in self:
                self.remove(i)
        return a not in self

    def __add__(self, other):
        """Add an item or items to the end of the progression."""
        _copy = self.copy()
        _copy.include(other)
        return _copy

    def __radd__(self, other):
        if not isinstance(other, Progression):
            _copy = self.copy()
            l_ = ln.copy(_copy.order)
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
        return self - other

    def __sub__(self, other):
        """Remove an item or items from the progression."""
        _copy = self.copy()
        _copy.remove(other)
        return _copy

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
        return ln.copy(self.order)

    def __reversed__(self):
        """Return a reversed progression."""
        return reversed(self.order)

    def clear(self):
        """Clear the progression."""
        self.order = []

    def to_dict(self):
        """Return a dictionary representation of the progression."""
        return {"order": self.order, "name": self.name}

    def __bool__(self):
        return True

    def __eq__(self, other):
        """Compare two Progression instances for equality."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name

    def __hash__(self):
        """Return a hash value for the Progression instance."""
        return hash((tuple(self.order), self.name))


def progression(order=None, name=None) -> Progression:
    return Progression(order=order, name=name)
