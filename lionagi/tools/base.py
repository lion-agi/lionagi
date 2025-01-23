"""System Tool Interface for Lionagi"""

from abc import ABC, abstractmethod
from enum import Enum

from lionagi.operatives.action.tool import Tool


class LionTool(ABC):
    is_lion_system_tool: bool = True
    system_tool_name: str

    @abstractmethod
    def to_tool(self) -> Tool:
        pass


class ToolAction(str, Enum):
    """
    This enumeration indicates the *type* of action the LLM wants to perform.
    Must be implemented by all tools.
    """
