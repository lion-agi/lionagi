# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Provides the `Exchange` class, which orchestrates mail flows among
sources that implement `Communicatable`. It collects pending outgoing
mail from each source and delivers them to the appropriate recipients.
"""

import asyncio
from typing import Any

from lionagi.protocols.generic.element import IDType

from .._concepts import Communicatable
from ..generic.element import ID
from ..generic.pile import Pile
from .mail import Mail, Package, PackageCategory
from .mailbox import Mailbox


class Exchange:
    """
    Manages mail exchange operations among a set of sources that are
    `Communicatable`. Each source has an associated `Mailbox` to store
    inbound and outbound mail.

    Attributes
    ----------
    sources : Pile[Communicatable]
        The communicatable sources participating in the exchange.
    buffer : dict[IDType, list[Mail]]
        A temporary holding area for mail messages before they reach
        their recipient's mailbox.
    mailboxes : dict[IDType, Mailbox]
        Maps each source's ID to its Mailbox.
    _execute_stop : bool
        A flag indicating whether to stop the asynchronous execution loop.
    """

    def __init__(self, sources: ID[Communicatable].ItemSeq = None):
        """
        Initialize an `Exchange` instance.

        Parameters
        ----------
        sources : ID[Communicatable].ItemSeq, optional
            One or more communicatable sources to manage. If provided,
            they are immediately added.
        """
        self.sources: Pile[Communicatable] = Pile(
            item_type={Communicatable}, strict_type=False
        )
        self.buffer: dict[IDType, list[Mail]] = {}
        self.mailboxes: dict[IDType, Mailbox] = {}
        if sources:
            self.add_source(sources)
        self._execute_stop: bool = False

    def add_source(self, sources: ID[Communicatable].ItemSeq) -> None:
        """
        Register new communicatable sources for mail exchange.

        Parameters
        ----------
        sources : ID[Communicatable].ItemSeq
            The source(s) to be added.

        Raises
        ------
        ValueError
            If the given sources already exist in this exchange.
        """
        if sources in self.sources:
            raise ValueError(
                f"Source {sources} already exists in the mail manager."
            )

        self.sources.include(sources)
        for source in sources:
            self.mailboxes[source.id] = source.mailbox
        self.buffer.update({source.id: [] for source in sources})

    def delete_source(self, sources: ID[Communicatable].ItemSeq) -> None:
        """
        Remove specified sources from the exchange, clearing any pending
        mail associated with them.

        Parameters
        ----------
        sources : ID[Communicatable].ItemSeq
            The source(s) to remove.

        Raises
        ------
        ValueError
            If the given sources do not exist in this exchange.
        """
        if not sources in self.sources:
            raise ValueError(
                f"Source {sources} does not exist in the mail manager."
            )

        self.sources.exclude(sources)
        for source in sources:
            self.buffer.pop(source.id)
            self.mailboxes.pop(source.id)

    @staticmethod
    def create_mail(
        sender: ID[Communicatable],
        recipient: ID[Communicatable],
        category: PackageCategory | str,
        item: Any,
        request_source: Any = None,
    ) -> Mail:
        """
        Helper method to create a new Mail instance.

        Parameters
        ----------
        sender : ID[Communicatable]
            The ID (or Communicatable) identifying the mail sender.
        recipient : ID[Communicatable]
            The ID (or Communicatable) identifying the mail recipient.
        category : PackageCategory | str
            A classification for the package contents.
        item : Any
            The actual item/data to be sent.
        request_source : Any, optional
            Additional context about the request origin, if any.

        Returns
        -------
        Mail
            A newly created Mail object ready for sending.
        """
        package = Package(
            category=category, item=item, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=package)

    def collect(self, sender: ID[Communicatable]) -> None:
        """
        Collect all outbound mail from a specific sender, moving it
        to the exchange buffer.

        Parameters
        ----------
        sender : ID[Communicatable]
            The ID of the source from which mail is collected.

        Raises
        ------
        ValueError
            If the sender is not part of this exchange.
        """
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")

        sender_mailbox: Mailbox = self.sources[sender].mailbox

        while sender_mailbox.pending_outs:
            mail: Mail = sender_mailbox.pile_.popleft()
            self.buffer[mail.recipient].append(mail)

    def deliver(self, recipient: ID[Communicatable]) -> None:
        """
        Deliver all mail in the buffer addressed to a specific recipient.

        Parameters
        ----------
        recipient : ID[Communicatable]
            The ID of the source to receive mail.

        Raises
        ------
        ValueError
            If the recipient is not part of this exchange or if mail
            references an unknown sender.
        """
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")

        recipient_mailbox: Mailbox = self.sources[recipient].mailbox

        while self.buffer[recipient]:
            mail = self.buffer[recipient].pop(0)
            if mail.recipient != recipient:
                raise ValueError(
                    f"Mail recipient {mail.recipient} does not match recipient {recipient}"
                )
            if mail.sender not in self.sources:
                raise ValueError(f"Mail sender {mail.sender} does not exist.")
            recipient_mailbox.append_in(mail)

    def collect_all(self) -> None:
        """
        Collect mail from every source in this exchange.
        """
        for source in self.sources:
            self.collect(sender=source.id)

    def deliver_all(self) -> None:
        """
        Deliver mail to every source in this exchange.
        """
        for source in self.sources:
            self.deliver(recipient=source.id)

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Continuously collect and deliver mail in an asynchronous loop.

        Parameters
        ----------
        refresh_time : int, optional
            Number of seconds to wait between each cycle. Defaults to 1.
        """
        while not self._execute_stop:
            self.collect_all()
            self.deliver_all()
            await asyncio.sleep(refresh_time)


# File: lionagi/protocols/mail/exchange.py
