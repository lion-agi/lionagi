from pathlib import Path
import json
from typing import Any, List, Union, Dict, Optional, Tuple
from dotenv import load_dotenv

from lionagi.schema import DataLogger, Tool, BaseNode
from lionagi.utils import strip_lower, as_dict, nget, to_readable_dict, lcall, CallDecorator, create_copy, get_flattened_keys, alcall
from lionagi.configs.oai_configs import oai_schema

from datetime import datetime
import pandas as pd

from ..messages.messages import System, Message, Instruction, Response
from lionagi.tools.tool_manager import ToolManager
from ..branch.conversation import Conversation
from ..branch.branch import Branch
from ..._services.oai import OpenAIService
from ..instruction_set.instruction_set import InstructionSet

            

OAIService = OpenAIService()

class Session:

    def __init__(
        self,
        system: str,
        dir: str = None,
        llmconfig: Dict[str, Any] = None,
        service  = OAIService,
    ):

        self.llmconfig = llmconfig or oai_schema["chat/completions"]["config"]
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.branches = {"main": Branch()}
        self.branches['main'].add_message(system=system)
        self.current_branch_name = 'main'
        self.current_branch = self.branches[self.current_branch_name]

    def new_branch(self, name: str, system=None, tools=None, sender=None) -> None:
 
        if name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {name}. Already existed.')

        self.branches[name] = Branch()
        if system:
            self.branches[name].change_system_message(system, sender=sender)
        if tools:
            self.branches[name].register_tools(tools)

    def switch_branch(self, branch: Union[str, Branch]) -> None:
        self.current_branch = self.get_branch(branch)


    def merge_branch(
        self, from_: str, to_: str, update: bool = True, if_delete: bool = False
    ) -> None:

        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')
        if to_ not in self.branches.keys():
            raise ValueError(f'Invalid target branch name {from_}. Not exist.')

        self.branches[to_].merge(self.branches[from_], update)
        if if_delete:
            if from_ == self.current_branch_name:
                self.current_branch_name = to_
                self.current_branch = self.branches[to_]
            self.branches.pop(from_)
 
    def delete_branch(self, name: str, verbose=True) -> bool:

        if name == self.current_branch_name:
            raise ValueError(f'{name} is the current active branch, please switch to another branch before delete it.')
        if name not in self.branches.keys():
            return False
        else:
            self.branches.pop(name)
            if verbose:
                print(f'Branch {name} is deleted.')
            return True

    def get_branch(self, branch: Any = None):
        if branch:
            if isinstance(branch, Branch):
                return branch
            if isinstance(branch, str):
                if branch in self.branches.keys():
                    return self.branches[branch]
                else:
                    raise ValueError(f'branch{branch} does not exist.')
        else:
            return self.current_branch

    async def call_chatcompletion(self, branch_name : Any = None, **kwargs):
        branch = self.get_branch(branch_name)

        messages = branch.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self.logger_.add_entry({"input": payload, "output": completion})
            branch.add_message(response=completion['choices'][0])
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1

    async def _output(self, branch_name, invoke=True, out=True):
        branch = self.get_branch(branch_name)
        content_ = as_dict(branch.messages.content.iloc[-1])
        if invoke:
            try:
                tool_uses = content_
                func_calls = lcall(
                    [as_dict(i) for i in tool_uses["action_list"]], 
                    branch.tool_manager.get_function_call
                )
                outs = await alcall(func_calls, branch.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    branch.add_message(response={"function": f[0], "arguments": f[1], "output": out})
            except:
                pass
        if out:
            if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
                key = get_flattened_keys(content_)[0]
                return content_[key]
            
            return content_

    def _tool_parser(self, branch_name, tools: Union[Dict, Tool, List[Tool], str, List[str], List[Dict]], **kwargs) -> Dict:
        branch = self.get_branch(branch_name)
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if branch.tool_manager.name_existed(tool):
                    tool = branch.tool_manager.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": branch.tool_manager.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}

        return kwargs

    async def chat(
        self,
        instruction: Union[Instruction, str],
        system: Optional[str] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        branch_name = None,
        **kwargs,
    ) -> Any:

        branch_name = branch_name or self.current_branch_name
        branch = self.get_branch(branch_name)
        if system:
            branch.change_system_message(system)
        branch.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if branch.tool_manager.registry != {}:
                if tools:
                    kwargs = self._tool_parser(branch_name=branch_name, tools=tools, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(branch_name=branch_name, **config)

        return await self._output(branch_name=branch_name, invoke=invoke, out=out)

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        branch_name=None,
        **kwargs,
    ) -> None:
        branch = self.get_branch(branch_name)
        if branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(branch_name=branch_name, tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.chat(instruction, tool_choice="auto", tool_parsed=True, branch_name=branch_name, **kwargs)
            else:
                await self.chat(instruction, tool_parsed=True, branch_name=branch_name, **kwargs)
            num -= 1
            cont_ = True if branch._is_invoked() else False
        if num == 0:
            await self.chat(instruction, tool_parsed=True, branch_name=branch_name, **kwargs)

    async def instruction_set_auto_followup(
        self,
        instruction_set: InstructionSet,
        num: Union[int, List[int]] = 3,
        branch=None,
        **kwargs,
    ) -> None:
        """Automatically follows up an entire set of instructions.

        Args:
            instruction_set: The set of instructions to follow up.
            num: The number of follow-ups to attempt for each instruction or a list of numbers for each instruction.
            **kwargs: Additional keyword arguments for the AI service.

        Raises:
            ValueError: If the number of follow-ups does not match the number of instructions.
        """
        branch = self.get_branch(branch)
        if isinstance(num, List):
            if len(num) != instruction_set.instruct_len:
                raise ValueError('Unmatched auto_followup num size and instructions set size')

        current_instruct_node = instruction_set.get_instruction_by_id(instruction_set.first_instruct)
        for i in range(instruction_set.instruct_len):
            num_ = num if isinstance(num, int) else num[i]
            tools = instruction_set.get_tools(current_instruct_node)
            if tools:
                await self.auto_followup(current_instruct_node, num=num_, tools=tools, branch=branch, **kwargs)
            else:
                await self.chat(current_instruct_node, branch_name=branch)
            current_instruct_node = instruction_set.get_next_instruction(current_instruct_node)

#### Branch Methods: effective to current active branch
    def change_system_message(self, system: System) -> None:
        """Changes the system message of the current active branch.

        Args:
            system: The new system message.
        """
        self.current_branch.change_system_message(system)

    def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
        """Adds an instruction set to the current active branch.

        Args:
            name: The name of the instruction set.
            instruction_set: The instruction set to add.
        """
        self.current_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name: str) -> bool:
        """Removes an instruction set from the current active branch.

        Args:
            name: The name of the instruction set to remove.

        Returns:
            bool: True if the instruction set is removed, False otherwise.
        """
        return self.current_branch.remove_instruction_set(name)

    def register_tools(self, tools: Union[Tool, List[Tool]]) -> None:
        """Registers one or more tools to the current active branch.

        Args:
            tools: The tool or list of tools to register.
        """
        self.current_branch.register_tools(tools)

    def delete_tool(self, name: str) -> bool:
        """Deletes a tool from the current active branch.

        Args:
            name: The name of the tool to delete.

        Returns:
            bool: True if the tool is deleted, False otherwise.
        """
        return self.current_branch.delete_tool(name)

    def describe(self) -> Dict[str, Any]:
        """Generates a report of the current active branch.

        Returns:
            Dict[str, Any]: The report of the current active branch.
        """
        return self.current_branch.describe()
