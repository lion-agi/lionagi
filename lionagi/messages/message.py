import json
from typing import Any, Optional
from lionagi.schema import BaseNode

class Message(BaseNode):
    """
    Represents a message within a communication system, extending from BaseNode.

    This class encapsulates the details of a message, including its role, content, and name. 
    It provides methods to manipulate and retrieve message information.

    Attributes:
        role (Optional[str]): The role associated with the message (e.g., 'user', 'system'). Defaults to None.
        name (Optional[str]): The name associated with the message, often reflecting the role. Defaults to None.

    Properties:
        message: Returns the message as a dictionary including role and content.
        message_content: Returns only the content part of the message.

    Methods:
        to_message: Converts the message object into a dictionary format.
        create_role_message: Sets the role, content, and name of the message.
        get_role: Retrieves the role of the message, formatted as a lowercase string.
        get_name: Retrieves the name of the message, formatted as a lowercase string.
    """

    role: Optional[str] = None
    name: Optional[str] = None
    
    @property
    def message(self):
        """
        Property that returns the message as a dictionary.

        Returns:
            dict: A dictionary representation of the message with 'role' and 'content'.
        """
        return self._to_message()
    
    @property
    def message_content(self):
        """
        Property that returns the content part of the message.

        Returns:
            Any: The content of the message.
        """
        return self.message['content']
    
    def _to_message(self):
        """
        Converts the message object into a dictionary format, including role and content.

        Returns:
            dict: A dictionary with 'role' and 'content' keys.
        """
        out = {
            "role": self.role,
            "content": json.dumps(self.content) if isinstance(self.content, dict) else self.content
            }
        return out

    def _create_roled_message(
        self, role_: str, content: Any, content_key: str, 
        name: Optional[str] = None
    ) -> None:
        """
        Sets the role, content, and name of the message.

        Parameters:
            role_ (str): The role to assign to the message.
            content (Any): The content of the message.
            content_key (str): The key under which the content is stored.
            name (Optional[str]): The name associated with the message. Defaults to the role if not provided.
        """
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_

    def get_role(self):
        """
        Retrieves the role of the message, formatted as a lowercase string.

        Returns:
            str: The message's role in lowercase.
        """
        return str(self.role).strip().lower()
    
    def get_name(self):
        """
        Retrieves the name of the message, formatted as a lowercase string.

        Returns:
            str: The message's name in lowercase.
        """
        return str(self.name).strip().lower()
        
    def __str__(self):
        """
        Informal string representation of Message object, intended to be readable.
        Includes role, name, and a brief preview of the content.
        """
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75 
            else str(self.content)
        )
        return f"Message(role={self.role}, name={self.name}, content='{content_preview}')"


    