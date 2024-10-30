from pydantic import Field

from lionagi.core.collections import Exchange
from lionagi.core.generic.node import Node
from lionagi.core.mail.mail import Mail, Package


class StartMail(Node):
    """
    Represents a start mail node that triggers the initiation of a process.

    Attributes:
        mailbox (Exchange): The exchange object that holds pending start mails.
    """

    mailbox: Exchange = Field(
        default_factory=Exchange[Mail], description="The pending start mail"
    )

    def trigger(self, context, structure_id, executable_id):
        """
        Triggers the start mail by including it in the mailbox.

        Args:
            context (Any): The context to be included in the start mail.
            structure_id (str): The ID of the structure to be initiated.
            executable_id (str): The ID of the executable to receive the start mail.
        """
        start_mail_content = {"context": context, "structure_id": structure_id}
        pack = Package(category="start", package=start_mail_content)
        start_mail = Mail(
            sender=self.ln_id,
            recipient=executable_id,
            package=pack,
        )
        self.mailbox.include(start_mail, "out")
