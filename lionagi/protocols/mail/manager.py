# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines the `MailManager` class, which coordinates mail operations
across multiple sources in a more abstract or high-level manner.
"""

import asyncio
from collections import deque
from typing import Any

from lionagi._errors import ItemNotFoundError

from .._concepts import Manager, Observable
from ..generic.element import ID, IDType
from ..generic.pile import Pile, to_list_type
from .exchange import Exchange
from .mail import Mail, Package, PackageCategory


class MailManager(Manager):
    """
    A manager for mail operations across various observable sources
    within LionAGI. Unlike `Exchange`, this class can manage the state
    of multiple sources in a more general or higher-level context,
    storing mail queues in a dictionary rather than individual buffers.

    Attributes
    ----------
    sources : Pile[Observable]
        A concurrency-safe collection of known sources.
    mails : dict[str, dict[str, deque]]
        A nested mapping of recipient -> sender -> queue of mail.
    execute_stop : bool
        Controls the asynchronous execution loop; set to True to exit.
    """

    def __init__(self, sources: ID.Item | ID.ItemSeq = None) -> None:
        """
        Initialize a MailManager instance.

        Parameters
        ----------
        sources : ID.Item | ID.ItemSeq, optional
            Initial source(s) to manage. Each source must be an Observable.
        """
        self.sources: Pile[Observable] = Pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: ID.Item | ID.ItemSeq, /) -> None:
        """
        Register new sources in the MailManager.

        Parameters
        ----------
        sources : ID.Item | ID.ItemSeq
            A single source or multiple sources to be added.

        Raises
        ------
        ValueError
            If adding the sources fails for any reason.
        """
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.id] = {}
        except Exception as e:
            raise ValueError("Failed to add source.") from e

    @staticmethod
    def create_mail(
        sender: ID.Ref,
        recipient: ID.Ref,
        category: PackageCategory | str,
        package: Any,
        request_source: Any = None,
    ) -> Mail:
        """
        Factory method to generate a Mail object.

        Parameters
        ----------
        sender : ID.Ref
            Reference (ID or object) for the sender.
        recipient : ID.Ref
            Reference (ID or object) for the recipient.
        category : PackageCategory | str
            The category of this package.
        package : Any
            The payload or content in the mail.
        request_source : Any, optional
            Additional context about the request source.

        Returns
        -------
        Mail
            A new mail object with specified sender, recipient, and package.
        """
        pack = Package(
            category=category, package=package, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=pack)

    def delete_source(self, source_id: IDType) -> None:
        """
        Remove a source from the manager, discarding any associated mail.

        Parameters
        ----------
        source_id : IDType
            The ID of the source to be removed.

        Raises
        ------
        ItemNotFoundError
            If the given source ID is not present.
        """
        if source_id not in self.sources:
            raise ItemNotFoundError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: IDType) -> None:
        """
        Collect outbound mail from a single source.

        Parameters
        ----------
        sender : IDType
            The ID of the sender whose outbound mail is retrieved.

        Raises
        ------
        ItemNotFoundError
            If the sender is not recognized.
        """
        if sender not in self.sources:
            raise ItemNotFoundError(f"Sender source {sender} does not exist.")
        mailbox: Exchange = (
            self.sources[sender]
            if isinstance(self.sources[sender], Exchange)
            else self.sources[sender].mailbox
        )
        while mailbox.pending_outs.size() > 0:
            mail_id = mailbox.pending_outs.popleft()
            mail: Mail = mailbox.pile_.pop(mail_id)
            if mail.recipient not in self.sources:
                rec_ = mail.recipient
                raise ItemNotFoundError(
                    f"Recipient source {rec_} does not exist"
                )
            if mail.sender not in self.mails[mail.recipient]:
                self.mails[mail.recipient].update({mail.sender: deque()})
            self.mails[mail.recipient][mail.sender].append(mail)

    def send(self, recipient: IDType) -> None:
        """
        Send any pending mail to a specified recipient.

        Parameters
        ----------
        recipient : IDType
            The ID of the recipient to which mail should be delivered.

        Raises
        ------
        ItemNotFoundError
            If the recipient ID is not recognized.
        """
        if recipient not in self.sources:
            raise ItemNotFoundError(
                f"Recipient source {recipient} does not exist."
            )
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            pending_mails = self.mails[recipient].pop(key)
            mailbox: Exchange = (
                self.sources[recipient]
                if isinstance(self.sources[recipient], Exchange)
                else self.sources[recipient].mailbox
            )
            while pending_mails:
                mail = pending_mails.popleft()
                mailbox.include(mail, direction="in")

    def collect_all(self) -> None:
        """
        Collect outbound mail from all known sources.
        """
        for source in self.sources:
            self.collect(sender=source.id)

    def send_all(self) -> None:
        """
        Send mail to all known recipients who have pending items.
        """
        for source in self.sources:
            self.send(recipient=source.id)

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Continuously collect and send mail in an asynchronous loop.

        Parameters
        ----------
        refresh_time : int, optional
            Delay (in seconds) between each collect/send cycle.
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/manager.py
