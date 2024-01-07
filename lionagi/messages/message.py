import json
from typing import Any, Optional
from ..schema import BaseNode

class Message(BaseNode):

    role: Optional[str] = None
    name: Optional[str] = None
    
    def _to_message(self):
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def _create_role_message(
        self, role_: str, 
        content: Any, 
        content_key: str, 
        name: Optional[str] = None
    ) -> None:
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_


