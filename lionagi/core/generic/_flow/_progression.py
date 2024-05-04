from collections import deque
from pydantic import Field, field_validator
from lionagi.libs.ln_convert import is_same_dtype

from ..abc import Component, Ordering


class Progression(Component, Ordering):

    order: deque[str] = Field(
        default_factory=deque,
        description="A sequence of item ids",
    )

    @field_validator("order", mode="before")
    def _f(cls, value):
        if not all(is_same_dtype(value)) and len(value) > 1:
            raise TypeError(f"Flow must have homogenous items.")

        if isinstance(value[0], Component):
            value = [item.ln_id for item in value]

        if not all([isinstance(item, str) and len(item) == 32 for item in value]):
            raise ValueError(f"Flow must only contain lion ids.")

        return deque(value)

    def __getitem__(self, item):
        return self.order[item]

    def __setitem__(self, key, value):
        self.order[key] = value

    def __add__(self, other):
        return self.order + other.order

    def __sub__(self, other):
        return self.order - other.order

    def __radd__(self, other):
        return other.order + self.order

    def forward(): ...

    def remove(): ...

    def extend(): ...

    def append(): ...

    def popleft(): ...

    def __len__(self):
        return len(self.order)

    def __iter__(self):
        return iter(self.order)

    def __next__(self):
        return self.order.popleft()

    def __contains__(self, item):
        return item in self.order
