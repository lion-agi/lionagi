from collections import deque
from pydantic import Field
from lionagi.libs import AsyncUtil
from lionagi.core.collections.abc import Executable, Element
from lionagi.core.collections import Exchange
from lionagi.core.collections.util import to_list_type, get_lion_id
from .mail import Mail, Package
from lionagi.core.collections import Pile, pile, Progression, progression

class MailManager(Element, Executable):
    """
    Manages the sending, receiving, and storage of mail items between various sources.

    This class acts as a central hub for managing mail transactions within a system. It allows for the addition
    and deletion of sources, and it handles the collection and dispatch of mails to and from these sources.

    Attributes:
            sources (Dict[str, Any]): A dictionary mapping source identifiers to their attributes.
            mails (Dict[str, Dict[str, deque]]): A nested dictionary storing queued mail items, organized by recipient
                    and sender.
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
        super().__init__()
        if sources:
            self.add_sources(sources)

    def add_sources(self, sources):
        try:
            sources = to_list_type(sources)
            self.sources.include(sources)
            for item in sources:
                self.mails[item.ln_id] = {}
        except Exception as e:
            raise ValueError(f"Failed to add source. Error {e}")

    @staticmethod
    def create_mail(sender, recipient, category, package):
        pack = Package(category=category, package=package)
        mail = Mail(
            sender=sender,
            recipient=recipient,
            package=pack,
        )
        return mail

    def delete_source(self, source_id):
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        # if self.mails[source_id]:
        #     raise ValueError(f"None empty pending mails in source {source_id}")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender):
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist.")
        mailbox = self.sources[sender] if isinstance(self.sources[sender], Exchange) else self.sources[sender].mailbox
        while mailbox.pending_outs:
            mail_id = mailbox.pending_outs.popleft()
            mail = mailbox.pile.pop(mail_id)
            if mail.recipient not in self.sources:
                raise ValueError(f"Recipient source {mail.recipient} does not exist")
            if mail.sender not in self.mails[mail.recipient]:
                self.mails[mail.recipient].update({mail.sender: deque()})
            self.mails[mail.recipient][mail.sender].append(mail)

    def send(self, recipient):
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            pending_mails = self.mails[recipient].pop(key)
            mailbox = self.sources[recipient] if isinstance(self.sources[recipient], Exchange) \
                else self.sources[recipient].mailbox
            while pending_mails:
                mail = pending_mails.popleft()
                mailbox.include(mail, "in")

    def collect_all(self):
        for source in self.sources:
            self.collect(get_lion_id(source))

    def send_all(self):
        for source in self.sources:
            self.send(get_lion_id(source))

    async def execute(self, refresh_time=1):
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await AsyncUtil.sleep(refresh_time)
