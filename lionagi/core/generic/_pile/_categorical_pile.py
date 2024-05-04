from typing import TypeVar
from pydantic import Field
from ..abc import Component, LionIDable, Record
from ._pile import Pile


T = TypeVar("T", bound=Component)


class CategoricalPile(Component, Record):

    categories: dict[str, Pile] = Field({"main": Pile()})

    def all_items(self) -> Pile[T]:
        return Pile(set({item for pile in self.values() for item in pile}))

    def keys(self):
        iter(self.categories.keys())

    def values(self):
        iter(self.categories.values())

    def items(self):
        iter(self.categories.items())

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
