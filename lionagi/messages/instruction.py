from typing import Any, Optional
from ..done_.message import Message

class Instruction(Message):
    """
    Represents an instruction, which is a specific type of message with additional attributes like priority and execution status.

    Inherits from Message.

    Attributes:
        priority (Optional[int]): Priority level of the instruction.
        execution_status (Optional[str]): Current execution status of the instruction.
    """
    priority: Optional[int] = None
    execution_status: Optional[str] = None

    def _create_message(self, instruction: Any, context=None, name: Optional[str] = None) -> None:
        """
        Initializes an Instruction instance.

        Args:
            instruction (Any): The instruction content.
            context (Optional): Additional context for the instruction.
            name (Optional[str]): Name of the sender.
            priority (Optional[int]): Priority of the instruction.
            execution_status (Optional[str]): Execution status of the instruction.
        """
        super().__call__(
            role_="user", 
            content_key="instruction", 
            content=instruction, 
            name=name
        )
        if context:
            self.content.update({"context": context})

    def set_priority(self, priority: int):
        """
        Sets the priority of the instruction.

        Args:
            priority (int): The priority level to set.
        """
        self.priority = priority
    
    def get_priority(self):
        """
        Gets the priority of the instruction.

        Returns:
            Optional[int]: The priority of the instruction.
        """
        return self.priority
    
    def set_execution_status(self, status: str):
        """
        Sets the execution status of the instruction.

        Args:
            status (str): The execution status to set.
        """
        self.execution_status = status
    
    def get_execution_status(self):
        """
        Gets the execution status of the instruction.

        Returns:
            Optional[str]: The execution status of the instruction.
        """
        return self.execution_status



class System(Message):
    
    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        self.__call__(
            role_="system", 
            content_key="system", 
            content=system, 
            name=name
        )

# filename: instruction_system.py
import json
from typing import Any, Optional, List
from ..done_.messages import Message

class System(Message):
    system_status: Optional[str] = None
    system_logs: List[str] = []

    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        super().__call__(
            role_="system", 
            content_key="system", 
            content=system, 
            name=name
        )

    def set_system_status(self, status: str):
        self.system_status = status
    
    def get_system_status(self):
        return self.system_status
    
    def log_event(self, event: str):
        self.system_logs.append(event)
    
    def get_system_logs(self):
        return self.system_logs
    
    def clear_system_logs(self):
        self.system_logs = []