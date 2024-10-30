from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field

from lionagi.core.collections import Exchange
from lionagi.core.collections.abc import Element, Executable, Progressable
from lionagi.core.mail.mail import Mail, Package


class BaseExecutor(Element, Progressable, Executable, ABC):
    """
    BaseExecutor is an abstract base class that defines the structure for executors
    handling mails, execution control, and context management within the LionAGI system.
    """

    mailbox: Exchange = Field(
        default_factory=Exchange[Mail], description="The pending mails."
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

    context_log: list = Field(
        default_factory=list, description="The context log."
    )

    verbose: bool = Field(
        True,
        description="A flag indicating whether to provide verbose output.",
    )

    def send(
        self,
        recipient: str,
        category: str,
        package: Any,
        request_source: str = None,
    ) -> None:
        """
        Sends a mail to a recipient.

        Args:
            recipient (str): The ID of the recipient.
            category (str): The category of the mail.
            package (Any): The package to send in the mail.
            request_source (str): The source of the request.
        """
        pack = Package(
            category=category, package=package, request_source=request_source
        )
        mail = Mail(
            sender=self.ln_id,
            recipient=recipient,
            package=pack,
        )
        self.mailbox.include(mail, "out")

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the executor's main function.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.

        Returns:
            Any: The result of the execution.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError("The execute method must be implemented.")

    @abstractmethod
    async def forward(self, *args: Any, **kwargs: Any) -> None:
        """
        Forward the execution flow.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError("The forward method must be implemented.")
