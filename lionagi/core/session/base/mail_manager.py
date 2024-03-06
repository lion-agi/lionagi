from typing import Dict, Any
from collections import deque
from lionagi.core.session.base.schema import BaseMail


class MailManager:
    """
    Manages the sending, receiving, and storage of mail items between various sources.

    This class acts as a central hub for managing mail transactions within a system. It allows for the addition
    and deletion of sources, and it handles the collection and dispatch of mails to and from these sources.

    Attributes:
        sources (Dict[str, Any]): A dictionary mapping source identifiers to their attributes.
        mails (Dict[str, Dict[str, deque]]): A nested dictionary storing queued mail items, organized by recipient
            and sender.
    """

    def __init__(self, sources: Dict[str, Any]):
        """
        Initializes the MailManager with a set of sources.

        Args:
            sources (Dict[str, Any]): A mapping of source identifiers to their respective attributes.
        """
        self.sources = sources
        self.mails = {}
        for key in self.sources.keys():
            self.mails[key] = {}

    @staticmethod
    def create_mail(sender, recipient, category, package):
        """
        Constructs a mail item given its sender, recipient, category, and content package.

        Args:
            sender (str): The identifier of the sender.
            recipient (str): The identifier of the recipient.
            category (str): The category or type of the mail.
            package (Any): The content of the mail item.

        Returns:
            BaseMail: An instance of BaseMail constructed with the provided details.
        """
        return BaseMail(sender, recipient, category, package)

    def add_source(self, sources: Dict[str, Any]):
        """
         Adds new sources to the MailManager.

         Args:
             sources (Dict[str, Any]): A dictionary containing the new sources to be added, where each key is a source
                 identifier and the value is its attributes.

         Raises:
             ValueError: If a source with the same identifier already exists.
         """
        for key in sources.keys():
            if key in self.sources:
                raise ValueError(f"{key} exists, please input a different name.")
            self.sources[key] = {}

    def delete_source(self, source_name):
        """
        Deletes a source from the MailManager.

        Args:
            source_name (str): The identifier of the source to be deleted.

        Raises:
            ValueError: If the specified source does not exist.
        """
        if source_name not in self.sources:
            raise ValueError(f"{source_name} does not exist.")
        self.sources.pop(source_name)

    def collect(self, sender):
        """
        Collects pending outgoing mails from a specified sender and queues them for their recipients.

        Args:
            sender (str): The identifier of the sender whose outgoing mails are to be collected.

        Raises:
            ValueError: If the specified sender does not exist or has no registered sources.
        """
        if sender not in self.sources:
            raise ValueError(f"{sender} does not exist.")
        while self.sources[sender].pending_outs:
            mail_ = self.sources[sender].pending_outs.popleft()
            if mail_.sender not in self.mails[mail_.recipient]:
                self.mails[mail_.recipient] = {mail_.sender: deque()}
            self.mails[mail_.recipient][mail_.sender].append(mail_)

    def send(self, to_name):
        """
        Dispatches collected mails to a specified recipient.

        Args:
            to_name (str): The identifier of the recipient to whom the mails should be sent.

        Raises:
            ValueError: If the specified recipient does not exist or if there are no mails to send.
        """
        if to_name not in self.sources:
            raise ValueError(f"{to_name} does not exist.")
        if not self.mails[to_name]:
            return
        else:
            for key in list(self.mails[to_name].keys()):
                request = self.mails[to_name].pop(key)
                if key not in self.sources[to_name].pending_ins:
                    self.sources[to_name].pending_ins[key] = request
                else:
                    self.sources[to_name].pending_ins[key].append(request)
