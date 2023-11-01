import json

class Message:
    """
    Represents a single message in a conversation, which can be a system message,
    an instruction, or a response.
    
    Attributes:
        role (str): The role associated with the message. Can be 'system', 'user', or 'assistant'.
        content (Any): The content of the message. This can be any data structure.
    Methods:
        _create_message: Internal method to populate the `role` and `content` attributes.
        __call__: Creates a dictionary representation of the message when the object is called.
    Sample Usages:
        ```python
        # Create a system message
        msg = Message()
        print(msg(system="System maintenance scheduled."))
        
        # Create a user instruction message with context
        msg = Message()
        print(msg(instruction="Open file.", context={"filename": "example.txt"}))
        
        # Create an assistant response message
        msg = Message()
        print(msg(response={"content": "File opened successfully."}))
        ```
    """
    
    def __init__(self, role=None, content=None) -> None:
        self.role = role
        self.content = content

    def _create_message(
        self, system=None, response=None, instruction=None, context=None):
        """
        Internal method to set the `role` and `content` attributes based on the provided parameters.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Raises:
            ValueError: If more than one role is provided for a single message.
        """
        
        if (system and (response or instruction)) or (response and instruction):
            raise ValueError("Error: Message cannot have more than one role.")
        else:
            if response:
                self.role = "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                if context:
                    for k, v in context.items():
                        self.content[k] = v
            elif system:
                self.role = "system"
                self.content = system

    def __call__(self, system=None, response=None, instruction=None, context=None):
        """
        Converts the Message object to a dictionary representation when the object is called.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Returns:
            dict: A dictionary representation of the Message object.
        """

        self._create_message(
            system=system, response=response, instruction=instruction, context=context
        )
        if self.role == "assistant":
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": json.dumps(self.content)}

massenger = Message()