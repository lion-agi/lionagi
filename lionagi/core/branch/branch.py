import json
from datetime import datetime
import pandas as pd
from typing import Any, Dict,Dict
from lionagi.utils import as_dict
from lionagi.tools.tool_manager import ToolManager
from ..messages.messages import System
from .conversation import Conversation


class Branch(Conversation):

    def __init__(self, dir = None, messages: pd.DataFrame=None, instruction_sets: Dict =None, tool_manager=None):
        super().__init__(dir)
        self.messages = messages if messages is not None else pd.DataFrame(columns=["node_id", "role", "sender", "timestamp" ,"content"])
        self.instruction_sets = instruction_sets if instruction_sets else {}
        self.tool_manager = tool_manager if tool_manager else ToolManager()
    
    @property
    def system_message(self):
        return self.messages.loc[0, 'content']
    
    def change_system_message(self, system: Any, sender: str=None):
        if isinstance(system, (str, Dict)):
            system = System(system, sender=sender)
        if isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = datetime.now()
            self.messages.loc[0] = message_dict
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
        cloned.tool_manager.registry = self.tool_manager.registry.copy()

        return cloned

    def merge(self, branch, update=True):
        messages_copy = branch.messages.copy()
        branch_system = messages_copy.loc[0]
        messages_copy.drop(0, inplace=True)
        self.messages = self.messages.merge(messages_copy, how='outer')
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

    def messages_describe(self) -> Dict[str, Any]:
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
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
            if json.loads(content)['action_response'].keys() >= {'function', 'arguments', 'output'}:
                return True
        except:
            return False