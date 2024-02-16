import json
from typing import Any, Dict, Optional
import pandas as pd

from lionagi.utils.sys_util import strip_lower, to_dict
from lionagi.utils.nested_util import nget
from lionagi.schema import BaseNode
from .message_schema import MessageField, MessageContentKey, MessageRoleType, MessageSenderType


class BaseMessage(BaseNode):

    _role = None
    _sender = None
    recipient = None
    timestamp = None

    @property
    def role(self):
        return self._role
    
    @role.setter
    def role(self, role):
        self._role = role
    
    @property
    def content_str(self):
        if isinstance(self.content, Dict):
            return json.dumps(self.content)
        elif isinstance(self.content, str):
            return self.content
        else:
            try:
                return str(self.content)
            except:
                return 'null'
                                              
    @property
    def dict(self):
        return {
            'node_id': self.id_,
            'metadata': self.metadata or 'null',
            'timestamp': self.timestamp,
            'labels': self.label or 'null', 
            'role': self.role,
            'sender': self._sender,
            'recipient': self.recipient,
            'content': self.content_str,
            'related_nodes': self.related_nodes or 'null'
        }
    
    @property
    def to_pd_series(self):
        return pd.Series(self.dict)
    
    
    @property
    def sender(self):
        return self._sender
    
    @sender.setter
    def sender(self, sender):
        self._sender = sender
    
    
    
    
    
    @property
    def msg_sender(self) -> str:
        """
        Retrieves the sender identifier of the message.

        Returns:
            The identifier of the message sender.
        """
        return self.roled_msg[MessageField.SENDER.value]
    
    @property
    def msg_recipient(self) -> str:
        """
        Retrieves the recipient identifier of the message.

        Returns:
            The identifier of the message recipient.
        """
        return self.roled_msg[MessageField.RECIPIENT.value]

    @property
    def msg_timestamp(self) -> Any:
        """
        Retrieves the timestamp of the message.

        Returns:
            The timestamp marking when the message was created or sent.
        """
        return self.roled_msg[MessageField.TIMESTAMP.value]

    @property
    def as_pd_series(self) -> pd.Series:
        """
        Converts the message to a pandas Series object, facilitating data analysis and manipulation.

        Returns:
            A pandas Series object representing the structured message data.
        """
        return pd.Series(self.roled_msg)





    def add_recipient(self, recipient: str) -> None:
        """
        Updates the recipient identifier for the message.

        Args:
            recipient: The new recipient identifier to be assigned to the message.
        """
        self.recipient = recipient


    def _to_roled_message(self):
        """
        Serializes the message attributes into a dictionary, using `MessageField` enum values as keys.

        Returns:
            A dictionary representation of the message, suitable for serialization or further processing.
        """
        return {
            MessageField.ROLE.value: self._role.value,
            MessageField.CONTENT.value: (
                json.dumps(self.content) if isinstance(self.content, dict) 
                else self.content
            )
        }


            

    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75 
            else str(self.content)
        )
        return (
            f"Message({MessageField.ROLE.value}={self._role.value or 'none'}, \
                {MessageField.SENDER.value}={self._sender or 'none'}, \
                {MessageField.CONTENT.value}='{content_preview or 'none'}, \
                {MessageField.RECIPIENT.value}={self.recipient or 'none'}, \
                {MessageField.TIMESTAMP.value}={self.timestamp or 'none'})"
            )

class Instruction(BaseMessage):
    
    """
    Represents an instruction message, typically used to convey actions or commands.

    This class is intended for messages that carry instructions from users or automated
    systems, possibly including a context for the instruction.

    Args:
        instruction (Any): The main instruction or command this message is carrying.
        context (Optional[Any], optional): Additional context or parameters for the instruction.
        sender (Optional[str], optional): The identifier for the entity sending the instruction.
            Defaults to the role type converted to string if not specified.

    Attributes are inherited from `BaseMessage`.
    """

    def __init__(self, instruction: Any, context=None, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.USER.value, 
            sender=sender or MessageSenderType.USER.value, 
            content={MessageContentKey.INSTRUCTION.value: instruction}
        )
        if context:
            self.content.update({'context': context})
            
class System(BaseMessage):
    """
    Represents a system message, typically used to convey system-level information or status.

    This class is intended for messages that originate from or are about the system's internal
    processes, configurations, or states.

    Args:
        system (Any): The main content or information this message is carrying about the system.
        sender (Optional[str], optional): The identifier for the entity sending the system message.
            Defaults to the role type converted to string if not specified.

    Attributes are inherited from `BaseMessage`.
    """

    def __init__(self, system: Any, sender: Optional[str] = None):
        super().__init__(
            role=MessageRoleType.SYSTEM.value, 
            sender=sender or MessageSenderType.SYSTEM.value, 
            content={MessageContentKey.SYSTEM.value: system}
        )

            
class Response(BaseMessage):
    
    def __init__(self, response: Any, sender: Optional[str] = None) -> None:
        content_key = ''
        try:
            response = response["message"]
            if strip_lower(response[MessageField.CONTENT]) == "none":
                content_ = self._handle_action_request(response)
                sender = sender or MessageSenderType.ACTION_REQUEST
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in to_dict(response['content']):
                        content_ = to_dict(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        sender = sender or MessageSenderType.ACTION_REQUEST
                    elif 'response' in to_dict(response['content']):
                        sender = sender or "assistant"
                        content_key = content_key or "response"
                        content_ = to_dict(response['content'])['response']
                    elif 'action_list' in to_dict(response['content']):
                        sender = sender or MessageSenderType.ACTION_REQUEST
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
        
        super().__init__(
            role=MessageRoleType.ASSISTANT, sender=sender, content={content_key: content_}
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
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )
