import json
from datetime import datetime
from collections import deque
from typing import Any, Dict, List, Optional, Union, TypeVar

import pandas as pd

from lionagi.util import to_list, to_dict, ConvertUtil, lcall
from lionagi.util.api_util import StatusTracker

from lionagi.core.schema import Tool
from lionagi.core.action import ToolManager
from lionagi.core.flow import ChatFlow

from lionagi.core.session.base.base_branch import BaseBranch
from lionagi.core.session.base.schema import (
    BaseMail,
    Instruction,
    System,
    Response,
    BaseMessage,
)
from lionagi.core.session.base.util import MessageUtil


OAIService = ""

from dotenv import load_dotenv

load_dotenv()

# try:
#     from lionagi.integrations.provider import Services
#
#     OAIService = Services.OpenAI()
#
# except:
#     pass

T = TypeVar("T", bound=Tool)


class Branch(BaseBranch):

    def __init__(
        self,
        branch_name=None,
        system=None,
        messages=None,
        service=None,
        sender=None,
        llmconfig=None,
        tools=None,
        datalogger=None,
        persist_path=None,
        # instruction_sets=None,
        tool_manager=None,
        **kwargs,
    ):

        # init base class
        super().__init__(
            messages=messages,
            datalogger=datalogger,
            persist_path=persist_path,
            **kwargs,
        )

        # add branch name
        self.branch_name = branch_name
        self.sender = sender or "system"

        # add tool manager and register tools
        self.tool_manager = tool_manager if tool_manager else ToolManager()
        if tools:
            try:
                self.register_tools(tools)
            except Exception as e:
                raise TypeError(f"Error in registering tools: {e}")

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
        branch_name=None,
        service=None,
        llmconfig=None,
        tools=None,
        datalogger=None,
        persist_path=None,
        instruction_sets=None,
        tool_manager=None,
        read_kwargs=None,
        **kwargs,
    ):

        self = cls._from_csv(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    @classmethod
    def from_json(
        cls,
        filepath,
        branch_name=None,
        service=None,
        llmconfig=None,
        tools=None,
        datalogger=None,
        persist_path=None,
        instruction_sets=None,
        tool_manager=None,
        read_kwargs=None,
        **kwargs,
    ):

        self = cls._from_json(
            filepath=filepath,
            read_kwargs=read_kwargs,
            branch_name=branch_name,
            service=service,
            llmconfig=llmconfig,
            tools=tools,
            datalogger=datalogger,
            persist_path=persist_path,
            # instruction_sets=instruction_sets,
            tool_manager=tool_manager,
            **kwargs,
        )

        return self

    def messages_describe(self) -> Dict[str, Any]:

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
    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:

        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(
        self,
        tools: Union[T, List[T], str, List[str]],
        verbose: bool = True,
    ) -> bool:

        if not isinstance(tools, list):
            tools = [tools]
        if ConvertUtil.is_same_dtype(tools, str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif ConvertUtil.is_same_dtype(tools, Tool):
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
                if not isinstance(mail_.package, pd.DataFrame):
                    raise ValueError("Invalid messages format")
                MessageUtil.validate_messages(mail_.package)
                self.messages = self.messages.merge(mail_.package, how="outer")

            elif mail_.category == "tools" and tools:
                if not isinstance(mail_.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools([mail_.package])

            elif mail_.category == "provider" and service:
                from lionagi.util.api_util import BaseService

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
            if MessageUtil.to_dict_content(content)["action_response"].keys() >= {
                "function",
                "arguments",
                "output",
            }:
                return True
        except:
            return False

    # noinspection PyUnresolvedReferences
    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):

        await ChatFlow.call_chatcompletion(
            self, sender=sender, with_sender=with_sender, **kwargs
        )

    async def chat(
        self,
        instruction: Union[Instruction, str],
        context: Optional[Any] = None,
        sender: Optional[str] = None,
        system: Optional[Union[System, str, Dict[str, Any]]] = None,
        tools: Union[bool, T, List[T], str, List[str]] = False,
        out: bool = True,
        invoke: bool = True,
        **kwargs,
    ) -> Any:

        return await ChatFlow.chat(
            self,
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            out=out,
            invoke=invoke,
            **kwargs,
        )

    async def ReAct(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender=None,
        system=None,
        tools=None,
        num_rounds: int = 1,
        **kwargs,
    ):

        return await ChatFlow.ReAct(
            self,
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            num_rounds=num_rounds,
            **kwargs,
        )

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        context=None,
        sender=None,
        system=None,
        tools: Union[bool, T, List[T], str, List[str], List[Dict]] = False,
        max_followup: int = 3,
        out=True,
        **kwargs,
    ) -> None:

        return await ChatFlow.auto_followup(
            self,
            instruction=instruction,
            context=context,
            sender=sender,
            system=system,
            tools=tools,
            max_followup=max_followup,
            out=out,
            **kwargs,
        )