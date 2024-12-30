import asyncio
from collections import deque
from typing import Any

from lionagi.protocols.generic.element import IDType

from ..generic._id import ID
from ..generic.concepts import Communicatable, Manager, Observable
from ..generic.pile import Pile
from .mail import Mail, Package, PackageCategory
from .mailbox import Mailbox


class Exchange(Manager):

    def __init__(self, sources: ID[Communicatable].ItemSeq = None):
        self.sources: Pile[Communicatable] = Pile(
            item_type=Communicatable, strict_type=False
        )
        self.mailboxes: dict[IDType, Mailbox] = {}
        if sources:
            self.add_sources(sources)

        self._execute_stop: bool = False

    def add_sources(self, sources: ID[Communicatable].ItemSeq):
        if sources in self.sources:
            raise ValueError(
                f"Source {sources} already exists in the mail manager."
            )

        self.sources.include(sources)
        for source in sources:
            self.mailboxes[source.ln_id] = Mailbox()

    def delete_source(self, sources: ID[Communicatable].ItemSeq):
        if not sources in self.sources:
            raise ValueError(
                f"Source {sources} does not exist in the mail manager."
            )

        self.sources.exclude(sources)
        for source in sources:
            self.mailboxes.pop(source.ln_id)

    @staticmethod
    def create_mail(
        sender: IDType[Communicatable],
        recipient: IDType[Communicatable],
        category: PackageCategory | str,
        item: Any,
        request_source: Any = None,
    ) -> Mail:
        package = Package(
            category=category, item=item, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=package)

    def collect(self, sender: IDType[Communicatable]):
        """collect all mails from a particular sender"""
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")

        manager_sender_mailbox: Mailbox = self.mailboxes[sender]
        sender_mailbox: Mailbox = self.sources[sender].mailbox

        while sender_mailbox.pending_outs:
            mail = sender_mailbox.pending_outs.popleft()
            mail = sender_mailbox.pile_.pop(mail)
            if mail.recipient not in self.sources:
                rec_ = mail.recipient
                raise ValueError(f"Recipient source {rec_} does not exist.")

            manager_sender_mailbox.append_out(mail)

    def send(self, recipient: IDType[Communicatable]):
        """send all pending mails in mail manager to a particular recipient"""
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        manager_recipient_mailbox: Mailbox = self.mailboxes[recipient]
        recipient_mailbox: Mailbox = self.sources[recipient].mailbox

    def collect_all(self) -> None:
        """Collect mail from all sources."""
        for source in self.sources:
            self.collect(sender=source.ln_id)

    def send_all(self) -> None:
        """Send mail to all recipients."""
        for source in self.sources:
            self.send(recipient=source.ln_id)

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
