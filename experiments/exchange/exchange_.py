from collections import deque
from typing import Any

from lionagi.libs import AsyncUtil, func_call
from lionagi.core.generic import Node
from lionagi.core.generic.mail import Mail, MailBox, MailPackageCategory


class Exchange(Node):
    sources: dict[str, Node]

    def __init__(self, sources: list[Node] | dict[str, Node]):
        # source is  source_id: <Node with mail box>
        self.sources: dict[str, Node] = {}
        self.mails: dict = {}
        self.add_source(sources)
        self.execute_stop = False

    @func_call.singledispatchmethod
    def add_source(self, sources: Any):
        raise ValueError("Failed to add source, please input Node, list or dict")

    @add_source.register
    def _(self, sources: Node):
        if sources.id_ not in self.sources:
            self.sources[sources.id_] = sources
            self.mails[sources.id_] = {}

    @add_source.register
    def _(self, sources: list):
        for v in sources:
            self.add_source(v)

    @add_source.register
    def _(self, sources: dict):
        self.add_source(list(sources.values()))

    @func_call.singledispatchmethod
    def delete_source(self, sources: Any) -> bool | None:
        raise ValueError("Failed to delete source, please input str.")

    @delete_source.register
    def _(self, sources: str) -> bool | None:
        if sources not in self.sources:
            raise ValueError(f"Source {sources} does not exist.")
        self.sources.pop(sources)
        self.mails.pop(sources)
        return True

    @delete_source.register
    def _(self, sources: Node) -> bool | None:
        return self.delete_source(sources.id_)

    @delete_source.register
    def _(self, sources: list):
        return all([self.delete_source(v) for v in sources])

    @delete_source.register
    def _(self, sources: dict):
        return self.delete_source(list(sources.values()))

    @staticmethod
    def create_mail(*args, **kwargs):
        return Mail.create(*args, **kwargs)

    @func_call.singledispatchmethod
    def collect_from(self, sender: Any):
        raise ValueError(f"Failed to collect from source, invalid type {type(sender)}")

    @collect_from.register
    def _(self, sender: str):
        if sender not in self.sources:
            raise ValueError(f"Sender source {sender} does not exist in sources.")

        while self.sources[sender].mailbox.pending_outs:
            mail_: Mail = self.sources[sender].pending_outs.popleft()
            if mail_.recipient_id not in self.sources:
                raise ValueError(
                    f"Recipient source {mail_.recipient_id} does not exist"
                )
            if mail_.sender_id not in self.mails[mail_.recipient_id]:
                self.mails[mail_.recipient_id].update({mail_.sender_id: deque()})
            self.mails[mail_.recipient_id][mail_.sender_id].append(mail_)

    @func_call.singledispatchmethod
    def send_to(self, recipient: Any):
        raise ValueError(f"Failed to send to source, invalid type {type(recipient)}")

    @send_to.register
    def _(self, recipient: str):
        if recipient not in self.sources:
            raise ValueError(f"Recipient source {recipient} does not exist in sources.")

        if not self.mails[recipient]:
            return
        for key in list(self.mails[recipient].keys()):
            mails_deque = self.mails[recipient].pop(key)
            if key not in self.sources[recipient].pending_ins:
                self.sources[recipient].mailbox.pending_ins[key] = mails_deque
            else:
                while mails_deque:
                    mail_ = mails_deque.popleft()
                    self.sources[recipient].mailbox.pending_ins[key].append(mail_)

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
