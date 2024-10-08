from typing import Literal

from lionabc import Communicatable, Structure
from lionabc.exceptions import ItemExistsError, LionValueError
from pydantic import Field
from typing_extensions import override

from lion_core.generic.element import Element
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, progression


class Exchange(Element, Structure):
    """
    Item exchange system designed to handle incoming and outgoing flows.

    Attributes:
        pile (Pile): The pile of items in the exchange.
        pending_ins (dict[str, Progression]): The pending incoming items to the
            exchange.
        pending_outs (Progression): The progression of pending outgoing items.
    """

    pile_: Pile = Field(
        default_factory=lambda: pile(item_type={Communicatable}),
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

    def __contains__(self, item: Communicatable) -> bool:
        """
        Check if an item is in the pile.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the pile, False otherwise.
        """
        return item in self.pile_

    @property
    def senders(self) -> list[str]:
        """
        Get the list of senders for the pending incoming items.

        Returns:
            List[str]: The list of sender IDs.
        """
        return list(self.pending_ins.keys())

    def include(
        self, item: Communicatable, /, direction: Literal["in", "out"]
    ):
        if not isinstance(item, Communicatable):
            raise LionValueError(
                "Invalid item to include. Item must be a mail.",
            )
        if item in self.pile_:
            raise ItemExistsError(f"{item} is already pending in the exchange")
        if direction not in ["in", "out"]:
            raise LionValueError(
                "Invalid direction value. Specify either 'in' or 'out'."
            )
        self.pile_.include(item)

        if direction == "in":
            if item.sender not in self.pending_ins:
                self.pending_ins[item.sender] = Progression()
            self.pending_ins[item.sender].include(item)
        elif direction == "out":
            self.pending_outs.include(item)

    def exclude(self, item: Communicatable, /):
        self.pile_.exclude(item)
        self.pending_outs.exclude(item)
        for v in self.pending_ins.values():
            v.exclude(item)

    @override
    def __bool__(self) -> bool:
        return not self.pile_.is_empty()

    @override
    def __len__(self) -> int:
        return len(self.pile_)


__all__ = ["Exchange"]

# File: lion_core/generic/exchange.py
