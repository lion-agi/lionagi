import json
from typing import Any, Optional
from lionagi.utils.sys_util import strip_lower
from lionagi.utils.nested_util import nget
from lionagi.schema import BaseNode
from lionagi.utils.nested_util import to_readable_dict


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
        return self.name
    
    @property
    def readable_content(self) -> str:
        return to_readable_dict(self.content)

    @staticmethod
    def create_system(content: Any, name: Optional[str] = None):
        return System(system=content, name=name)

    @staticmethod
    def create_instruction(content: Any, context=None, name: Optional[str] = None):
        return Instruction(instruction=content, context=context, name=name)

    @staticmethod
    def create_response(content: Any, name: Optional[str] = None):
        return Response(response=content, name=name)
    
    def _to_message(self, use_name=False):
        out = {"name": self.name} if use_name else {"role": self.role}
        out['content'] = json.dumps(self.content) if isinstance(self.content, dict) else self.content
        return out

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

    def __init__(self, system: Any, name: Optional[str] = None):
        super().__init__(role="system", name=name, content={"system_info": system})


class Instruction(Message):

    def __init__(self, instruction: Any, context=None, name: Optional[str] = None):
        super().__init__(role="user", name=name, content={"instruction": instruction})
        if context:
            self.content.update({"context": context})


class Response(Message):

    def __init__(self, response: Any, name: Optional[str] = None, content_key=None):
        try:
            response = response["message"]

            if strip_lower(response['content']) == "none":
                content_ = self._handle_action_request(response)
                name = name or "action_request"
                content_key = content_key or "action_list"

            else:
                if 'tool_uses' in json.loads(response['content']):
                    content_ = json.loads(response['content'])['tool_uses']
                    content_key = content_key or "action_list"
                    name = name or "action_request"
                else:
                    content_ = response['content']
                    content_key = content_key or "response"
                    name = name or "assistant"

        except:
            content_ = response
            name = name or "action_response"
            content_key = content_key or "action_response"

        super().__init__(role="assistant", name=name, content={content_key: content_})

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