from typing import Any, Optional
from .message import Message

class System(Message):
    
    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        self.__call__(
            role_="system", 
            content_key="system", 
            content=system, 
            name=name
        )