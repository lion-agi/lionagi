from ..generic import Node, Pile, pile, DataLogger, progression, Progression
from ..message import MessageRole, RoledMessage, MessageField, System, Instruction, AssistantResponse, ActionRequest, ActionResponse
from ..action import Tool, ToolManager
from ..message.util import MessageUtil


_msg_fields = [i.value for i in MessageField]

class Branch(Node):
   
    messages: Pile[RoledMessage] = pile({}, RoledMessage)
    datalogger: DataLogger = DataLogger()
    prog: Progression = progression()
    tool_manager: ToolManager = ToolManager()
    
    
    
    
    
    def __init__(
        self, 
        system: System | None = None,
        messages: Pile[RoledMessage] = None,
        datalogger: DataLogger = None,
        persist_path: str | None = None,
        prog: Progression = None,
        tool_manager: ToolManager = None,
        tools: Any = None
    ):
        super().__init__()
        self.messages = messages or pile({}, RoledMessage)
        self.datalogger = datalogger or DataLogger(persist_path)
        self.prog = prog or progression()
        self.tool_manager = tool_manager or ToolManager()
        
        if system:
            self.system_node = system if isinstance(system, System) else System(system)
        else:
            self.system_node = None
            
        if tools:
            self.tool_manager.register_tools(tools)
    
    
    def add_message(
        self,
        system = None,
        instruction = None,
        context = None,
        response = None,
        requested_fields=None,
        sender=None,
        recipient=None,
        **kwargs,
    ) -> None:
        
        _msg = MessageUtil.create_message(
            system=system,
            instruction=instruction,
            context=context,
            response=response,
            requested_fields=requested_fields,
            sender=sender,
            recipient=recipient,
            **kwargs,
        )
        
        if isinstance(_msg, System):
            _msg.sender = sender or "system"
            _msg.recipient = self.ln_id     # the branch itself
        
        if isinstance(_msg, Instruction):
            _msg.sender = sender or "user"
            _msg.recipient = self.ln_id
        
        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "user"

        if isinstance(_msg, ActionRequest):
            
        
        
        
        
        
        
        _msg = MessageUtil.create_message(
            system=system,
            instruction=instruction,
            context=context,
            response=response,
            requested_fields=requested_fields,
            recipient=recipient,
            **kwargs,
        )

        if isinstance(_msg, System):
            self.system_node = _msg

        # sourcery skip: merge-nested-ifs
        if isinstance(_msg, Instruction):
            if recipient is None and self.name is not None:
                _msg.recipient = self.name

        if isinstance(_msg, Response):
            if "action_response" in _msg.content.keys():
                if recipient is None and self.name is not None:
                    _msg.recipient = self.name
                if recipient is not None and self.name is None:
                    _msg.recipient = recipient
            if "response" in _msg.content.keys():
                if self.name is not None:
                    _msg.sender = self.name

        setattr(_msg, "node_id", _msg.id_)
        _msg.content = _msg.msg_content
        self.messages.loc[len(self.messages)] = _msg.to_pd_series()
















class BaseBranch(BaseNode, ABC):


    _columns: list[str] = BranchColumns.COLUMNS.value

    def __init__(
        self,
        messages: dataframe.ln_DataFrame | None = None,
        datalogger: DataLogger | None = None,
        persist_path: str | Path | None = None,
        name=None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if isinstance(messages, dataframe.ln_DataFrame):
            if MessageUtil.validate_messages(messages):
                self.messages = messages
            else:
                raise ValueError("Invalid messages format")
        else:
            self.messages = dataframe.ln_DataFrame(columns=self._columns)

        self.datalogger = datalogger or DataLogger(persist_path=persist_path)
        self.name = name

    def add_message(
        self,
        system: dict | list | System | None = None,
        instruction: dict | list | Instruction | None = None,
        context: str | dict[str, Any] | None = None,
        response: dict | list | BaseMessage | None = None,
        requested_fields=None,
        recipient=None,
        **kwargs,
    ) -> None:

        _msg = MessageUtil.create_message(
            system=system,
            instruction=instruction,
            context=context,
            response=response,
            requested_fields=requested_fields,
            recipient=recipient,
            **kwargs,
        )

        if isinstance(_msg, System):
            self.system_node = _msg

        # sourcery skip: merge-nested-ifs
        if isinstance(_msg, Instruction):
            if recipient is None and self.name is not None:
                _msg.recipient = self.name

        if isinstance(_msg, Response):
            if "action_response" in _msg.content.keys():
                if recipient is None and self.name is not None:
                    _msg.recipient = self.name
                if recipient is not None and self.name is None:
                    _msg.recipient = recipient
            if "response" in _msg.content.keys():
                if self.name is not None:
                    _msg.sender = self.name

        setattr(_msg, "node_id", _msg.id_)
        _msg.content = _msg.msg_content
        self.messages.loc[len(self.messages)] = _msg.to_pd_series()

    def _to_chatcompletion_message(
        self, with_sender: bool = False
    ) -> list[dict[str, Any]]:


        message = []

        for _, row in self.messages.iterrows():
            content_ = row["content"]
            if content_.startswith("Sender"):
                content_ = content_.split(":", 1)[1]

            # if isinstance(content_, str):
            #     try:
            #         content_ = json.dumps(to_dict(content_))
            #     except Exception as e:
            #         raise ValueError(
            #             f"Error in serializing, {row['node_id']} {content_}: {e}"
            #         )

            out = {"role": row["role"], "content": content_}
            if with_sender:
                out["content"] = f"Sender {row['sender']}: {content_}"

            message.append(out)
        return message













from collections import deque
from typing import Any, Union, TypeVar, Callable
from pathlib import Path

from lionagi.libs import StatusTracker, BaseService, convert, dataframe

from lionagi.core.generic import DataLogger
from lionagi.core.tool import ToolManager, func_to_tool, Tool, TOOL_TYPE
from lionagi.core.messages.schema import System
from lionagi.core.mail.schema import BaseMail

from lionagi.core.message.util import MessageUtil
from lionagi.core.branch.base import BaseBranch
from lionagi.core.branch.flow_mixin import BranchFlowMixin

from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=Tool)


