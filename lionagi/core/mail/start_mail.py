from collections import deque
from pydantic import Field
from lionagi.core.generic.node import Node
from lionagi.core.mail.mail import Mail, Package
from lionagi.core.collections import Exchange


class StartMail(Node):
    mailbox: Exchange = Field(
        default_factory=Exchange[Mail], description="The pending start mail"
    )

    def trigger(self, context, structure_id, executable_id):
        start_mail_content = {"context": context, "structure_id": structure_id}
        pack = Package(category="start", package=start_mail_content)
        start_mail = Mail(
            sender=self.ln_id,
            recipient=executable_id,
            package=pack,
        )
        self.mailbox.include(start_mail, "out")
