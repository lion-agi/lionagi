from lion_core.generic.exchange import Exchange as CoreExchange

from lionagi.core.generic.pile import pile


class Exchange(CoreExchange):

    @property
    def unassigned(self):
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
