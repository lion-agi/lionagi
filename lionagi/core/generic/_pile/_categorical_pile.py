from typing import TypeVar, Any
from pydantic import Field
from ..abc import Component, LionIDable, Record
from ._pile import Pile, pile


T = TypeVar("T", bound=Component)


class CategoricalPile(Component, Record):

    categories: dict[str, Any] = Field(default_factory=lambda: {"main": pile()})

    def all_items(self) -> Pile[T]:
        if self.categories is None:
            return pile()

        else:
            pile1 = pile()
            for k, v in self.categories.items():
                if v and not v.is_empty():
                    for i in v:
                        pile1 += i
                if v is None:
                    self.categories[k] = pile()

            return pile1

    def keys(self):
        yield from self.categories.keys()

    def values(self):
        yield from self.categories.values()

    def items(self):
        yield from self.categories.items()

    def get(self, key: str, default=..., /):
        if key in self.categories:
            return self.categories[key]
        if default == ...:
            raise KeyError(f"Category {key} not found.")
        return default

    def __getitem__(self, key: str) -> Pile:
        return self.categories[key]

    def __setitem__(self, key: str, value: Pile):
        self.categories[key] = value

    def __contains__(self, item: LionIDable) -> bool:
        return any([item in pile for pile in self.values()])

    def size(self):
        return sum([len(pile) for pile in self.values()])

    def clear(self):
        self.categories.clear()
        self.categories["main"] = Pile()

    def include(self, item: LionIDable, key: str = None, /) -> bool:
        """will create new category if key is not found."""
        key = key.lower() if key else "main"
        if key not in self.categories:
            self.categories[key] = Pile()
        return self.categories[key].include(item)

    def exclude(self, item: LionIDable, key: str = None, /) -> bool:

        if not key:
            if all([i.exclude(item) for i in self.values()]):
                return True
            return False

        try:
            key = key.lower()
            if key not in self.categories:
                raise KeyError(f"Category {key} not found.")
            return self.categories[key].exclude(item)
        except Exception as e:
            raise e

    def is_homogenous(self):
        return all([pile.is_homogenous() for pile in self.values()])

    def is_empty(self):
        return self.size == 0

    def __iter__(self):
        return iter(self.categories)

    def __len__(self):
        return len(self.categories)
