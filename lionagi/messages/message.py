import json
from typing import Any, Optional
from lionagi.utils.nested_util import flatten
from lionagi.schema import BaseNode

class Message(BaseNode):
    """
    Represents a message in a conversation, encapsulating details like role, name, content, and attachments.

    Attributes:
        role (Optional[str]): Role of the message sender (e.g., 'user', 'system').
        name (Optional[str]): Name of the message sender.
        attachments (List[str]): List of attachments associated with the message.

    Methods:
        _to_message: Internal method to format the message content.
        __call__: Class method to create a new Message instance.
        role_msg: Property to get the message with role information.
        name_msg: Property to get the message with name information.
        msg_content: Property to get the content of the message.
        msg_content_flattened: Property to get flattened content of the message.
        get_role: Gets the role of the message sender.
        set_role: Sets the role of the message sender.
        set_name: Sets the name of the message sender.
        get_name: Gets the name of the message sender.
        __str__: String representation of the message.
    """
    
    role: Optional[str] = None
    name: Optional[str] = None
    def _to_message(self, use_name=False, name=None):
        """
        Formats the message content along with additional details like role, name, or attachments.

        Args:
            use_name (bool, optional): Flag to include name in the message. Defaults to False.
            name (Optional[str], optional): Name to be used in the message. Defaults to None.

        Returns:
            Dict[str, Any]: Formatted message as a dictionary.
        """
        out = {"content": json.dumps(self.content) if isinstance(self.content, dict) else self.content}
        if use_name:
            out.update({"name": name or self.name})
        else:
            out.update({"role": self.role})
        if self.attachments:
            out.update({"attachments": self.attachments})
        return out
    
    @classmethod
    def __call__(
        cls,
        role_: str, 
        content: Any, 
        content_key: str, 
        name: Optional[str] = None
    ) -> 'Message':
        """
        Class method to create and initialize a new Message instance.

        Args:
            role_ (str): Role of the message sender.
            content (Any): Content of the message.
            content_key (str): Key to associate with the content.
            name (Optional[str], optional): Name of the message sender. Defaults to role_ if not provided.

        Returns:
            Message: An instance of the Message class.
        """        
        self = cls()
        self.role = role_
        self.content = {content_key: content}
        self.name = name or role_
        return self

    @property
    def role_msg(self):
        """
        Property to get the message formatted with role information.

        Returns:
            Dict[str, Any]: Formatted message with role.
        """
        return self._to_message()
        
    @property
    def name_msg(self):
        """
        Property to get the message formatted with name information.

        Returns:
            Dict[str, Any]: Formatted message with name.
        """
        return self._to_message(use_name=True)
        
    @property
    def msg_content(self):
        """
        Property to get the content of the message.

        Returns:
            Any: The content of the message.
        """
        return self._to_message()['content']

    @property
    def msg_content_flattened(self):
        """
        Property to get the flattened content of the message.

        Returns:
            Any: The flattened content of the message.
        """
        return flatten(self.msg_content)

    def get_role(self):
        """
        Gets the role of the message sender.

        Returns:
            str: The role of the message sender.
        """
        return str(self.role).strip().lower()
    
    def set_role(self, role):
        """
        Sets the role of the message sender.

        Args:
            role (str): The role to set for the message sender.
        """
        self.role = role
        
    def set_name(self, name):
        """
        Sets the name of the message sender.

        Args:
            name (str): The name to set for the message sender.
        """
        self.name = name
    
    def get_name(self):
        """
        Gets the name of the message sender.

        Returns:
            str: The name of the message sender.
        """
        return str(self.name).strip().lower()
        
    def __str__(self):
        content_preview = (
            (str(self.content)[:75] + '...') if self.content and len(self.content) > 75 
            else str(self.content)
        )
        return f"Message(role={self.role}, name={self.name}, content='{content_preview}')"
    