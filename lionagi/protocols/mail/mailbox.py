# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols.generic.element import IDType

from ..generic.pile import Pile, Progression
from .mail import Mail

__all__ = ("Mailbox",)


class Mailbox:
    """
    A mailbox that accumulates inbound and outbound mail for a single
    communicatable source.

    Attributes
    ----------
    pile_ : Pile[Mail]
        A concurrency-safe collection storing all mail items.
    pending_ins : dict[IDType, Progression]
        Maps each sender's ID to a progression of inbound mail.
    pending_outs : Progression
        A progression of mail items waiting to be sent (outbound).
    """

    def __init__(self):
        """
        Initialize an empty Mailbox with separate tracks for inbound
        and outbound mail.
        """
        self.pile_ = Pile(item_type=Mail, strict_type=True)
        self.pending_ins: dict[IDType, Progression] = {}
        self.pending_outs = Progression()

    def __contains__(self, item: Mail) -> bool:
        """
        Check if a mail item is currently in this mailbox.
        """
        return item in self.pile_

    @property
    def senders(self) -> list[str]:
        """
        List of sender IDs that have inbound mail in this mailbox.

        Returns
        -------
        list[str]
        """
        return list(self.pending_ins.keys())

    def append_in(self, item: Mail, /):
        """
        Add a mail item to the inbound queue for the item's sender.

        Parameters
        ----------
        item : Mail
        """
        if item.sender not in self.pending_ins:
            self.pending_ins[item.sender] = Progression()
        self.pending_ins[item.sender].include(item)
        self.pile_.include(item)

    def append_out(self, item: Mail, /):
        """
        Add a mail item to the outbound (pending_outs) queue.

        Parameters
        ----------
        item : Mail
        """
        self.pending_outs.include(item)
        self.pile_.include(item)

    def exclude(self, item: Mail, /):
        """
        Remove a mail item from all internal references (inbound, outbound, and pile).

        Parameters
        ----------
        item : Mail
        """
        self.pile_.exclude(item)
        self.pending_outs.exclude(item)
        for v in self.pending_ins.values():
            v.exclude(item)

    def __bool__(self) -> bool:
        """
        Indicates if the mailbox contains any mail.
        """
        return bool(self.pile_)

    def __len__(self) -> int:
        """
        Number of mail items in this mailbox.
        """
        return len(self.pile_)


# File: lionagi/protocols/mail/mailbox.py
