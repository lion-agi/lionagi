from enum import Enum

from lionagi.core.schema.base_node import BaseNode


class ActionSelection(BaseNode):

    def __init__(self, action: str = "chat", action_kwargs={}):
        super().__init__()
        self.action = action
        self.action_kwargs = action_kwargs


class ActionNode(BaseNode):

    def __init__(self, instruction, action: str = "chat", tools=[], action_kwargs={}):
        super().__init__()
        self.instruction = instruction
        self.action = action
        self.tools = tools
        self.action_kwargs = action_kwargs
