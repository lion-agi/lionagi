from collections import deque
from ..generic import Node
from .mail import Mail


class StartMail(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pending_outs = deque()

    def trigger(self, context, structure_id, executable_id):
        start_mail_content = {"context": context, "structure_id": structure_id}
        start_mail = Mail(
            sender_id=self.id_,
            recipient_id=executable_id,
            category="start",
            package=start_mail_content,
        )
        self.pending_outs.append(start_mail)


class MailTransfer(Node):
    def __init__(self):
        super().__init__()
        self.pending_ins = {}
        self.pending_outs = deque()
