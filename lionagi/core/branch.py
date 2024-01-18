from ..tools.tool_manager import ToolManager
from .conversation import Conversation
from .messages import Message
from pandas import DataFrame
from copy import deepcopy
from typing import Any, Dict, Union
from datetime import datetime


class Branch(Conversation):

    # instruction set is an object
    def __init__(self, init_message: Union[Message, DataFrame],
                 instruction_sets: dict = None,
                 tool_manager: ToolManager = None) -> None:
        super().__init__()
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()

        if isinstance(init_message, DataFrame):
            self.messages = init_message
        elif isinstance(init_message, Message):
            self.add_message(init_message)
        else:
            raise ValueError('Please input a valid init_message: DataFrame or Message')
        self.system_message = self.messages.loc[0, 'content']

    def change_system_message(self, system: Message):
        message_dict = system.to_dict()
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[0] = message_dict
        self.system_message = self.messages.loc[0, 'content']

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
        cloned = Branch()
        cloned.messages = self.messages.copy()
        cloned.instruction_sets = deepcopy(self.instruction_sets)
        cloned.tool_manager = ToolManager()
        cloned.tool_manager.registry = deepcopy(self.tool_manager.registry)
        return cloned

    def merge(self, branch, update=True):
        message_copy = self.messages.copy()
        branch_system = message_copy.loc[0]
        message_copy.drop(0, inplace=True)
        self.messages = self.messages.merge(message_copy, how='outer')
        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.tool_manager.registry.update(branch.tool_manager.registry)
            self.messages.loc[0] = branch_system
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.tool_manager.registry.items():
                if key not in self.tool_manager.registry:
                    self.tool_manager.registry[key] = value

    def report(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.message_counts(),
            "instruction_sets": self.instruction_sets,
            "registered_tools": self.tool_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def to_chatcompletion_message(self):
        message = []
        for _, row in self.messages.iterrows():
            out = {"role": row['role'], "content": row['content']}
            message.append(out)
        return message