import json
from typing import Any, Union, List
from dotenv import load_dotenv

from ..configs.oai_configs import oai_schema
from ..utils.call_util import lcall, alcall
from ..schema import DataLogger, Tool
from ..services.oai import OpenAIService
from .messages import System, Instruction, Response
from .instruction_set import InstructionSet
from .branch import Branch


load_dotenv()
OAIService = OpenAIService()

class Session:

    def __init__(
            self, system, dir=None, llmconfig=oai_schema['chat/completions']['config'],
            service=OAIService
    ):
        self.llmconfig = llmconfig
        self.logger_ = DataLogger(dir=dir)
        self.service = service
        self.branches = {"main": Branch(System(system))}
        self.current_branch_name = 'main'
        self.current_branch = self.branches[self.current_branch_name]
        self.latest_response = None

    def new_branch(self, name: str, from_: str):
        if name in self.branches.keys():
            raise ValueError(f'Invalid new branch name {name}. Already existed.')
        if from_ not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {from_}. Not exist.')

        self.branches[name] = self.branches[from_].clone()

    def switch_branch(self, name):
        if name not in self.branches.keys():
            raise ValueError(f'Invalid source branch name {name}. Not exist.')
        self.current_branch_name = name
        self.current_branch = self.branches[name]

    def merge_branch(self, from_: str, to_: str, update=True, if_delete=False):
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

    def delete_branch(self, name) -> bool:
        if name == self.current_branch_name:
            raise ValueError(f'{name} is the current active branch, please switch to another branch before delete it.')
        if name not in self.branches.keys():
            return False
        else:
            self.branches.pop(name)
            return True

    async def call_chatcompletion(self, **kwargs):
        messages = self.current_branch.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self.logger_({"input": payload, "output": completion})
            self.latest_response = Response(response=completion['choices'][0])
            self.current_branch.add_message(self.latest_response)
            self.service.status_tracker.num_tasks_succeeded += 1
        else:
            self.service.status_tracker.num_tasks_failed += 1

    async def _output(self, invoke=True, out=True):
        if invoke:
            try:
                tool_uses = self.latest_response.content
                func_calls = lcall(tool_uses["action_list"], self.current_branch.tool_manager.get_function_call)
                outs = await  alcall(func_calls, self.current_branch.tool_manager.invoke)
                for out, f in zip(outs, func_calls):
                    response = Response(response={"function": f[0], "arguments": f[1], "output": out})
                    self.current_branch.add_message(response)
            except:
                pass
        if out:
            return self.latest_response.content

    def _tool_parser(self, tools, **kwargs):
        # 1. single schema: dict
        # 2. tool: Tool
        # 3. name: str
        # 4. list: 3 types of lists
        def tool_check(tool):
            if isinstance(tool, dict):
                return tool
            elif isinstance(tool, Tool):
                return tool.schema_
            elif isinstance(tool, str):
                if self.current_branch.tool_manager.name_existed(tool):
                    tool = self.current_branch.tool_manager.registry[tool]
                    return tool.schema_
                else:
                    raise ValueError(f'Function {tool} is not registered.')

        if isinstance(tools, bool):
            tool_kwarg = {"tools": self.current_branch.tool_manager.to_tool_schema_list()}
            kwargs = {**tool_kwarg, **kwargs}

        else:
            if not isinstance(tools, list):
                tools = [tools]
            tool_kwarg = {"tools": lcall(tools, tool_check)}
            kwargs = {**tool_kwarg, **kwargs}

        return kwargs

    def _is_invoked(self):
        content = self.current_branch.messages.iloc[-1]['content']
        try:
            if json.loads(content).keys() >= {'function', 'arguments', 'output'}:
                return True
        except:
            return False

    async def initiate(self, instruction, system=None, context=None,
                       name=None, invoke=True, out=True, tools=False, **kwargs) -> Any:
        if system:
            self.current_branch.change_system_message(System(system))
        if isinstance(instruction, Instruction):
            self.current_branch.add_message(instruction)
        else:
            instruct = Instruction(instruction, context, name)
            self.current_branch.add_message(instruct)
        if self.current_branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(tools=tools, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None,
                       out=True, name=None, invoke=True, tools=False, **kwargs) -> Any:
        if system:
            self.current_branch.change_system_message(System(system))
        if isinstance(instruction, Instruction):
            self.current_branch.add_message(instruction)
        else:
            instruct = Instruction(instruction, context, name)
            self.current_branch.add_message(instruct)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
        else:
            if self.current_branch.tool_manager.registry != {}:
                if tools:
                    kwargs = self._tool_parser(tools=tools, **kwargs)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruction, num=3, tools=False, **kwargs):
        if self.current_branch.tool_manager.registry != {}:
            if tools:
                kwargs = self._tool_parser(tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruction, tool_choice="auto", tool_parsed=True, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruction, tool_parsed=True, **kwargs)

    async def instruction_set_auto_followup(self, instruction_set: InstructionSet,
                                            num: Union[int, List] = 3, **kwargs):
        if isinstance(num, List):
            if len(num) != instruction_set.instruct_len:
                raise ValueError('Unmatched auto_followup num size and instructions set size')

        current_instruct_id = instruction_set.first_instruct
        for i in range(instruction_set.instruct_len):
            num_ = num if isinstance(num, int) else num[i]
            instruct_node = instruction_set.get_instruction_node(current_instruct_id)
            tools = instruction_set.get_tools(instruct_node)
            await self.auto_followup(instruct_node, num=num_, tools=tools, **kwargs)

#### Branch Methods: effective to current active branch
    def change_system_message(self, system: System):
        self.current_branch.change_system_message(system)

    def add_instruction_set(self, name, instruction_set):
        self.current_branch.add_instruction_set(name, instruction_set)

    def remove_instruction_set(self, name):
        return self.current_branch.remove_instruction_set(name)

    def register_tools(self, tools):
        self.current_branch.register_tools(tools)

    def delete_tool(self, name):
        return self.current_branch.delete_tool(name)

    def report(self):
        return self.current_branch.report()
