import asyncio
from collections import deque

from pydantic import Field

from lionagi.core.collections import Exchange, Pile, pile
from lionagi.core.collections.abc import Element, Executable
from lionagi.core.collections.util import get_lion_id, to_list_type

from .mail import Mail, Package


class MailManager(Element, Executable):
    """
    Manages the sending, receiving, and storage of mail items between various sources.

    This class acts as a central hub for managing mail transactions within a system. It allows for the addition
    and deletion of sources, and it handles the collection and dispatch of mails to and from these sources.

    Attributes:
            sources (Dict[str, Any]): A dictionary mapping source identifiers to their attributes.
            mails (Dict[str, Dict[str, deque]]): A nested dictionary storing queued mail items, organized by recipient
                    and sender.
            execute_stop (bool): A flag indicating whether to stop execution.
    """

    sources: Pile[Element] = Field(
        default_factory=lambda: pile(),
        description="The pile of managed sources",
    )

    mails: dict[str, dict[str, deque]] = Field(
        default_factory=dict,
        description="The mails waiting to be sent",
        examples=["{'recipient_id': {'sender_id': deque()}}"],
    )

    execute_stop: bool = Field(
        False, description="A flag indicating whether to stop execution."
    )

    def __init__(self, sources=None):
        """
        Initializes the MailManager with optional sources.

        Args:
            sources (Optional[list]): A list of sources to be managed by the MailManager.
        """
        super().__init__()
        if sources:
            self.add_sources(sources)

    def add_sources(self, sources):
        """
        Adds new sources to the MailManager.

        Args:
            sources (list): A list of sources to be added.

        Raises:
            ValueError: If failed to add sources.
        """
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError(f"Failed to add source. Error {e}")

    @staticmethod
    def create_mail(sender, recipient, category, package):
        """
        Creates a mail item.

        Args:
            sender (str): The sender of the mail.
            recipient (str): The recipient of the mail.
            category (str): The category of the mail.
            package (Any): The content of the package.

        Returns:
            Mail: The created mail object.
        """
        pack = Package(category=category, package=package)
        mail = Mail(
            sender=sender,
            recipient=recipient,
            package=pack,
        )
        return mail

    def delete_source(self, source_id):
        """
        Deletes a source from the MailManager.

        Args:
            source_id (str): The ID of the source to be deleted.

        Raises:
            ValueError: If the source does not exist.
        """
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender):
        """
        Collects mails from a sender's outbox and queues them for the recipient.

        Args:
            sender (str): The ID of the sender.

        Raises:
            ValueError: If the sender or recipient source does not exist.
        """
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")
        mailbox = (
            self.sources[sender]
            if isinstance(self.sources[sender], Exchange)
            else self.sources[sender].mailbox
        )
        while mailbox.pending_outs.size() > 0:
            mail_id = mailbox.pending_outs.popleft()
            mail = mailbox.pile.pop(mail_id)
            if mail.recipient not in self.sources:
                raise ValueError(
                    f"Recipient source {mail.recipient} does not exist"
                )
            if mail.sender not in self.mails[mail.recipient]:
                self.mails[mail.recipient].update({mail.sender: deque()})
            self.mails[mail.recipient][mail.sender].append(mail)

    def send(self, recipient):
        """
        Sends mails to a recipient's inbox.

        Args:
            recipient (str): The ID of the recipient.

        Raises:
            ValueError: If the recipient source does not exist.
        """
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            pending_mails = self.mails[recipient].pop(key)
            mailbox = (
                self.sources[recipient]
                if isinstance(self.sources[recipient], Exchange)
                else self.sources[recipient].mailbox
            )
            while pending_mails:
                mail = pending_mails.popleft()
                mailbox.include(mail, "in")

    def collect_all(self):
        """
        Collects mails from all sources.
        """
        for source in self.sources:
            self.collect(get_lion_id(source))

    def send_all(self):
        """
        Sends mails to all sources.
        """
        for source in self.sources:
            self.send(get_lion_id(source))

    async def execute(self, refresh_time=1):
        """
        Continuously collects and sends mails until execution is stopped.

        Args:
            refresh_time (int): The time in seconds to wait between each cycle. Defaults to 1.
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await asyncio.sleep(refresh_time)
