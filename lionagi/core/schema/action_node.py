from enum import Enum

from .base_node import BaseNode


class ActionSelection(BaseNode):

    def __init__(self, action: str = "chat", action_kwargs=None):
        if action_kwargs is None:
            action_kwargs = {}
        super().__init__()
        self.action = action
        self.action_kwargs = action_kwargs


class ActionNode(BaseNode):

    def __init__(
        self, instruction, action: str = "chat", tools=None, action_kwargs=None
    ):
        if tools is None:
            tools = []
        if action_kwargs is None:
            action_kwargs = {}
        super().__init__()
        self.instruction = instruction
        self.action = action
        self.tools = tools
        self.action_kwargs = action_kwargs
