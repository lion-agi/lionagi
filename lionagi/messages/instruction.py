from typing import Any, Optional
from .message import Message

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
    