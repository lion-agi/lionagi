from typing import Generic, TypeVar

from .abc import Element, Field, Sendable
from .pile import Pile, pile
from .progression import Progression, progression

T = TypeVar("T")


class Exchange(Element, Generic[T]):
    """
    Item exchange system designed to handle incoming and outgoing flows of items.

    Attributes:
        pile (Pile[T]): The pile of items in the exchange.
        pending_ins (dict[str, Progression]): The pending incoming items to the exchange.
        pending_outs (Progression): The progression of pending outgoing items.
    """

    pile: Pile[T] = Field(
        default_factory=lambda: pile(),
        description="The pile of items in the exchange.",
        title="pending items",
    )

    pending_ins: dict[str, Progression] = Field(
        default_factory=dict,
        description="The pending incoming items to the exchange.",
        title="pending incoming items",
        examples=["{'sender_id': Progression}"],
    )

    pending_outs: Progression = Field(
        default_factory=lambda: progression(),
        description="The pending outgoing items to the exchange.",
        title="pending outgoing items",
    )

    def __contains__(self, item):
        """
        Check if an item is in the pile.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the pile, False otherwise.
        """
        return item in self.pile

    @property
    def unassigned(self) -> Pile[T]:
        """
        if the item is not in the pending_ins or pending_outs, it is unassigned.
        """
        return pile(
            [
                item
                for item in self.pile
                if (
                    all(item not in j for j in self.pending_ins.values())
                    and item not in self.pending_outs
                )
            ]
        )

    @property
    def senders(self) -> list[str]:
        """
        Get the list of senders for the pending incoming items.

        Returns:
            list[str]: The list of sender IDs.
        """
        return list(self.pending_ins.keys())

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
