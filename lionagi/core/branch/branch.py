from collections import deque
from typing import Any
from lionagi.libs.ln_convert import is_same_dtype, to_dict

from ..generic.abc import Field
from ..generic import Node, Pile, pile, DataLogger, progression, Progression, Model, Exchange
from ..action import Tool, ToolManager
from ..mail.mail import Mail


from .directive_mixin import DirectiveMixin
from ..message import (
    RoledMessage,
    create_message,
    System,
    Instruction,
    AssistantResponse,
    ActionRequest,
    ActionResponse,
)


class Branch(Node, DirectiveMixin):

    messages: Pile[RoledMessage] = Field(None)
    datalogger: DataLogger = Field(None)
    progre: Progression = Field(None)
    tool_manager: ToolManager = Field(None)
    system: System = Field(None)
    user: str = Field(None)
    mailbox: Exchange = Field(None)
    model: Model = Field(None)

    def __init__(
        self,
        system: System | None = None,
        system_sender: str | None = None,
        user: str | None = None,
        messages: Pile[RoledMessage] = None,
        datalogger: DataLogger = None,
        persist_path: str | None = None,
        progre: Progression = None,
        tool_manager: ToolManager = None,
        tools: Any = None,
        mailbox=None,
        model=None,
    ):

        super().__init__()
        self.system = None

        system = system or "You are a helpful assistant, let's think step by step"
        if system:
            self.system = (
                system
                if isinstance(system, System)
                else create_message(
                    system=system,
                    recipient=self.ln_id,
                    sender=system_sender or "system",
                )
            )

        self.user = user or "user"
        self.messages = messages or pile({}, RoledMessage)
        self.datalogger = datalogger or DataLogger(persist_path)
        self.progre = progre or progression()
        self.tool_manager = tool_manager or ToolManager()
        self.mailbox = mailbox or Exchange()
        self.model = model or Model()
        if tools:
            self.tool_manager.register_tools(tools)

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
    ) -> bool:

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

        return self.messages.include(_msg) and self.progre.include(_msg)

    def to_chat_messages(self) -> list[dict[str, Any]]:
        return [self.messages[j].chat_msg for j in self.progre]

    def _remove_system(self) -> None:
        self.messages.exclude(self.system)
        self.progre.exclude(self.system)
        self.system = None

    @property
    def has_tools(self) -> bool:
        return self.tool_manager.registry != {}

    def merge_branch(
        self, branch: "Branch", update_tool: bool = False, update_model=False
    ) -> None:

        if update_model and not branch.model:
            raise ValueError(
                "Cannot update model: The branch to be merged has no model"
            )

        if self.messages.include(branch.messages) and self.progre.include(
            branch.messages
        ):
            self.datalogger.extend(branch.datalogger.log)

            if update_tool:
                self.tool_manager.registry.update(branch.tool_manager.registry)

            if update_model:
                self.model = branch.model

    def register_tools(self, tools) -> None:
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(self, tools, verbose: bool = True) -> bool:
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

    # TODO: need to modify this method to include the new message types
    def _is_invoked(self) -> bool:
        content = self.messages[self.progre[-1]].content

        try:
            if to_dict(content)["action_response"].keys() >= {
                "function",
                "arguments",
                "output",
            }:
                return True
        except Exception:
            return False
        return False


