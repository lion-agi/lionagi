from collections import deque
from pydantic import Field, field_validator
import contextlib

from ..abc import Component, Ordering, get_lion_id, ItemNotFoundError
from .._util import _to_list_type


class Progression(Component, Ordering):

    order: deque[str] = Field(
        default_factory=deque,
        description="A sequence of item ids",
    )

    @field_validator("order", mode="before")
    def _f(cls, value):
        if value is None:
            return deque()
        if isinstance(value, str) and len(value) == 32:
            return deque([value])
        elif isinstance(value, Component):
            return deque([value.ln_id])

        value = [
            i
            for item in _to_list_type(value)
            if isinstance(i := get_lion_id(item), str)
        ]

        if not all([isinstance(item, str) and len(item) == 32 for item in value]):
            raise ValueError(f"Progression must only contain lion ids.")
        return deque(value)

    def __len__(self):
        return len(self.order)

    def append(self, item):
        order = self._f(item)
        self.order.extend(order)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return list(self.order)[key]
        try:
            return self.order[key]
        except IndexError:
            raise ItemNotFoundError(f"index {key}")

    def __contains__(self, item):
        item = self._f(item)
        return all([i in self.order for i in item])

    def remove(self, item):
        """remove first occurrence of item, raise error if not found"""
        item = self._f(item)
        l_ = list(self.order)
        for i in item:
            try:
                l_.remove(i)
            except:
                raise ItemNotFoundError(f"{i}")
        self.order = deque(l_)

    def discard_all(self, item):
        item = self._f(item)
        for i in item:
            while i in self:
                self.remove(i)
                pass

    def popleft(self):
        with contextlib.suppress(IndexError):
            return self.order.popleft()
        raise ItemNotFoundError("None")

    def clear(self):
        self.order.clear()

    def __add__(self, other):
        return progression(self.order + other.order)

    def __radd__(self, other):
        return other + self

    def __setitem__(self, key, value):
        l_ = list(self.order)
        v_ = self._f(value)
        l_[key] = v_[0]
        self.order = deque(l_)

    def __iadd__(self, other):
        self.append(other)
        return self

    def __isub__(self, other):
        self.remove(other)
        return self

    def __len__(self):
        return len(self.order)

    def __iter__(self):
        return iter(self.order)

    # def __next__(self):
    #     return self.order.popleft()

    def __repr__(self):
        return f"Progression({len(self.order)})"

    def __str__(self):
        return self.__repr__()


def progression(order=None, /):
    return Progression(order=order)
