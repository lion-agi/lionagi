from typing import List, Any, Union, Dict, Optional, Tuple
from lionagi.schema.base_node import BaseNode
from lionagi.utils import strip_lower, as_dict, nget, to_readable_dict, lcall
import json


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
        try:
            content_key = ''
            response = response["message"]
            content_=''
            if strip_lower(response['content']) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or "action_request"
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in json.loads(response['content']):
                        content_ = json.loads(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or "action_request"
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
            raise ValueError("Response message must be one of regular response or function calling")

        