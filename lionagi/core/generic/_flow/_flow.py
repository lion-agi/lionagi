"""flow as categorical sequences"""

from collections.abc import Mapping
from collections import deque
from typing import Any
from lionagi.libs.ln_convert import is_same_dtype
from pydantic import Field, field_validator
from ..abc import Record, Component, LionTypeError
from .._util import _to_list_type
from .._pile._pile import Pile, pile
from .._pile._categorical_pile import CategoricalPile

from ._progression import Progression


class Flow(Component):

    branches: Pile[Any] = Field(default_factory=lambda: pile({}, Progression))
    

    def next(self, branch=None, /):
        return self.popleft(branch)

    def popleft(self, branch=None, /):
        try:
            return self.branches[branch or self.default_name].popleft()
        except IndexError:
            return None

    def keys(self):
        return self.branches.keys()

    def items(self):
        return self.branches.items()

    def size(self):
        a = 0
        for seq in self.branches.values():
            a += len(seq)
        return a

    def shape(self):
        return {branch: len(seq) for branch, seq in self.items()}

    def get(self, branch: str, /, default=False) -> deque[str] | None:
        try:
            return self.branches[branch]
        except KeyError as e:
            if default == False:
                raise e
            return default

    def __len__(self):
        return len(self.branches)

    def __iter__(self):
        return iter(self.branches)

    def __next__(self):
        return next(iter(self.branches.values()))

    def __contains__(self, item):
        if isinstance(item, Component):
            return item.ln_id in tuple(
                {item for seq in self.branches.values() for item in seq}
            )
        if isinstance(item, deque):
            return item in self.branches.values()
        return item in self.branches or item in tuple(
            {item for seq in self.branches.values() for item in seq}
        )

    def __getitem__(self, item: str) -> deque[str]:
        return self.branches[item]

    def __setitem__(self, branch, value: deque[str]):
        self.branches[branch] = self._f(value)


def flow(sequences=None, /):
    if sequences is None:
        return Flow()
    return Flow(branches=sequences)


# """flow as categorical sequences"""

# from collections.abc import Mapping
# from collections import deque
# from lionagi.libs.ln_convert import is_same_dtype
# from pydantic import Field, field_validator
# from ..abc import Record, Component

# from .._pile._pile import Pile
# from ._stream import Stream


# class Flow(Pile):

#     item_type: set[type] = Field(
#         default_factory=lambda: {Stream},
#         description="The type of items that can be added to the pile. "
#         "If None, any type is allowed.",
#         frozen=True,
#     )

#     branches: dict[str, Stream] = Field(
#         default_factory=dict,
#         description="A mapping of branches in the flow",
#         alias="pile",
#     )

#     @field_validator("sequences", mode="before")
#     def _validate_sequence(cls, value):

#         if isinstance(value, (list, set, deque)):
#             return {cls.default_name: cls._f(value)}

#         if isinstance(value, Mapping):
#             for branch, seq in value.items():
#                 value[branch] = cls._f(seq)
#             return value

#         raise ValueError("Flow sequences must be a dictionary.")

#     def next(self, branch=None, /):
#         return self.popleft(branch)

#     def popleft(self, branch=None, /):
#         try:
#             return self.branches[branch or self.default_name].popleft()
#         except IndexError:
#             return None

#     def keys(self):
#         return self.branches.keys()

#     def items(self):
#         return self.branches.items()

#     def size(self):
#         a = 0
#         for seq in self.branches.values():
#             a += len(seq)
#         return a

#     def shape(self):
#         return {branch: len(seq) for branch, seq in self.items()}

#     def get(self, branch: str, /, default=False) -> deque[str] | None:
#         try:
#             return self.branches[branch]
#         except KeyError as e:
#             if default == False:
#                 raise e
#             return default

#     def __len__(self):
#         return len(self.branches)

#     def __iter__(self):
#         return iter(self.branches)

#     def __next__(self):
#         return next(iter(self.branches.values()))

#     def __contains__(self, item):
#         if isinstance(item, Component):
#             return item.ln_id in tuple(
#                 {item for seq in self.branches.values() for item in seq}
#             )
#         if isinstance(item, deque):
#             return item in self.branches.values()
#         return item in self.branches or item in tuple(
#             {item for seq in self.branches.values() for item in seq}
#         )

#     def __getitem__(self, item: str) -> deque[str]:
#         return self.branches[item]

#     def __setitem__(self, branch, value: deque[str]):
#         self.branches[branch] = self._f(value)


# def flow(sequences=None, /):
#     if sequences is None:
#         return Flow()
#     return Flow(branches=sequences)
