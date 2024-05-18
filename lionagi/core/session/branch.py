from collections import deque
from typing import Any
from lionagi.libs.ln_convert import is_same_dtype, to_dict, to_df
from lionagi.core.collections.abc import Field
from lionagi.core.collections import (
    pile,
    progression,
    Pile,
    Progression,
    iModel,
    Exchange,
)
from lionagi.core.generic.node import Node
from lionagi.core.action import Tool, ToolManager
from lionagi.core.message import (
    create_message,
    System,
    Instruction,
    AssistantResponse,
    ActionRequest,
    ActionResponse,
)

from lionagi.core.session.directive_mixin import DirectiveMixin

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
    system: System = Field(None)
    user: str = Field(None)
    mailbox: Exchange = Field(None)
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
        mailbox=None,
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
            mailbox (Exchange, optional): An exchange for managing mail.
            imodel (iModel, optional): The model associated with the branch.
        """
        super().__init__()
        self.system = None

        self.user = user or "user"
        self.messages = messages or pile({})
        self.progress = progress or progression()
        self.tool_manager = tool_manager or ToolManager()
        self.mailbox = mailbox or Exchange()
        self.imodel = imodel or iModel()
        if tools:
            self.tool_manager.register_tools(tools)

        system = system or "You are a helpful assistant, let's think step by step"
        self.add_message(system=system, sender=system_sender)

    def set_system(self, system=None) -> None:
        """
        Sets the system message.

        Args:
            system (System): The system message to set.
        """
        system = system or "You are a helpful assistant, let's think step by step"
        self.add_message(system=system)

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
            recipient=recipient,
            requested_fields=requested_fields,
            **kwargs,
        )
    
        if isinstance(_msg, System):
            _msg.recipient = self.ln_id  # the branch itself, system is to the branch
            self._remove_system()
            self.system = _msg

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user or "user"
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

    def merge_branch(
        self, branch: "Branch", update_tool: bool = False, update_model=False
    ) -> None:
        """
        Merges another branch into this branch.

        Args:
            branch (Branch): The branch to merge.
            update_tool (bool, optional): Whether to update the tool manager.
            update_model (bool, optional): Whether to update the model.

        Raises:
            ValueError: If the branch to be merged has no model and update_model is True.
        """
        if update_model and not branch.imodel:
            raise ValueError(
                "Cannot update model: The branch to be merged has no model"
            )

        if self.messages.include(branch.messages) and self.progress.include(
            branch.messages
        ):
            self.datalogger.extend(branch.datalogger.log)

            if update_tool:
                self.tool_manager.registry.update(branch.tool_manager.registry)

            if update_model:
                self.imodel = branch.imodel

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
                if act_.schema_["function"]["name"] in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.schema_["function"]["name"])
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

    # def send(self, recipient: str, category: str, package: Any) -> None:
    #     mail = Mail(
    #         sender=self.ln_id,
    #         recipient=recipient,
    #         category=category,
    #         package=package,
    #     )
    #     self.mailbox.include(mail, direction="out")

    # # TODO: need to modify this method to include the new message types
    # def receive(
    #     self,
    #     sender: str,
    #     messages: bool = True,
    #     tools: bool = True,
    #     service: bool = True,
    #     llmconfig: bool = True,
    # ) -> None:
    #     skipped_requests = deque()
    #     if sender not in self.pending_ins:
    #         raise ValueError(f"No package from {sender}")
    #     while self.pending_ins[sender]:
    #         mail_ = self.pending_ins[sender].popleft()

    #         # if mail_.category == "messages" and messages:
    #         #     if not isinstance(mail_.package, dataframe.ln_DataFrame):
    #         #         raise ValueError("Invalid messages format")
    #         #     MessageUtil.validate_messages(mail_.package)
    #         #     self.messages = self.messages.merge(mail_.package, how="outer")

    #         if mail_.category == "tools" and tools:
    #             if not isinstance(mail_.package, Tool):
    #                 raise ValueError("Invalid tools format")
    #             self.tool_manager.register_tools([mail_.package])

    #         elif mail_.category == "provider" and service:
    #             from lionagi.libs.ln_api import BaseService

    #             if not isinstance(mail_.package, BaseService):
    #                 raise ValueError("Invalid provider format")
    #             self.service = mail_.package

    #         elif mail_.category == "llmconfig" and llmconfig:
    #             if not isinstance(mail_.package, dict):
    #                 raise ValueError("Invalid llmconfig format")
    #             self.llmconfig.update(mail_.package)

    #         else:
    #             skipped_requests.append(mail_)

    #     self.mailbox.pending_ins[sender] = skipped_requests

    #     if len(self.mailbox.pending_ins[sender]) == 0:
    #         self.mailbox.pending_ins.pop(sender)

    # def receive_all(self) -> None:
    #     for key in list(self.mailbox.pending_ins.keys()):
    #         self.receive(key)
