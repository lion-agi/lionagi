from collections import deque
from pydantic import Field, field_validator
import contextlib

from ..abc import Component, Ordering, get_lion_id, ItemNotFoundError, LionIDable, LionTypeError
from .._util import _to_list_type


class Progression(Component, Ordering):

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
        if value is None:
            return deque()
        if isinstance(value, str) and len(value) == 32:
            return deque([value])
        elif isinstance(value, Component):
            return deque([value.ln_id])

        with contextlib.suppress(Exception):
            value = [
                i
                for item in _to_list_type(value)
                if (i := get_lion_id(item))
            ]
            return deque(value)
        raise LionTypeError(f"Progression must only contain lion ids.")
        
    def __len__(self):
        return len(self.order)

    def append(self, item):
        id_ = get_lion_id(item)
        self.order.append(id_)

    def extend(self, item):
        """if the item is a Progressable, extend the order, else add to the order"""
        if isinstance(item, Progression):
            self.order.extend(item.order)
            return
        order = self._f(item)
        self.order.extend(order)

    def include(self, item) -> bool:
        if item not in self:
            self.extend(item)
        return item in self

    def __getitem__(self, key):
        if isinstance(key, slice):
            return list(self.order)[key]
        try:
            return self.order[key]
        except IndexError:
            raise ItemNotFoundError(f"index {key}")

    def __contains__(self, item):
        if not item:
            return False
        if isinstance(item, Progression):
            return all([i in self.order for i in item.order])
        if isinstance(item, LionIDable) and len( a:= get_lion_id(item)) == 32:
            return a in self.order
        item = self._f(item)
        return all([i in self.order for i in item])

    def remove(self, item: LionIDable):
        """pop the next occurrence of an item, raise error if not found"""
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
        with contextlib.suppress(IndexError):
            return self.order.popleft()
        raise ItemNotFoundError("None")

    def forward(self):
        return self.popleft()

    def clear(self):
        self.order.clear()

    def __add__(self, other):
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
        """add item is from right"""
        return self + other

    def __isub__(self, other):
        """remove item is from left"""
        p = progression(self.order)
        p.exclude(other)
        return p

    def __sub__(self, other):
        p = self.model_copy(deep=True)
        p.exclude(other)
        return p

    def __len__(self):
        return len(self.order)

    def __iter__(self):
        return iter(self.order)

    def __next__(self):
        return self.popleft()

    def __repr__(self):
        return f"Progression({len(self)})"

    def __str__(self):
        return self.__repr__()


def progression(order=None, name=None, /) -> Progression:
    return Progression(order=order, name=name)
