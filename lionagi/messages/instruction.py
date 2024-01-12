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
            