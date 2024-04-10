from abc import ABC
from collections import deque
from lionagi.core.generic import BaseNode
from lionagi.core.generic.mail import Mail
from typing import Any


class Signal(BaseNode, ABC): ...


class Start(Signal):
    pending_outs: deque = deque()

    def trigger(self, context: Any, structure_id: str, executable_id: str):
        start_mail_content = {"context": context, "structure_id": structure_id}
        start_mail = Mail(
            sender=self.id_,
            recipient=executable_id,
            category="start",
            package=start_mail_content,
        )
        self.pending_outs.append(start_mail)
