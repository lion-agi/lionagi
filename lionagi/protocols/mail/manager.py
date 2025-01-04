# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

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
    Manages mail operations for multiple sources in the Lion framework.

    This class handles the collection, distribution, and management of mail
    between different sources within the system.
    """

    def __init__(self, sources: ID.Item | ID.ItemSeq = None) -> None:
        """
        Initialize a MailManager instance.

        Args:
            sources (List[Any], optional): Initial list of mail sources to
                manage.
        """
        self.sources: Pile[Observable] = Pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: ID.Item | ID.ItemSeq, /) -> None:
        """
        Add new sources to the MailManager.

        Args:
            sources (Any): The sources to add. Can be a single source or
                a list of sources.

        Raises:
            LionValueError: If adding the source(s) fails.
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
        Create a new Mail object.

        Args:
            sender (str): The ID of the sender.
            recipient (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The content of the package.
            request_source (Any, optional): The source of the request.

        Returns:
            Mail: A new Mail object.
        """
        pack = Package(
            category=category, package=package, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=pack)

    def delete_source(self, source_id: IDType) -> None:
        """
        Delete a source from the MailManager.

        Args:
            source_id (str): The ID of the source to delete.

        Raises:
            LionValueError: If the source does not exist.
        """
        if source_id not in self.sources:
            raise ItemNotFoundError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: IDType) -> None:
        """Collect mail from a specific sender."""
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
        """Send mail to a specific recipient."""
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
        """Collect mail from all sources."""
        for source in self.sources:
            self.collect(sender=source.id)

    def send_all(self) -> None:
        """Send mail to all recipients."""
        for source in self.sources:
            self.send(recipient=source.id)

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Execute mail collection and sending process asynchronously.

        This method runs in a loop, collecting and sending mail at
            regular intervals.

        Args:
            refresh_time (int, optional): The time to wait between
                each cycle in seconds. Defaults to 1.
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/mail_manager.py
