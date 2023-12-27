from .messages import Message


class Conversation:
    """
    A class representing a conversation between users and the assistant.

    This class manages the exchange of messages within a conversation, including system settings,
    user instructions, and assistant responses.

    Attributes:
        response_counts (int): The count of assistant responses in the conversation.
        messages (list): A list to store messages in the conversation.
        msg (Message): An instance of the Message class for creating messages.
        responses (list): A list to store assistant responses in the conversation.

    Methods:
        initiate_conversation(system, instruction, context=None, name=None):
            Initiate a conversation with a system setting and user instruction.

        add_messages(system, instruction, context=None, response=None, tool=None, name=None):
            Add messages to the conversation, including system setting, user instruction, and assistant response.

        change_system(system):
            Change the system setting in the conversation.

        keep_last_n_exchanges(n: int):
            Keep the last n exchanges in the conversation.
    """
    response_counts = 0
    
    def __init__(self, messages=None) -> None:
        """
        Initialize a Conversation object.

        Parameters:
            messages (list): A list of messages to initialize the conversation. Default is None.

        """
        self.messages = messages or []
        self.msg = Message()
        self.responses = []

    def initiate_conversation(self, system=None, instruction=None, context=None, name=None):
        """
        Initiate a conversation with a system setting and user instruction.

        Parameters:
            system (str): The system setting for the conversation.
            instruction (str): The user instruction to initiate the conversation.
            context (dict): Additional context for the conversation. Default is None.
            name (str): The name associated with the user. Default is None.
        """
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context, name=name)

    # modify the message adding to accomodate tools
    def add_messages(self, system=None, instruction=None, context=None, response=None, name=None):
        """
        Add messages to the conversation, including system setting, user instruction, and assistant response.

        Parameters:
            system (str): The system setting for the message. Default is None.
            instruction (str): The instruction content for the message. Default is None.
            context (dict): Additional context for the message. Default is None.
            response (dict): The response content for the message. Default is None.
            tool (dict): The tool information for the message. Default is None.
            name (str): The name associated with the message. Default is None.
        """
        msg = self.msg(system=system, instruction=instruction, context=context, 
                       response=response, name=name)
        self.messages.append(msg)

    def change_system(self, system):
        """
        Change the system setting in the conversation.

        Parameters:
            system (str): The new system setting for the conversation.
        """
        self.messages[0] = self.msg(system=system)

    def keep_last_n_exchanges(self, n: int):
        """
        Keep the last n exchanges in the conversation.

        Parameters:
            n (int): The number of exchanges to keep.
        """
        # keep last n_exchanges, one exchange is marked by one assistant response
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]
            