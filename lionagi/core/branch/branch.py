from collections import deque
from typing import Any, Union, TypeVar, Callable

from lionagi.libs.sys_util import PATH_TYPE
from lionagi.libs import StatusTracker, BaseService, convert, dataframe

from ..schema import TOOL_TYPE, Tool, DataLogger
from ..tool import ToolManager, func_to_tool

from ..messages import System
from ..mail import BaseMail

from .util import MessageUtil
from .base_branch import BaseBranch
from .branch_flow_mixin import BranchFlowMixin

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
        persist_path: PATH_TYPE | None = None,  # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        **kwargs,
    ):

        # init base class
        super().__init__(
            messages=messages,
            datalogger=datalogger,
            persist_path=persist_path,
            name=name,
            **kwargs,
        )

        # add branch name
        self.sender = sender or "system"

        # add tool manager and register tools
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

        # add service and llmconfig
        self.service, self.llmconfig = self._add_service(service, llmconfig)
        self.status_tracker = StatusTracker()

        # add instruction sets
        # self.instruction_sets = instruction_sets

        # add pending ins and outs for mails
        self.pending_ins = {}
        self.pending_outs = deque()

        # add system
        if system is not None:
            self.add_message(system=system)

    @classmethod
    def from_csv(
        cls,
        filepath,
        name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,  # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):

        return cls._from_csv(
            filepath=filepath,
            read_kwargs=read_kwargs,
            name=name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

    @classmethod
    def from_json_string(
        cls,
        filepath,
        name: str | None = None,
        service: BaseService | None = None,
        llmconfig: dict[str, str | int | dict] | None = None,
        tools: TOOL_TYPE | None = None,
        datalogger: None | DataLogger = None,
        persist_path: PATH_TYPE | None = None,  # instruction_sets=None,
        tool_manager: ToolManager | None = None,
        read_kwargs=None,
        **kwargs,
    ):

        return cls._from_json(
            filepath=filepath,
            read_kwargs=read_kwargs,
            name=name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

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
    def register_tools(self, tools: Union[Tool, list[Tool]]) -> None:

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

    def send(self, recipient: str, category: str, package: Any) -> None:

        mail_ = BaseMail(
            sender=self.sender, recipient=recipient, category=category, package=package
        )
        self.pending_outs.append(mail_)

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
        """
        Check if the conversation has been invoked with an action response.

        Returns:
                bool: True if the conversation has been invoked, False otherwise.

        """
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
