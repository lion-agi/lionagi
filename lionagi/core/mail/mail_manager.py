from collections import deque
from lionagi.libs import AsyncUtil
from ..schema import BaseNode
from .schema import BaseMail


class MailManager:
    """
    Manages the sending, receiving, and storage of mail items between various sources.

    This class acts as a central hub for managing mail transactions within a system. It allows
    for the addition and deletion of sources, and it handles the collection and dispatch of
    mails to and from these sources.

    Attributes:
        sources (Dict[str, Any]): A dictionary mapping source identifiers to their attributes.
        mails (Dict[str, Dict[str, deque]]): A nested dictionary storing queued mail items,
            organized by recipient and sender.
        execute_stop (bool): A flag indicating whether to stop the mail execution loop.

    Methods:
        __init__(self, sources: Any) -> None:
            Initializes the MailManager instance with the given sources.

        add_sources(self, sources: Any) -> None:
            Adds sources to the MailManager.

        create_mail(sender_id: str, recipient_id: str, category: str, package: Any) -> BaseMail:
            Creates a new BaseMail instance with the given parameters.

        add_source(self, sources: list[BaseNode]) -> None:
            Adds a list of sources to the MailManager.

        delete_source(self, source_id: str) -> None:
            Deletes a source from the MailManager.

        collect(self, sender_id: str) -> None:
            Collects outgoing mails from a sender and queues them for the recipients.

        send(self, recipient_id: str) -> None:
            Sends queued mails to a recipient.

        collect_all(self) -> None:
            Collects outgoing mails from all sources.

        send_all(self) -> None:
            Sends queued mails to all recipients.

        async execute(self, refresh_time: int = 1) -> None:
            Executes the mail collection and sending process in a loop until stopped.
    """

    def __init__(self, sources):
        """
        Initializes the MailManager instance with the given sources.

        Args:
            sources: The sources to initialize the MailManager with.
        """
        self.sources = {}
        self.mails = {}
        self.add_sources(sources)
        self.execute_stop = False

    def add_sources(self, sources):
        """
        Adds sources to the MailManager.

        Args:
            sources: The sources to add. Can be a dictionary or a list of sources.
        """
        if isinstance(sources, dict):
            for _, v in sources.items():
                if v.id_ not in self.sources:
                    self.sources[v.id_] = v
                    self.mails[v.id_] = {}
        elif isinstance(sources, list):
            for v in sources:
                if v.id_ not in self.sources:
                    self.sources[v.id_] = v
                    self.mails[v.id_] = {}

    @staticmethod
    def create_mail(sender_id, recipient_id, category, package):
        """
        Creates a new BaseMail instance with the given parameters.

        Args:
            sender_id: The ID of the sender.
            recipient_id: The ID of the recipient.
            category: The category of the mail.
            package: The package to be sent in the mail.

        Returns:
            A new BaseMail instance.
        """
        return BaseMail(sender_id, recipient_id, category, package)

    def add_source(self, sources: list[BaseNode]):
        """
        Adds a list of sources to the MailManager.

        Args:
            sources: The list of sources to add.
        """
        for source in sources:
            if source.id_ in self.sources:
                # raise ValueError(f"Source {source.id_} exists, please input a different name.")
                continue
            self.sources[source.id_] = source
            self.mails[source.id_] = {}

    def delete_source(self, source_id):
        """
        Deletes a source from the MailManager.

        Args:
            source_id: The ID of the source to delete.

        Raises:
            ValueError: If the source does not exist.
        """
        if source_id not in self.sources:
            raise ValueError(f"Source {source_id} does not exist.")
        # if self.mails[source_id]:
        #     raise ValueError(f"None empty pending mails in source {source_id}")
        self.sources.pop(source_id)
        self.mails.pop(source_id)

    def collect(self, sender_id):
        """
        Collects outgoing mails from a sender and queues them for the recipients.

        Args:
            sender_id: The ID of the sender.

        Raises:
            ValueError: If the sender source does not exist or the recipient source does not exist.
        """
        if sender_id not in self.sources:
            raise ValueError(f"Sender source {sender_id} does not exist.")
        while self.sources[sender_id].pending_outs:
            mail_ = self.sources[sender_id].pending_outs.popleft()
            if mail_.recipient_id not in self.sources:
                raise ValueError(
                    f"Recipient source {mail_.recipient_id} does not exist"
                )
            if mail_.sender_id not in self.mails[mail_.recipient_id]:
                self.mails[mail_.recipient_id] = {mail_.sender_id: deque()}
            self.mails[mail_.recipient_id][mail_.sender_id].append(mail_)

    def send(self, recipient_id):
        """
        Sends queued mails to a recipient.

        Args:
            recipient_id: The ID of the recipient.

        Raises:
            ValueError: If the recipient source does not exist.
        """
        if recipient_id not in self.sources:
            raise ValueError(f"Recipient source {recipient_id} does not exist.")
        if not self.mails[recipient_id]:
            return
        for key in list(self.mails[recipient_id].keys()):
            mails_deque = self.mails[recipient_id].pop(key)
            if key not in self.sources[recipient_id].pending_ins:
                self.sources[recipient_id].pending_ins[key] = mails_deque
            else:
                while mails_deque:
                    mail_ = mails_deque.popleft()
                    self.sources[recipient_id].pending_ins[key].append(mail_)

    def collect_all(self):
        """Collects outgoing mails from all sources."""
        for ids in self.sources:
            self.collect(ids)

    def send_all(self):
        """Sends queued mails to all recipients."""
        for ids in self.sources:
            self.send(ids)

    async def execute(self, refresh_time=1):
        """
        Executes the mail collection and sending process in a loop until stopped.

        Args:
            refresh_time: The time interval between each iteration of the loop (default: 1).
        """
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await AsyncUtil.sleep(refresh_time)
