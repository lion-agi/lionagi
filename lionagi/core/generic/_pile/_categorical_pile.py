from typing import TypeVar, Any
from pydantic import Field
from ..abc import Component, LionIDable, Record
from ._pile import Pile, pile


T = TypeVar("T", bound=Component)


class CategoricalPile(Component, Record):

    categories: dict[str, Any] = Field(default_factory=lambda: {"main": pile()})

    def all_items(self) -> Pile[T]:
        """Return a pile containing all items from all categories."""
        if self.categories is None:
            return pile()

        else:
            pile1 = pile()
            for k, v in self.categories.items():
                if v and not v.is_empty():
                    pile1.include(v)
                if v is None:
                    self.categories[k] = pile()

            return pile1

    def keys(self):
        """Yield the keys of the categories."""
        yield from self.categories.keys()

    def values(self):
        """Yield the values of the categories."""
        yield from self.categories.values()

    def pile(self):
        """Yield the key-value pairs of the categories."""
        yield from self.categories.items()

    def get(self, key: str, default=...):
        """Get the pile for a given category key."""
        if key in self.categories:
            return self.categories[key]
        if default == ...:
            raise KeyError(f"Category {key} not found.")
        return default

    def __getitem__(self, key: str) -> Pile:
        """Get the pile for a given category key."""
        return self.categories[key]

    def __setitem__(self, key: str, value: Pile):
        """Set the pile for a given category key."""
        self.categories[key] = value

    def __contains__(self, item: LionIDable) -> bool:
        """Check if an item is present in any of the piles."""
        return any(item in pile for pile in self.values())

    def size(self):
        """Return the total size of all piles."""
        return sum(len(pile) for pile in self.values())

    def clear(self):
        """Clear all categories and create a new 'main' category."""
        self.categories.clear()
        self.categories["main"] = Pile()

    def include(self, item: LionIDable, key: str = None) -> bool:
        """Include an item in a specific category or the 'main' category."""
        key = key.lower() if key else "main"
        if key not in self.categories:
            self.categories[key] = Pile()
        return self.categories[key].include(item)

    def exclude(self, item: LionIDable, key: str = None) -> bool:
        """Exclude an item from a specific category or all categories."""
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
        """Check if all piles in the categories are homogenous."""
        return all(pile.is_homogenous() for pile in self.values())

    def is_empty(self):
        """Check if all piles in the categories are empty."""
        return self.size() == 0

    def __iter__(self):
        """Iterate over the categories."""
        return iter(self.categories)

    def __len__(self):
        """Return the number of categories."""
        return len(self.categories)
