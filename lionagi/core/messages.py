import json
from typing import Any, Optional
from lionagi.utils.sys_util import strip_lower
from lionagi.utils.nested_util import nget
from lionagi.schema import BaseNode

class Message(BaseNode):
    role: Optional[str] = None
    name: Optional[str] = None
    
    @property
    def msg(self):
        return self._to_message()
        
    @property 
    def named_msg(self):
        return self._to_message(use_name=True)
    
    @property
    def msg_content(self):
        return self.msg['content']
    
    @property
    def sender(self):
        return self._get_name()
    
    @property
    def readable_content(self) -> str:
        return json.dumps(self.content, indent=4) if isinstance(self.content, dict) else str(self.content)

    @classmethod
    def create_system_message(cls, content: Any) -> 'System':
        return System(content=content, role='system')

    @classmethod
    def create_instruction_message(cls, content: Any) -> 'Instruction':
        return Instruction(content=content, role='user')

    @classmethod
    def create_response_message(cls, content: Any) -> 'Response':
        return Response(content=content, role='assistant')
    
    def _to_message(self, use_name=False):
        out = {"name": self.name} if use_name else {"role": self.role}
        out['content'] = json.dumps(self.content) if isinstance(self.content, dict) else self.content
        return out

    def _create_roled_message(
        self, role_: str, content: Any, content_key: str, 
        name: Optional[str] = None
    ) -> None:
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_
    
    def _get_name(self):
        return strip_lower(self.name)
        
    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75 
            else str(self.content)
        )
        return f"Message(role={self.role}, name={self.name}, content='{content_preview}')"

    def to_plain_text(self) -> str:
        """
        Returns the plain text representation of the message content.

        Returns:
            str: The plain text content of the message.
        """
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, dict):
            return json.dumps(self.content)
        elif self.content is None:
            return ""
        else:
            return str(self.content)

    def __str__(self) -> str:
        content_preview = self.to_plain_text()[:75] + "..." if len(self.to_plain_text()) > 75 else self.to_plain_text()
        return f"Message(role={self.role}, name={self.name}, content='{content_preview}')"


class System(Message):
    
    def _create_message(self, system: Any, name: Optional[str] = None) -> None:
        self._create_roled_message(
            role_="system", 
            content_key="system_info", 
            content=system, 
            name=name
        )
    
    @property
    def is_system(self) -> bool:
        return self.role == 'system'

    @property
    def is_user():
        return False
    
    @property
    def is_assistant():
        return False
        
class Instruction(Message):

    def _create_message(self, instruction: Any, context=None ,name: Optional[str] = None) -> None:
        self._create_roled_message(
            role_="user", 
            content_key="instruction", 
            content=instruction, 
            name=name
        )
        if context: 
            self.content.update({"context": context})

    @property
    def is_system():
        return False

    @property
    def is_user(self) -> bool:
        return self.role == 'user'
    
    @property
    def is_assistant():
        return False
    
class Response(Message):

    @property
    def is_system():
        return False

    @property
    def is_user():
        return False
    
    @property
    def is_assistant(self) -> bool:
        return self.role == 'assistant'
    
    def _create_message(self, response: Any, name: Optional[str] = None, content_key=None) -> None:
        role_ = "assistant"
        content_ = ''
        
        try:
            response = response["message"]

            if strip_lower(response['content']) == "none":
                content_ = self._handle_action_request(response)
                name = name or "action_request"
                content_key = content_key or "action_list"

            else:
                content_ = response['content']
                content_key = content_key or "response"
                name = name or "assistant"

        except:
            content_ = response
            name = name or "action_response"
            content_key = content_key or "action_response"

        self._create_roled_message(
                role_=role_, 
                content_key=content_key, 
                content=content_, 
                name=name
            )

    @staticmethod
    def _handle_action_request(response):
        try:
            tool_count = 0
            func_list = []
            while tool_count < len(response['tool_calls']):
                _path = ['tool_calls', tool_count, 'type']
                
                if nget(response, _path) == 'function':
                    _path1 = ['tool_calls', tool_count, 'function', 'name']
                    _path2 = ['tool_calls', tool_count, 'function', 'arguments']
                    
                    func_content = {
                        "action": ("action_" + nget(response, _path1)),
                        "arguments": nget(response, _path2)
                        }
                    func_list.append(func_content)
                tool_count += 1
            return func_list
        except:
            raise ValueError("Response message must be one of regular response or function calling")