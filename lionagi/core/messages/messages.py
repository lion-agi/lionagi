import json
from typing import Any, Dict, Optional

from lionagi.utils.sys_util import strip_lower, to_dict
from lionagi.utils.nested_util import nget
from lionagi.schema import BaseNode


class Message(BaseNode):

    role: Optional[str] = None
    sender: Optional[str] = None

    @property
    def msg(self) -> Dict[str, Any]:
        return self._to_message()
        
    @property
    def msg_content(self) -> Any:
        return self.msg['content']
    
    @property
    def sender(self) -> str:
        return self.sender
    
    def _to_message(self):
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75 
            else str(self.content)
        )
        return f"Message(role={self.role}, sender={self.sender}, content='{content_preview}')"

class Instruction(Message):

    def __init__(self, instruction: Any, context=None, sender: Optional[str] = None):
        super().__init__(
            role="user", sender=sender or 'user', content={"instruction": instruction}
        )
        if context:
            self.content.update({"context": context})
            
class System(Message):

    def __init__(self, system: Any, sender: Optional[str] = None):
        super().__init__(
            role="system", sender=sender or 'system', content={"system_info": system}
        )
            
class Response(Message):
    
    def __init__(self, response: Any, sender: Optional[str] = None) -> None:
        content_key = ''
        try:
            response = response["message"]
            if strip_lower(response['content']) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or "action_request"
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in to_dict(response['content']):
                        content_ = to_dict(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or "action_request"
                    elif 'response' in to_dict(response['content']):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = to_dict(response['content'])['response']
                    elif 'action_list' in to_dict(response['content']):
                        sender = sender or "action_request"
                        content_key = content_key or "action_list"
                        content_ = to_dict(response['content'])['action_list']
                    else:
                        content_ = response['content']
                        content_key = content_key or "response"
                        sender = sender or "assistant"
                except:
                    content_ = response['content']
                    content_key = content_key or "response"
                    sender = sender or "assistant"

        except:
            sender = sender or "action_response"
            content_ = response
            content_key = content_key or "action_response"
        
        super().__init__(role="assistant", sender=sender, content={content_key: content_})
        
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
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
