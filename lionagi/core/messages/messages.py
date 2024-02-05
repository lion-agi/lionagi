from typing import Any, Dict, Optional
from lionagi.schema.base_node import BaseNode

from lionagi.utils.sys_util import strip_lower
from lionagi.utils.nested_util import nget

import json


class Message(BaseNode):
    """
    Represents a message in a chatbot-like system, inheriting from BaseNode.
    
    Attributes:
        role (Optional[str]): The role of the entity sending the message, e.g., 'user', 'system'.
        sender (Optional[str]): The identifier of the sender of the message.
        content (Any): The actual content of the message.
    """


    role: Optional[str] = None
    sender: Optional[str] = None

    @property
    def msg(self) -> Dict[str, Any]:
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
            A dictionary representation of the message with 'role' and 'content' keys.
        """
        return self._to_message()
        
    @property
    def msg_content(self) -> Any:
        """
        Gets the 'content' field of the message.

        Returns:
            The 'content' part of the message.
        """
        return self.msg['content']
    
    @property
    def sender(self) -> str:
        return self.sender
    
    def _to_message(self):
        """
        Constructs and returns a dictionary representation of the message.

        Returns:
            dict: A dictionary representation of the message with 'role' and 'content' keys.
        """
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
    """
    Represents an instruction message, a specialized subclass of Message.

    This class is specifically used for creating messages that are instructions from the user,
    including any associated context. It sets the message role to 'user'.
    """

    def __init__(self, instruction: Any, context=None, sender: Optional[str] = None):
        super().__init__(
            role="user", sender=sender or 'user', content={"instruction": instruction}
        )
        if context:
            self.content.update({"context": context})
            
class System(Message):
    """
    Represents a system-related message, a specialized subclass of Message.

    Designed for messages containing system information, this class sets the message role to 'system'.
    """
    def __init__(self, system: Any, sender: Optional[str] = None):
        super().__init__(
            role="system", sender=sender or 'system', content={"system_info": system}
        )
            
class Response(Message):
    """
    Represents a response message, a specialized subclass of Message.

    Used for various types of response messages including regular responses, action requests,
    and action responses. It sets the message role to 'assistant'.

    """

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
                    if 'tool_uses' in json.loads(response['content']):
                        content_ = json.loads(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or "action_request"
                    elif 'response' in json.loads(response['content']):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = json.loads(response['content'])['response']
                    elif 'action_list' in json.loads(response['content']):
                        sender = sender or "action_request"
                        content_key = content_key or "action_list"
                        content_ = json.loads(response['content'])['action_list']
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
        """
        Processes an action request response and extracts relevant information.

        Args:
            response (dict): The response dictionary containing tool calls and other information.

        Returns:
            list: A list of dictionaries, each representing a function call with action and arguments.

        Raises:
            ValueError: If the response does not conform to the expected format for action requests.
        """
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
