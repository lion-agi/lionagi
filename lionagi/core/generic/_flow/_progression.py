from collections import deque
import contextlib
from pydantic import Field, field_validator

from ..abc import (
    Component,
    Ordering,
    get_lion_id,
    ItemNotFoundError,
    LionIDable,
    LionTypeError,
)
from .._util import _to_list_type


class Progression(Component, Ordering):
    """Represents a sequence of item ids."""

    order: deque[str] = Field(
        default_factory=deque,
        description="A sequence of item ids",
    )

    name: str | None = Field(
        default=None,
        description="An optional name for the progression.",
    )

    @field_validator("order", mode="before")
    def _f(cls, value):
        """Validate and convert the order field."""
        if value is None:
            return deque()
        if isinstance(value, str) and len(value) == 32:
            return deque([value])
        elif isinstance(value, Component):
            return deque([value.ln_id])

        with contextlib.suppress(Exception):
            value = [i for item in _to_list_type(value) if (i := get_lion_id(item))]
            return deque(value)
        raise LionTypeError("Progression must only contain lion ids.")

    def __len__(self):
        """Return the length of the progression."""
        return len(self.order)

    def append(self, item):
        """Append an item to the end of the progression."""
        id_ = get_lion_id(item)
        self.order.append(id_)

    def extend(self, item):
        """Extend the progression with items from another progression or iterable."""
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = self._f(item)
        self.order.extend(order)

    def include(self, item) -> bool:
        """Include an item or items in the progression."""
        if item not in self:
            self.extend(item)
        return item in self

    def __getitem__(self, key):
        """Get an item or slice of items from the progression."""
        if isinstance(key, slice):
            return list(self.order)[key]
        try:
            return self.order[key]
        except IndexError:
            raise ItemNotFoundError(f"index {key}")

    def __contains__(self, item):
        """Check if an item or items are in the progression."""
        if not item:
            return False
        if isinstance(item, Progression):
            return all([i in self.order for i in item.order])
        if isinstance(item, LionIDable) and len(a := get_lion_id(item)) == 32:
            return a in self.order
        item = self._f(item)
        return all([i in self.order for i in item])

    def remove(self, item: LionIDable):
        """Remove the next occurrence of an item from the progression."""
        if item in self:
            item = self._f(item)
            l_ = list(self.order)

            with contextlib.suppress(Exception):
                for i in item:
                    l_.remove(i)
                self.order = deque(l_)
                return
        raise ItemNotFoundError(f"{item}")

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
        for i in (a := self._f(item)):
            while i in self:
                self.remove(i)
        return a not in self

    def popleft(self):
        """Remove and return the leftmost item from the progression."""
        with contextlib.suppress(IndexError):
            return self.order.popleft()
        raise ItemNotFoundError("None")

    def forward(self):
        """Move the progression forward by removing the leftmost item."""
        return self.popleft()

    def clear(self):
        """Clear the progression."""
        self.order.clear()

    def __add__(self, other):
        """Add an item or items to the end of the progression."""
        _copy = self.model_copy(deep=True)
        _copy.include(other)
        return _copy

    def __radd__(self, other):
        if not isinstance(other, Progression):
            _copy = self.model_copy(deep=True)
            l_ = list(_copy.order)
            l_.insert(0, get_lion_id(other))
            _copy.order = deque(l_)
            return _copy

        return other + self

    def __setitem__(self, key, value):
        a = get_lion_id(value)
        l_ = list(self.order)
        l_[key] = a
        self.order = deque(l_)

    def __iadd__(self, other):
        """Add an item or items to the end of the progression."""
        return self + other

    def __isub__(self, other):
        """Remove an item or items from the beginning of the progression."""
        p = progression(self.order)
        p.exclude(other)
        return p

    def __sub__(self, other):
        """Remove an item or items from the progression."""
        p = self.model_copy(deep=True)
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
        return f"Progression({len(self)})"

    def __str__(self):
        """Return a string representation of the progression."""
        return self.__repr__()


def progression(order=None, name=None, /) -> Progression:
    return Progression(order=order, name=name)
