from typing import Generic, TypeVar

from .abc import Element, Field, Sendable
from .pile import Pile, pile
from .progression import Progression, progression

T = TypeVar("T")


class Exchange(Element, Generic[T]):
    """Item exchange system"""

    def exclude(self, item) -> bool:
        """
        Exclude an item from the exchange.

        Args:
            item: The item to exclude.

        Returns:
            bool: True if the item was successfully excluded, False otherwise.
        """
        return (
            self.pile.exclude(item)
            and all([v.exclude(item) for v in self.pending_ins.values()])
            and self.pending_outs.exclude(item)
        )

    def include(self, item, direction=None) -> bool:
        """
        Include an item in the exchange in a specified direction.

        Args:
            item: The item to include.
            direction (str): The direction to include the item ('in' or 'out').

        Returns:
            bool: True if the item was successfully included, False otherwise.
        """
        if self.pile.include(item):
            item = self.pile[item]
            item = [item] if not isinstance(item, list) else item
            for i in item:
                if not self._include(i, direction=direction):
                    return False
            return True

    def _include(self, item: Sendable, direction) -> bool:
        """
        Helper method to include an item in the exchange in a specified direction.

        Args:
            item (Sendable): The item to include.
            direction (str): The direction to include the item ('in' or 'out').

        Returns:
            bool: True if the item was successfully included, False otherwise.
        """
        if direction == "in":
            if item.sender not in self.pending_ins:
                self.pending_ins[item.sender] = progression()
            return self.pending_ins[item.sender].include(item)

        if direction == "out":
            return self.pending_outs.include(item)

        return True

    def to_dict(self) -> dict:
        """
        Convert the exchange to a dictionary.

        Returns:
            dict: The dictionary representation of the exchange.
        """
        return self.model_dump(by_alias=True)

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.pile)
