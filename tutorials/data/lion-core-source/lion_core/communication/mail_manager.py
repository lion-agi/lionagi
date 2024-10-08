import asyncio
from collections import deque
from typing import Any

from lionabc import BaseManager

from lion_core.communication.mail import Mail, Package
from lion_core.generic.exchange import Exchange
from lion_core.generic.pile import Pile, pile
from lion_core.generic.utils import to_list_type
from lion_core.sys_utils import SysUtil


class MailManager(BaseManager):
    """Manages mail operations for multiple sources in the Lion framework."""

    def __init__(self, sources: list[Any] = None) -> None:
        """Initialize a MailManager instance."""
        self.sources: Pile = pile()
        self.mails: dict[str, dict[str, deque]] = {}
        self.execute_stop: bool = False

        if sources:
            self.add_sources(sources)

    def add_sources(self, sources: Any, /) -> None:
        """Add new sources to the MailManager."""
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError("Failed to add source.") from e

    @staticmethod
    def create_mail(
        sender: str,
        recipient: str,
        category: str,
        package: Any,
        request_source=None,
    ) -> Mail:
        """Create a new Mail object."""
        pack = Package(
            category=category, package=package, request_source=request_source
        )
        return Mail(sender=sender, recipient=recipient, package=pack)

    def delete_source(self, source_id: str) -> None:
        """Delete a source from the MailManager."""
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender: str) -> None:
        """Collect mail from a specific sender."""
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")
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
                raise ValueError(f"Recipient source {rec_} does not exist")
            if mail.sender not in self.mails[mail.recipient]:
                self.mails[mail.recipient].update({mail.sender: deque()})
            self.mails[mail.recipient][mail.sender].append(mail)

    def send(self, recipient: str) -> None:
        """Send mail to a specific recipient."""
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
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
            self.collect(sender=SysUtil.get_id(source))

    def send_all(self) -> None:
        """Send mail to all recipients."""
        for source in self.sources:
            self.send(recipient=SysUtil.get_id(source))

    async def execute(self, refresh_time: int = 1) -> None:
        """Execute mail collection and sending process asynchronously."""
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)


# File: lion_core/communication/mail_manager.py
