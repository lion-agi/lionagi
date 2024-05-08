from collections import deque
from lionagi.libs import AsyncUtil

from ..generic.abc import Executable
from .mail import Mail


class MailManager(Executable):
    """
    Manages the sending, receiving, and storage of mail items between various sources.

    This class acts as a central hub for managing mail transactions within a system. It allows for the addition
    and deletion of sources, and it handles the collection and dispatch of mails to and from these sources.

    Attributes:
            sources (Dict[str, Any]): A dictionary mapping source identifiers to their attributes.
            mails (Dict[str, Dict[str, deque]]): A nested dictionary storing queued mail items, organized by recipient
                    and sender.
    """

    def __init__(self, sources=None):
        self.sources = {}
        self.mails = {}
        if sources:
            self.add_sources(sources)
        self.execute_stop = False

    def add_sources(self, sources):
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
        else:
            raise ValueError("Failed to add source, please input list or dict.")

    @staticmethod
    def create_mail(sender, recipient, category, package):
        return Mail(sender, recipient, category, package)

    # def add_source(self, sources: list[Node]):
    #     for source in sources:
    #         if source.id_ in self.sources:
    #             # raise ValueError(f"Source {source.id_} exists, please input a different name.")
    #             continue
    #         self.sources[source.id_] = source
    #         self.mails[source.id_] = {}

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
        while self.sources[sender].pending_outs:
            mail_: Mail = self.sources[sender].pending_outs.popleft()
            if mail_.recipient not in self.sources:
                raise ValueError(
                    f"Recipient source {mail_.recipient} does not exist"
                )
            if mail_.sender not in self.mails[mail_.recipient]:
                self.mails[mail_.recipient].update({mail_.sender: deque()})
            self.mails[mail_.recipient][mail_.sender].append(mail_)

    def send(self, recipient):
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist.")
        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            mails_deque = self.mails[recipient].pop(key)
            if key not in self.sources[recipient].pending_ins:
                self.sources[recipient].pending_ins[key] = mails_deque
            else:
                while mails_deque:
                    mail_ = mails_deque.popleft()
                    self.sources[recipient].pending_ins[key].append(mail_)

    def collect_all(self):
        for ids in self.sources:
            self.collect(ids)

    def send_all(self):
        for ids in self.sources:
            self.send(ids)

    async def execute(self, refresh_time=1):
        while not self.execute_stop:
            self.collect_all()
            self.send_all()
            await AsyncUtil.sleep(refresh_time)
