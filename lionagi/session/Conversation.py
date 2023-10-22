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
        to_dict: Creates a dictionary representation of the message.
    """

    def __init__(self, role=None, content=None) -> None:
        self.role = role
        self.content = content

    def _create_message(
        self, system=None, response=None, instruction=None, context=None
    ):
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
                    for key, item in context.items():
                        self.content[key] = item
            elif system:
                self.role = "system"
                self.content = system

    def to_dict(self, system=None, response=None, instruction=None, context=None):
        """
        Converts the Message object to a dictionary representation.

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

class Conversation:
    """
    Manages a conversation consisting of multiple messages.

    Attributes:
        response_counts (int): A class-level counter for responses.
        messages (list): A list of messages in the conversation.
        system (str): System-related message.
        responses (list): A list to store responses.
        message (Message): An instance of the Message class to handle individual messages.

    Methods:
        initiate_conversation: Initializes a new conversation.
        add_messages: Adds a new message to the conversation.
        change_system: Changes the system message.
        append_last_response: Adds the last response to the list of messages.
    """

    response_counts = 0

    def __init__(self, system, messages=[]) -> None:
        self.messages = messages
        self.system = system
        self.responses = []
        self.message = Message()

    def initiate_conversation(self, system, instruction, context=None):
        """
        Initializes a new conversation by setting the initial system and instruction messages.

        Args:
            system (str): The initial system message.
            instruction (str): The initial instruction from the user.
            context (dict, optional): Additional context for the instruction. Defaults to None.
        """
        self.messages = []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(
        self, system=None, instruction=None, context=None, response=None
    ):
        """
        Adds a new message to the conversation.

        Args:
            system (str, optional): System-related message. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
        """
        message = self.message.to_dict(
            system=system, response=response, instruction=instruction, context=context
        )
        self.messages.append(message)

    def change_system(self, system):
        """
        Changes the initial system message.

        Args:
            system (str): The new system message.
        """
        self.system = system
        self.messages[0] = self.message.to_dict(system=system)

    def append_last_response(self):
        """
        Appends the last response to the list of messages.
        """
        self.add_messages(response=self.responses[-1])