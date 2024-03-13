from typing import Dict, Any
from collections import deque
from lionagi.core.mail.schema import BaseMail


class MailManager:

    def __init__(self, sources: Dict[str, Any]):
        self.sources = sources
        self.mails = {}
        for key in self.sources.keys():
            self.mails[key] = {}

    @staticmethod
    def create_mail(sender, recipient, category, package):
        return BaseMail(sender, recipient, category, package)

    def add_source(self, sources: Dict[str, Any]):
        for key in sources.keys():
            if key in self.sources:
                raise ValueError(f"{key} exists, please input a different name.")
            self.sources[key] = {}

    def delete_source(self, source_name):
        if source_name not in self.sources:
            raise ValueError(f"{source_name} does not exist.")
        self.sources.pop(source_name)

    def collect(self, sender):
        if sender not in self.sources:
            raise ValueError(f"{sender} does not exist.")
        while self.sources[sender].pending_outs:
            mail_ = self.sources[sender].pending_outs.popleft()
            if mail_.sender not in self.mails[mail_.recipient]:
                self.mails[mail_.recipient] = {mail_.sender: deque()}
            self.mails[mail_.recipient][mail_.sender].append(mail_)

    def send(self, to_name):
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
