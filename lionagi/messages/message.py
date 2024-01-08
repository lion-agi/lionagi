import json
from typing import Any, Optional
from ..schema import BaseNode

class Message(BaseNode):

    role: Optional[str] = None
    name: Optional[str] = None
    
    @property
    def message(self):
        return self.to_message()
    
    @property
    def message_content(self):
        return self.message['content']
    
    def to_message(self):
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def create_role_message(
        self, 
        role_: str, 
        content: Any, 
        content_key: str, 
        name: Optional[str] = None
    ) -> None:
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_

    def get_role(self):
        return str(self.role).strip().lower()
    
    def get_name(self):
        return str(self.name).strip().lower()
        
    def __str__(self) -> str:
        ...
        
    def __repr__(self) -> str:
        ...
    