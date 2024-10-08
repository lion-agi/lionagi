from collections.abc import Callable
from typing import Any, ClassVar, Literal

from lionabc import BaseiModel, Traversal
from lionfuncs import is_same_dtype
from pydantic import Field, model_validator

from lion_core.action import Tool, ToolManager
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.mail import Mail
from lion_core.communication.message import MessageFlag, RoledMessage
from lion_core.communication.package import Package
from lion_core.communication.system import System
from lion_core.converter import ConverterRegistry
from lion_core.generic.exchange import Exchange
from lion_core.generic.note import Note
from lion_core.generic.pile import Pile
from lion_core.generic.progression import Progression, progression
from lion_core.session.base import BaseSession
from lion_core.session.msg_handlers.create_msg import create_message
from lion_core.session.msg_handlers.validate_msg import validate_message


class BranchConverterRegistry(ConverterRegistry):
    """Registry for Branch converters."""

    pass


class Branch(BaseSession, Traversal):
    """
    Represents a branch in the conversation tree with tools and messages.

    This class manages a conversation branch, including messages, tools,
    and communication within the branch.
    """

    messages: Pile | None = Field(None)
    tool_manager: ToolManager | None = Field(None)
    mailbox: Exchange | None = Field(None)
    progress: Progression | None = Field(None)
    system: System | None = Field(None)
    user: str | None = Field(None)
    imodel: BaseiModel | None = Field(None)

    _converter_registry: ClassVar = BranchConverterRegistry

    @model_validator(mode="before")
    def _validate_input(cls, data: dict) -> dict:
        messages = data.pop("messages", None)
        data["messages"] = cls.pile_type(
            validate_message(messages),
            {RoledMessage},
            strict=False,
        )
        data["progress"] = progression(
            list(data.pop("messages", [])),
        )
        data["tool_manager"] = data.pop(
            "tool_manager",
            ToolManager(),
        )
        data["mailbox"] = data.pop(
            "mailbox",
            Exchange(),
        )
        if "tools" in data:
            data["tool_manager"].register_tools(data.pop("tools"))
        return cls.validate_system(data)

    @model_validator(mode="after")
    def _check_system(self):
        if self.system not in self.messages:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)
        return self

    def set_system(self, system: System) -> None:
        """
        Set or update the system message for the branch.

        Args:
            system: The new system message.
        """
        if len(self.progress) < 1:
            self.messages.include(system)
            self.system = system
            self.progress[0] = self.system
        else:
            self._change_system(system, delete_previous_system=True)
            self.progress[0] = self.system

    def add_message(
        self,
        *,
        sender: Any | MessageFlag = None,
        recipient: Any | MessageFlag = None,
        instruction: Any | MessageFlag = None,
        context: Any | MessageFlag = None,
        guidance: Any | MessageFlag = None,
        request_fields: dict | MessageFlag = None,
        system: Any = None,
        system_sender: Any = None,
        system_datetime: bool | str | None | MessageFlag = None,
        images: list | MessageFlag = None,
        image_detail: Literal["low", "high", "auto"] | MessageFlag = None,
        assistant_response: str | dict | None | MessageFlag = None,
        action_request: ActionRequest | None = None,
        action_response: ActionResponse | None = None,
        func: str | Callable | MessageFlag = None,
        arguments: dict | MessageFlag = None,
        func_output: Any | MessageFlag = None,
        metadata: Note | dict = None,  # additional branch parameters
        delete_previous_system: bool = None,
    ) -> bool:
        _msg = create_message(
            sender=sender,
            recipient=recipient,
            instruction=instruction,
            context=context,
            guidance=guidance,
            request_fields=request_fields,
            system=system,
            system_datetime=system_datetime,
            images=images,
            image_detail=image_detail,
            assistant_response=assistant_response,
            action_request=action_request,
            action_response=action_response,
            func=func,
            arguments=arguments,
            func_output=func_output,
            system_sender=system_sender,
        )

        if isinstance(_msg, System):
            _msg.recipient = (
                self.ln_id
            )  # the branch itself, system is to the branch
            self._change_system(
                system=_msg,
                delete_previous_system=delete_previous_system,
            )

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user
            _msg.recipient = recipient or self.ln_id

        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or self.user or "user"

        if isinstance(_msg, ActionRequest):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "N/A"

        if isinstance(_msg, ActionResponse):
            _msg.sender = sender or "N/A"
            _msg.recipient = recipient or self.ln_id

        if metadata:
            _msg.metadata.update(metadata, ["extra"])

        return self.messages.include(_msg)

    def clear_messages(self) -> None:
        """Clear all messages except the system message."""
        self.messages.clear()
        self.progress.clear()
        self.messages.include(self.system)
        self.progress.insert(0, self.system)

    def _change_system(
        self,
        system: System,
        delete_previous_system: bool = False,
    ):
        """
        Change the system message.

        Args:
            system: The new system message.
            delete_previous_system: If True, delete the previous system
                message.
        """
        old_system = self.system
        self.system = system
        self.messages.insert(0, self.system)

        if delete_previous_system:
            self.messages.exclude(old_system)

    def send(
        self,
        recipient: str,
        category: str,
        package: Any,
        request_source: str,
    ) -> None:
        """
        Send a mail to a recipient.

        Args:
            recipient: The recipient's ID.
            category: The category of the mail.
            package: The content of the mail.
            request_source: The source of the request.
        """
        package = Package(
            category=category,
            package=package,
            request_source=request_source,
        )

        mail = Mail(
            sender=self.ln_id,
            recipient=recipient,
            package=package,
        )
        self.mailbox.include(mail, "out")

    def receive(
        self,
        sender: str,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ) -> None:
        """
        Receives mail from a sender.

        Args:
            sender (str): The ID of the sender.
            message (bool, optional): Whether to process message mails.
            tool (bool, optional): Whether to process tool mails.
            imodel (bool, optional): Whether to process imodel mails.

        Raises:
            ValueError: If the sender does not exist or the mail category
                is invalid.
        """
        skipped_requests = progression()
        if sender not in self.mailbox.pending_ins.keys():
            raise ValueError(f"No package from {sender}")
        while self.mailbox.pending_ins[sender].size() > 0:
            mail_id = self.mailbox.pending_ins[sender].popleft()
            mail: Mail = self.mailbox.pile_[mail_id]

            if mail.category == "message" and message:
                if not isinstance(mail.package.package, RoledMessage):
                    raise ValueError("Invalid message format")
                new_message = mail.package.package.clone()
                new_message.sender = mail.sender
                new_message.recipient = self.ln_id
                self.messages.include(new_message)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools(mail.package.package)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.package, BaseiModel):
                    raise ValueError("Invalid iModel format")
                self.imodel = mail.package.package
                self.mailbox.pile_.pop(mail_id)

            else:
                skipped_requests.append(mail)

        self.mailbox.pending_ins[sender] = skipped_requests

        if self.mailbox.pending_ins[sender].size() == 0:
            self.mailbox.pending_ins.pop(sender)

    def receive_all(self) -> None:
        """
        Receives mail from all senders.
        """
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)

    @property
    def last_response(self) -> AssistantResponse | None:
        """
        Get the last assistant response.

        Returns:
            AssistantResponse | None: The last assistant response, if any.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile:
        """
        Get all assistant responses as a Pile.

        Returns:
            Pile: A Pile containing all assistant responses.
        """
        return self.pile_type(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    def update_last_instruction_meta(self, meta: dict) -> None:
        """
        Update metadata of the last instruction.

        Args:
            meta (dict): Metadata to update.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], Instruction):
                self.messages[i].metadata.update(meta, ["extra"])
                return

    def has_tools(self) -> bool:
        """
        Check if the branch has any registered tools.

        Returns:
            bool: True if tools are registered, False otherwise.
        """
        return self.tool_manager.registry != {}

    def register_tools(self, tools: Any) -> None:
        """
        Register new tools to the tool manager.

        Args:
            tools (Any): Tools to be registered.
        """
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(
        self,
        tools: Any,
        verbose: bool = True,
    ) -> bool:
        """
        Delete specified tools from the tool manager.

        Args:
            tools (Any): Tools to be deleted.
            verbose (bool): If True, print status messages.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not isinstance(tools, list):
            tools = [tools]
        if is_same_dtype(input_=tools, dtype=str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif is_same_dtype(input_=tools, dtype=Tool):
            for act_ in tools:
                if act_.function_name in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.function_name)
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def to_chat_messages(self, progress=None) -> list[dict[str, Any]]:
        """
        Convert messages to a list of chat message dictionaries.

        Returns:
            list[dict[str, Any]]: A list of chat message dictionaries.
        """
        if not all(i in self.messages for i in (progress or self.progress)):
            raise ValueError("Invalid progress")
        return [self.messages[i].chat_msg for i in (progress or self.progress)]

    def _is_invoked(self) -> bool:
        """Check if the last message is an ActionResponse."""
        return isinstance(self.messages[-1], ActionResponse)


__all__ = ["Branch"]
# File: lion_core/session/branch.py
