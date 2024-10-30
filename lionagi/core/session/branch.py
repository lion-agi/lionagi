from typing import Any

from lionagi.core.action import Tool, ToolManager
from lionagi.core.collections import (
    Exchange,
    Pile,
    Progression,
    iModel,
    pile,
    progression,
)
from lionagi.core.collections.abc import Field
from lionagi.core.generic.node import Node
from lionagi.core.mail import Mail, Package
from lionagi.core.message import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
    RoledMessage,
    System,
    create_message,
)
from lionagi.core.session.directive_mixin import DirectiveMixin
from lionagi.libs.ln_convert import is_same_dtype, to_df


class Branch(Node, DirectiveMixin):
    """
    A class representing a branch in a messaging system.

    Attributes:
        messages (Pile): A pile of messages.
        progress (Progression): A progression of messages.
        tool_manager (ToolManager): A manager for handling tools.
        system (System): The system associated with the branch.
        user (str): The user associated with the branch.
        mailbox (Exchange): An exchange for managing mail.
        imodel (iModel): The model associated with the branch.
    """

    messages: Pile = Field(None)
    progress: Progression = Field(None)
    tool_manager: ToolManager = Field(None)
    system: System | None = Field(None)
    user: str = Field(None)
    mailbox: Exchange[Mail] = Field(None)
    imodel: iModel = Field(None)

    def __init__(
        self,
        system: System | None = None,
        system_sender: str | None = None,
        user: str | None = None,
        messages: Pile = None,
        progress: Progression = None,
        tool_manager: ToolManager = None,
        tools: Any = None,
        imodel=None,
    ):
        """
        Initializes a new instance of the Branch class.

        Args:
            system (System, optional): The system associated with the branch.
            system_sender (str, optional): The sender of the system message.
            user (str, optional): The user associated with the branch.
            messages (Pile, optional): A pile of messages.
            progress (Progression, optional): A progression of messages.
            tool_manager (ToolManager, optional): A manager for handling tools.
            tools (Any, optional): Tools to be registered with the tool manager.
            imodel (iModel, optional): The model associated with the branch.
        """
        super().__init__()
        self.system = None

        self.user = user or "user"
        self.messages = messages or pile({})
        self.progress = progress or progression()
        self.tool_manager = tool_manager or ToolManager()
        self.mailbox = Exchange()
        self.imodel = imodel or iModel()
        if tools:
            self.tool_manager.register_tools(tools)
        self.set_system(system=system, sender=system_sender)
        # system = system or "You are a helpful assistant, let's think step by step"
        # self.add_message(system=system, sender=system_sender)

    def set_system(self, system=None, sender=None) -> None:
        """
        Sets the system message.

        Args:
            system (System): The system message to set.
            sender (str, optional): The sender of the system message.
        """
        if system is not None:
            if len(self.progress) == 0:
                self.add_message(system=system, sender=sender)
            else:
                _msg = System(system=system, sender=sender)
                _msg.recipient = self.ln_id
                self._remove_system()
                self.system = _msg

    def add_message(
        self,
        *,
        system=None,  # system node - JSON serializable
        instruction=None,  # Instruction node - JSON serializable
        context=None,  # JSON serializable
        assistant_response=None,  # JSON
        function=None,
        arguments=None,
        func_outputs=None,
        action_request=None,  # ActionRequest node
        action_response=None,  # ActionResponse node
        images=None,
        sender=None,  # str
        recipient=None,  # str
        requested_fields=None,  # dict[str, str]
        metadata: dict | None = None,  # extra metadata
        **kwargs,  # additional context fields
    ) -> bool:
        """
        Adds a message to the branch.

        Args:
            system (Any, optional): The system node (JSON serializable).
            instruction (Any, optional): The instruction node (JSON serializable).
            context (Any, optional): Additional context (JSON serializable).
            assistant_response (Any, optional): The assistant's response (JSON serializable).
            function (Any, optional): The function associated with the message.
            arguments (Any, optional): The arguments for the function.
            func_outputs (Any, optional): The outputs of the function.
            action_request (Any, optional): The action request node.
            action_response (Any, optional): The action response node.
            sender (str, optional): The sender of the message.
            recipient (str, optional): The recipient of the message.
            requested_fields (dict[str, str], optional): Requested fields for the message.
            metadata (dict, optional): Extra metadata for the message.
            **kwargs: Additional context fields.

        Returns:
            bool: True if the message was successfully added, else False.
        """
        if assistant_response:
            sender = self.ln_id

        _msg = create_message(
            system=system,
            instruction=instruction,
            context=context,
            assistant_response=assistant_response,
            function=function,
            arguments=arguments,
            func_outputs=func_outputs,
            action_request=action_request,
            action_response=action_response,
            sender=sender,
            images=images,
            recipient=recipient,
            requested_fields=requested_fields,
            **kwargs,
        )

        if isinstance(_msg, System):
            _msg.recipient = (
                self.ln_id
            )  # the branch itself, system is to the branch
            self._remove_system()
            self.system = _msg

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user
            _msg.recipient = recipient or self.ln_id

        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "user"

        if isinstance(_msg, ActionRequest):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "N/A"

        if isinstance(_msg, ActionResponse):
            _msg.sender = sender or "N/A"
            _msg.recipient = recipient or self.ln_id

        if metadata:
            _msg._meta_insert(["extra"], metadata)

        return self.messages.include(_msg) and self.progress.include(_msg)

    def to_chat_messages(self) -> list[dict[str, Any]]:
        """
        Converts the messages to chat message format.

        Returns:
            list[dict[str, Any]]: A list of chat messages.
        """
        return [self.messages[j].chat_msg for j in self.progress]

    def _remove_system(self) -> None:
        """
        Removes the system message from the branch.
        """
        self.messages.exclude(self.system)
        self.progress.exclude(self.system)
        self.system = None

    def clear(self) -> None:
        """
        Clears all messages and progression in the branch.
        """
        self.messages.clear()
        self.progress.clear()

    @property
    def has_tools(self) -> bool:
        """
        Checks if the branch has tools.

        Returns:
            bool: True if the branch has tools, else False.
        """
        return self.tool_manager.registry != {}

    def register_tools(self, tools) -> None:
        """
        Registers tools with the tool manager.

        Args:
            tools (Any): The tools to register.
        """
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(self, tools, verbose: bool = True) -> bool:
        """
        Deletes tools from the tool manager.

        Args:
            tools (Any): The tools to delete.
            verbose (bool, optional): Whether to print deletion status.

        Returns:
            bool: True if tools were successfully deleted, else False.
        """
        if not isinstance(tools, list):
            tools = [tools]
        if is_same_dtype(tools, str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif is_same_dtype(tools, Tool):
            for act_ in tools:
                if (
                    act_.schema_["function"]["name"]
                    in self.tool_manager.registry
                ):
                    self.tool_manager.registry.pop(
                        act_.schema_["function"]["name"]
                    )
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def update_last_instruction_meta(self, meta):
        """
        Updates metadata of the last instruction.

        Args:
            meta (dict): The metadata to update.
        """

        for i in reversed(self.progress):
            if isinstance(self.messages[i], Instruction):
                self.messages[i]._meta_insert(["extra"], meta)
                return

    @property
    def last_response(self):
        for i in reversed(self.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def assistant_responses(self):
        return pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    def to_df(self) -> Any:
        """
        Converts the messages to a DataFrame.

        Returns:
            Any: A DataFrame representation of the messages.
        """
        fields = [
            "ln_id",
            "message_type",
            "timestamp",
            "role",
            "content",
            "metadata",
            "sender",
            "recipient",
        ]
        dicts_ = []
        for i in self.progress:
            _d = {}
            for j in fields:
                _d.update({j: getattr(self.messages[i], j, None)})
                _d["message_type"] = self.messages[i].class_name
            dicts_.append(_d)

        return to_df(dicts_)

    def _is_invoked(self) -> bool:
        """
        Checks if the last message is an ActionResponse.

        Returns:
            bool: True if the last message is an ActionResponse, else False.
        """
        return isinstance(self.messages[-1], ActionResponse)

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

    def receive(
        self,
        sender: str,
        message: bool = True,
        tool: bool = True,
        imodel: bool = True,
    ) -> None:
        """
        Receives mail from a sender.

        Args:
            sender (str): The ID of the sender.
            message (bool, optional): Whether to process message mails. Defaults to True.
            tool (bool, optional): Whether to process tool mails. Defaults to True.
            imodel (bool, optional): Whether to process imodel mails. Defaults to True.

        Raises:
            ValueError: If the sender does not exist or the mail category is invalid.
        """
        skipped_requests = progression()
        if sender not in self.mailbox.pending_ins.keys():
            raise ValueError(f"No package from {sender}")
        while self.mailbox.pending_ins[sender].size() > 0:
            mail_id = self.mailbox.pending_ins[sender].popleft()
            mail: Mail = self.mailbox.pile[mail_id]

            if mail.category == "message" and message:
                if not isinstance(mail.package.package, RoledMessage):
                    raise ValueError("Invalid message format")
                new_message = mail.package.package.clone()
                new_message.sender = mail.sender
                new_message.recipient = self.ln_id
                self.messages.include(new_message)
                self.progress.include(new_message)
                self.mailbox.pile.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools(mail.package.package)
                self.mailbox.pile.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.package, iModel):
                    raise ValueError("Invalid iModel format")
                self.imodel = mail.package.package
                self.mailbox.pile.pop(mail_id)

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
