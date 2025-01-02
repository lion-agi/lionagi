# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import Any

from lionagi.protocols.generic.element import IDType

from .._concepts import Communicatable
from ..generic.element import ID
from ..generic.pile import Pile
from .mail import Mail, Package, PackageCategory
from .mailbox import Mailbox


class Exchange:

    def __init__(self, sources: ID[Communicatable].ItemSeq = None):
        self.sources: Pile[Communicatable] = Pile(
            item_type={Communicatable}, strict_type=False
        )
        self.buffer: dict[IDType, list[Mail]] = {}
        self.mailboxes: dict[IDType, Mailbox] = {}
        if sources:
            self.add_source(sources)
        self._execute_stop: bool = False

    def add_source(self, sources: ID[Communicatable].ItemSeq):
        if sources in self.sources:
            raise ValueError(
                f"Source {sources} already exists in the mail manager."
            )

        self.sources.include(sources)
        for source in sources:
            self.mailboxes[source.id] = source.mailbox
        self.buffer.update({source.id: [] for source in sources})

    def delete_source(self, sources: ID[Communicatable].ItemSeq):
        """this will remove the source from the mail manager and all assosiated pending mails"""
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
        package = Package(
            category=category, item=item, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=package)

    def collect(self, sender: ID[Communicatable]):
        """collect all mails from a particular sender"""
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")

        sender_mailbox: Mailbox = self.sources[sender].mailbox

        while sender_mailbox.pending_outs:
            mail: Mail = sender_mailbox.pile_.popleft()
            self.buffer[mail.recipient].append(mail)

    def deliver(self, recipient: ID[Communicatable]):
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
        """Collect mail from all sources."""
        for source in self.sources:
            self.collect(sender=source.id)

    def deliver_all(self) -> None:
        """Send mail to all recipients."""
        for source in self.sources:
            self.deliver(recipient=source.id)

    async def execute(self, refresh_time: int = 1) -> None:
        """
        Execute mail collection and sending process asynchronously.

        This method runs in a loop, collecting and sending mail at
            regular intervals.

        Args:
            refresh_time (int, optional): The time to wait between
                each cycle in seconds. Defaults to 1.
        """
        while not self._execute_stop:
            self.collect_all()
            self.deliver_all()
            await asyncio.sleep(refresh_time)
