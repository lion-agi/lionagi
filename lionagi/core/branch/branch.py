from datetime import datetime
import json
import pandas as pd
from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
from dotenv import load_dotenv

from lionagi._services.base_service import StatusTracker
from lionagi._services.oai import OpenAIService
from lionagi.configs.oai_configs import oai_schema
from lionagi.schema import DataLogger, Tool
from lionagi.tools.tool_manager import ToolManager
from lionagi.utils import alcall, as_dict, get_flattened_keys, lcall, get_timestamp
from ..instruction_set.instruction_set import InstructionSet
from ..messages.messages import Instruction, System
from .conversation import Conversation

load_dotenv()

oai_service = OpenAIService()

class Branch(Conversation):

    def __init__(self, dir = None, messages: pd.DataFrame=None, instruction_sets: Dict =None, tool_manager=None, service=oai_service, llmconfig=None):
        super().__init__(dir)
        self.messages = messages if messages is not None else pd.DataFrame(columns=["node_id", "role", "sender", "timestamp" ,"content"])
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()
        self.service=service
        self.status_tracker = StatusTracker()
        self.llmconfig = llmconfig or oai_schema["chat/completions"]["config"]

    def change_system_message(self, system: Any, sender: str=None):
        if isinstance(system, (str, Dict)):
            system = System(system, sender=sender)
        if isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = str(pd.Timestamp.now())
            self.add_message(system=message_dict)
            df = self.messages[self.messages.role == 'system']
            df.loc[0] = message_dict
        else:
            raise ValueError("Input cannot be converted into a system message.")

    def add_instruction_set(self, name, instruction_set):
        self.instruction_sets[name] = instruction_set

    def remove_instruction_set(self, name):
        return self.instruction_sets.pop(name)

    def register_tools(self, tools):
        if not isinstance(tools, list):
            tools = [tools]
        self.tool_manager.register_tools(tools=tools)

    def delete_tool(self, name):
        if name in self.tool_manager.registry:
            self.tool_manager.registry.pop(name)
            return True
        return False

    def clone(self):
        cloned = Branch(
            dir = self._logger.dir,
            messages=self.messages.copy(), 
            instruction_sets=self.instruction_sets.copy(),
            tool_manager=ToolManager()
        )
        tools = [
            tool for tool in self.tool_manager.registry.values()]
        
        cloned.register_tools(tools)

        return cloned

    def merge_branch(self, branch: 'Branch', update=True):
        
        branch_copy = branch.clone()
        self.merge_conversation(branch_copy, update=update)

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(
                branch.tool_manager.registry
            )
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    def messages_describe(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
            "summary_by_sender": self.info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def to_chatcompletion_message(self):
        message = []
        for _, row in self.messages.iterrows():
            out = {"role": row['role'], "content": json.dumps(as_dict(row['content']))}
            message.append(out)
        return message


    def _is_invoked(self):

        content = self.messages.iloc[-1]['content']
        try:
            if (
                as_dict(content)['action_response'].keys() >= {'function', 'arguments', 'output'}
            ):
                return True
        except:
            return False
    
    async def call_chatcompletion(self, **kwargs):
        messages = self.to_chatcompletion_message()
        payload, completion = await self.service.serve_chat(messages=messages, **kwargs)
        if "choices" in completion:
            self._logger.add_entry({"input": payload, "output": completion})
            self.add_message(response=completion['choices'][0])
            self.status_tracker.num_tasks_succeeded += 1
        else:
            self.status_tracker.num_tasks_failed += 1

    @property
    def has_tools(self):
        return self.tool_manager.registry != {}

    async def chat(
        self,
        instruction: Union[Instruction, str],
        system: Union[System, str, Dict] = None,
        context: Optional[Any] = None,
        out: bool = True,
        sender: Optional[str] = None,
        invoke: bool = True,
        tools: Union[bool, Tool, List[Tool], str, List[str]] = False,
        **kwargs,
    ) -> Any:
        
        config = {**self.llmconfig}
        
        if system:
            self.change_system_message(system)
        self.add_message(instruction=instruction, context=context, sender=sender)

        if 'tool_parsed' in kwargs:
            kwargs.pop('tool_parsed')
            tool_kwarg = {'tools': tools}
            kwargs = {**tool_kwarg, **kwargs}
            config.update(kwargs)
        else:
            if tools and self.has_tools:
                kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)
                config.update(kwargs)

        
        await self.call_chatcompletion(**config)
        
        async def _output():
            content_ = as_dict(self.messages.content.iloc[-1])
            if invoke:
                try:
                    tool_uses = content_
                    func_calls = lcall(
                        [as_dict(i) for i in tool_uses["action_list"]], 
                        self.tool_manager.get_function_call
                    )
                    outs = await alcall(func_calls, self.tool_manager.invoke)
                    for out_, f in zip(outs, func_calls):
                        self.add_message(response={"function": f[0], "arguments": f[1], "output": out_})
                except:
                    pass
            if out:
                if len(content_.items()) == 1 and len(get_flattened_keys(content_)) == 1:
                    key = get_flattened_keys(content_)[0]
                    return content_[key]
                return content_
        
        return await _output()

    async def auto_followup(
        self,
        instruction: Union[Instruction, str],
        num: int = 3,
        tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
        fallback: Callable =None,
        fallback_kwargs = {},
        **kwargs,
    ) -> None:
        if self.tool_manager.registry != {} and tools:
            kwargs = self.tool_manager._tool_parser(tools=tools, **kwargs)

        cont_ = True
        while num > 0 and cont_ is True:
            if tools:
                await self.chat(instruction, tool_choice="auto", tool_parsed=True, **kwargs)
            else:
                await self.chat(instruction, tool_parsed=True, **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            if fallback is not None:
                if asyncio.iscoroutinefunction(fallback):
                    return await fallback(**fallback_kwargs)
                else:
                    return fallback(**fallback_kwargs)
            return await self.chat(instruction, tool_parsed=True, **kwargs)
        

    async def instruction_set_auto_followup(
        self,
        instruction_set: InstructionSet,
        num: Union[int, List[int]] = 3,
        **kwargs,
    ) -> None:

        if isinstance(num, List):
            if len(num) != instruction_set.instruct_len:
                raise ValueError('Unmatched auto_followup num size and instructions set size')

        current_instruct_node = instruction_set.get_instruction_by_id(instruction_set.first_instruct)
        for i in range(instruction_set.instruct_len):
            num_ = num if isinstance(num, int) else num[i]
            tools = instruction_set.get_tools(current_instruct_node)
            if tools:
                await self.auto_followup(current_instruct_node, num=num_, tools=tools, self=self, **kwargs)
            else:
                await self.chat(current_instruct_node)
            current_instruct_node = instruction_set.get_next_instruction(current_instruct_node)
