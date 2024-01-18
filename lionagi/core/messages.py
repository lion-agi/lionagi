import json
from typing import Any, Optional, Dict
from ..utils.sys_util import strip_lower, as_dict
from ..utils.nested_util import nget, to_readable_dict
from ..schema import BaseNode


class Message(BaseNode):
    """
    Represents a message with associated role, name, and content.

    Attributes:
        role (Optional[str]): The role of the entity sending the message.
        name (Optional[str]): The name of the entity sending the message.
        content (Any): The content of the message.
    """
    
    role: Optional[str] = None
    name: Optional[str] = None
    
    @property
    def msg(self) -> Dict[str, Any]:
        """The message as a dictionary.

        Returns:
            Dict[str, Any]: The message in dictionary form with 'role' or 'name' as a key.
        """
        return self._to_message()
        
    @property
    def named_msg(self) -> Dict[str, Any]:
        """The message as a dictionary with the sender's name.

        Returns:
            Dict[str, Any]: The message in dictionary form with 'name' as a key.
        """
        return self._to_message(use_name=True)
    
    @property
    def msg_content(self) -> Any:
        """The content of the message.

        Returns:
            Any: The content of the message.
        """
        return self.msg['content']
    
    @property
    def sender(self) -> str:
        """The name of the sender of the message.

        Returns:
            Optional[str]: The name of the sender.
        """
        return self.name
    
    @property
    def readable_content(self) -> str:
        """The content of the message in a human-readable format.

        Returns:
            str: The message content as a human-readable string.
        """
        return to_readable_dict(self.content)

    @staticmethod
    def create_system(content: Any, name: Optional[str] = None):
        """Create a system message.

        Args:
            content (Any): The content of the system message.
            name (Optional[str]): The name of the system.

        Returns:
            System: The created system message.
        """
        return System(system=content, name=name)

    @staticmethod
    def create_instruction(
        content: Any, context: Optional[Any] = None, name: Optional[str] = None
    ) -> "Instruction":
        """Create an instruction message.

        Args:
            content (Any): The content of the instruction.
            context (Optional[Any]): Additional context for the instruction.
            name (Optional[str]): The name of the sender.

        Returns:
            Instruction: The created instruction message.
        """
        return Instruction(instruction=content, context=context, name=name)

    @staticmethod
    def create_response(content: Any, name: Optional[str] = None) -> "Response":
        """Create a response message.

        Args:
            content (Any): The content of the response.
            name (Optional[str]): The name of the sender.

        Returns:
            Response: The created response message.
        """
        return Response(response=content, name=name)
    
    def _to_message(self, use_name: bool = False) -> Dict[str, Any]:
        """Convert the message to a dictionary.

        Args:
            use_name (bool): Whether to use the sender's name as a key.

        Returns:
            Dict[str, Any]: The message in dictionary form.
        """
        out = {"name": self.name} if use_name else {"role": self.role}
        out['content'] = json.dumps(self.content) if isinstance(self.content, dict) else self.content
        return out

    def to_plain_text(self) -> str:
        """Convert the message content to plain text.

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
        """String representation of the Message object.

        Returns:
            str: The string representation of the message.
        """
        content_preview = self.to_plain_text()[:75] + "..." if len(self.to_plain_text()) > 75 else self.to_plain_text()
        return f"Message(role={self.role}, name={self.name}, content='{content_preview}')"


class System(Message):
    """Represents a system message."""

    def __init__(self, system: Any, name: Optional[str] = None):
        """Initialize the System message.

        Args:
            system (Any): The content of the system message.
            name (Optional[str]): The name of the system.
        """
        super().__init__(role="system", name=name or 'system', content={"system_info": system})


class Instruction(Message):
    """Represents an instruction message."""

    def __init__(self, instruction: Any, context=None, name: Optional[str] = None):
        """Initialize the Instruction message.

        Args:
            instruction (Any): The content of the instruction.
            context (Optional[Any]): Additional context for the instruction.
            name (Optional[str]): The name of the sender.
        """

        super().__init__(role="user", name=name or 'user', content={"instruction": instruction})
        if context:
            self.content.update({"context": context})




class Response(Message):

    def __init__(self, response: Any, name: Optional[str] = None, content_key=None) -> None:
        try:
            response = response["message"]

            if strip_lower(response['content']) == "none":
                content_ = self._handle_action_request(response)
                name = name or "action_request"
                content_key = content_key or "action_list"

            else:
                try:
                    if 'tool_uses' in json.loads(response['content']):
                        content_ = json.loads(response['content'])['tool_uses']
                        content_key = content_key or "action_list"
                        name = name or "action_request"
                    else:
                        content_ = response['content']
                        content_key = content_key or "response"
                        name = name or "assistant"
                except:
                    content_ = response['content']
                    content_key = content_key or "response"
                    name = name or "assistant"

        except:
            name = name or "action_response"
            content_ = response
            content_key = content_key or "action_response"
        
        super().__init__(role="assistant", name=name, content={content_key: content_})
        
    @staticmethod
    def _handle_action_request(response):
        """Handle an action request from the response.

        Args:
            response (Dict[str, Any]): The response dictionary containing the action request.

        Returns:
            List[Dict[str, Any]]: The list of actions parsed from the request.

        Raises:
            ValueError: If the response does not contain valid function calling information.
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
            raise ValueError("Response message must be one of regular response or function calling")