class Branch(BaseBranch, BranchFlowMixin):
    def __init__(
        self,
        name: str | None = None,
        system: dict | list | System | None = None,
        messages: dataframe.ln_DataFrame | None = None,
        service: BaseService | None = None,
        sender: str | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: list[Callable | Tool] | None = None,
        datalogger: None | DataLogger = None,
        persist_path: str | Path | None = None,  # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        **kwargs,
    ):
        super().__init__(
            messages=messages,
            datalogger=datalogger,
            persist_path=persist_path,
            name=name,
            **kwargs,
        )

        self.sender = sender or "system"
        self.tool_manager = tool_manager or ToolManager()

        if tools:
            try:
                tools_ = []
                _tools = convert.to_list(tools)
                for i in _tools:
                    if isinstance(i, Tool):
                        tools_.append(i)
                    else:
                        tools_.append(func_to_tool(i))

                self.register_tools(tools_)
            except Exception as e:
                raise TypeError(f"Error in registering tools: {e}") from e

        self.service, self.llmconfig = self._add_service(service, llmconfig)
        self.status_tracker = StatusTracker()

        # add instruction sets
        # self.instruction_sets = instruction_sets

        self.pending_ins = {}
        self.pending_outs = deque()

        if system is not None:
            self.add_message(system=system)


    def messages_describe(self) -> dict[str, Any]:
        return dict(
            total_messages=len(self.messages),
            summary_by_role=self._info(),
            summary_by_sender=self._info(use_sender=True),
            # instruction_sets=self.instruction_sets,
            registered_tools=self.tool_manager.registry,
            messages=[msg.to_dict() for _, msg in self.messages.iterrows()],
        )

    @property
    def has_tools(self) -> bool:
        return self.tool_manager.registry != {}

    # todo: also update other attributes
    def merge_branch(self, branch: "Branch", update: bool = True) -> None:
        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how="outer")
        self.datalogger.extend(branch.datalogger.log)

        if update:
            # self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(branch.tool_manager.registry)
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    # ----- tool manager methods ----- #
    def register_tools(
        self, tools: Union[Tool, list[Tool | Callable], Callable]
    ) -> None:
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(
        self,
        tools: Union[T, list[T], str, list[str]],
        verbose: bool = True,
    ) -> bool:
        if not isinstance(tools, list):
            tools = [tools]
        if convert.is_same_dtype(tools, str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif convert.is_same_dtype(tools, Tool):
            for act_ in tools:
                if act_.schema_["function"]["name"] in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.schema_["function"]["name"])
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def send(self, recipient_id: str, category: str, package: Any) -> None:
        mail = BaseMail(
            sender_id=self.id_,
            recipient_id=recipient_id,
            category=category,
            package=package,
        )
        self.pending_outs.append(mail)

    def receive(
        self,
        sender: str,
        messages: bool = True,
        tools: bool = True,
        service: bool = True,
        llmconfig: bool = True,
    ) -> None:
        skipped_requests = deque()
        if sender not in self.pending_ins:
            raise ValueError(f"No package from {sender}")
        while self.pending_ins[sender]:
            mail_ = self.pending_ins[sender].popleft()

            if mail_.category == "messages" and messages:
                if not isinstance(mail_.package, dataframe.ln_DataFrame):
                    raise ValueError("Invalid messages format")
                MessageUtil.validate_messages(mail_.package)
                self.messages = self.messages.merge(mail_.package, how="outer")

            elif mail_.category == "tools" and tools:
                if not isinstance(mail_.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools([mail_.package])

            elif mail_.category == "provider" and service:
                from lionagi.libs.ln_api import BaseService

                if not isinstance(mail_.package, BaseService):
                    raise ValueError("Invalid provider format")
                self.service = mail_.package

            elif mail_.category == "llmconfig" and llmconfig:
                if not isinstance(mail_.package, dict):
                    raise ValueError("Invalid llmconfig format")
                self.llmconfig.update(mail_.package)

            else:
                skipped_requests.append(mail_)

        self.pending_ins[sender] = skipped_requests
        if self.pending_ins[sender] == deque():
            self.pending_ins.pop(sender)

    def receive_all(self) -> None:
        for key in list(self.pending_ins.keys()):
            self.receive(key)

    @staticmethod
    def _add_service(service, llmconfig):
        from lionagi.integrations.provider.oai import OpenAIService

        if service is None:
            try:
                from lionagi.integrations.provider import Services

                service = Services.OpenAI()

            except:
                raise ValueError("No available service")
        if llmconfig is None:
            if isinstance(service, OpenAIService):
                from lionagi.integrations.config import oai_schema

                llmconfig = oai_schema["chat/completions"]["config"]
            else:
                llmconfig = {}
        return service, llmconfig

    def _is_invoked(self) -> bool:
        content = self.messages.iloc[-1]["content"]
        try:
            if convert.to_dict(content)["action_response"].keys() >= {
                "function",
                "arguments",
                "output",
            }:
                return True
        except Exception:
            return False
        return False
