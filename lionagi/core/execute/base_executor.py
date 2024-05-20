from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field

from lionagi.core.collections.abc import Element
from lionagi.core.collections import Exchange
from lionagi.core.mail.mail import Mail, Package


class BaseExecutor(Element, ABC):
    mailbox: Exchange = Field(
        default_factory=Exchange[Mail], description="The pending mails"
    )
    execute_stop: bool = Field(
        False, description="A flag indicating whether to stop execution."
    )
    context: dict | str | list | None = Field(
        None, description="The context buffer for the next instruction."
    )
    execution_responses: list = Field(
        default_factory=list, description="The list of responses."
    )
    context_log: list = Field(default_factory=list, description="The context log.")
    verbose: bool = Field(
        True, description="A flag indicating whether to provide verbose output."
    )

    def send(self, recipient_id: str, category: str, package: Any) -> None:
        """
        Sends a mail to a recipient.

        Args:
            recipient_id (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The package to send in the mail.
        """
        pack = Package(category=category, package=package)
        mail = Mail(
            sender=self.ln_id,
            recipient=recipient_id,
            package=pack,
        )
        self.mailbox.include(mail, "out")

    def to_dict(self):
        return self.model_dump(by_alias=True)