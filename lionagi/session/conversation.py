from .message import Message

class Conversation:
    """
    A class modeling conversations and managing messages within the conversation.

    This class facilitates the organization and manipulation of messages in a conversation.
    It includes methods for initiating a conversation, adding messages, changing the system message,
    appending the last response, and keeping the last N exchanges.

    Attributes:
        response_counts: A class-level attribute to track the number of responses.
        messages: A list containing messages in the conversation.
        msg: An instance of the Message class for creating and processing messages.
        responses: A list containing response messages.

    Methods:
        initiate_conversation: Start a new conversation with system and user instructions.
        add_messages: Add messages to the conversation.
        change_system: Change the system message in the conversation.
        append_last_response: Append the last response to the conversation.
        keep_last_n_exchanges: Keep only the last N exchanges in the conversation.
    """
    
    response_counts = 0
    
    def __init__(self, messages=None) -> None:
        """
        Initialize a Conversation object.

        Args:
            messages: A list of messages to initialize the conversation.
        """
        self.messages = messages or []
        self.msg = Message()
        self.responses = []

    def initiate_conversation(self, system, instruction, context=None):
        """
        Start a new conversation with a system message and an instruction.

        Args:
            system: The content of the system message.
            instruction: The content of the user instruction.
            context: Additional context for the user instruction.
        """
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(self, system=None, instruction=None, context=None, response=None):
        """
        Add messages to the conversation.

        Args:
            system: The content of the system message.
            instruction: The content of the user instruction.
            context: Additional context for the user instruction.
            response: The content of the assistant's response.
        """
        msg = self.msg(system=system, instruction=instruction, response=response, context=context)
        self.messages.append(msg)

    def change_system(self, system):
        """
        Change the system message in the conversation.

        Args:
            system: The new content for the system message.
        """
        self.messages[0] = self.msg(system=system)

    def append_last_response(self):
        """
        Append the last response to the conversation.
        """
        self.add_messages(response=self.responses[-1])

    def keep_last_n_exchanges(self, n: int):
        """
        Keep only the last N exchanges in the conversation.

        Args:
            n: The number of exchanges to keep.
        """
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]