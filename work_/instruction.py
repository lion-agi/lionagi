from typing import Any, Optional
from .message import Message

class Instruction(Message):

    def _create_message(self, instruction: Any, context=None ,name: Optional[str] = None) -> None:
        self.__call__(
            role_="user", 
            content_key="instruction", 
            content=instruction, 
            name=name
        )
        if context: 
            self.content.update({"context": context})


class Instruction(Message):
    priority: Optional[int] = None
    execution_status: Optional[str] = None

    def _create_message(self, instruction: Any, context=None, name: Optional[str] = None) -> None:
        super().__call__(
            role_="user", 
            content_key="instruction", 
            content=instruction, 
            name=name
        )
        if context:
            self.content.update({"context": context})

    def set_priority(self, priority: int):
        self.priority = priority
    
    def get_priority(self):
        return self.priority
    
    def set_execution_status(self, status: str):
        self.execution_status = status
    
    def get_execution_status(self):
        return self.execution_status
    
    def add_context(self, context: dict):
        if self.content is None:
            self.content = {}
        if 'context' in self.content:
            self.content['context'].update(context)
        else:
            self.content['context'] = context
