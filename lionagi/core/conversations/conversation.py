from typing import List, Any

from lionagi.schema.base_node import BaseNode
from lionagi.messages import Message, Response
from lionagi.objs.messenger import Messenger


class Conversation(BaseNode):
    """
    A conversation that handles messages and responses.

    Attributes:
        response_counts (int): A counter for the number of responses in the conversation.
        messages (List[Message]): A list of message objects in the conversation.
        msgr (Messenger): An instance of Messenger to create message objects.
        responses (List[Response]): A list of response objects in the conversation.
    """    

    response_counts : int = 0
    messages: List[Message] = []
    msgr : Any = Messenger()
    responses: List[Response] = []

    def initiate_conversation(
        self, system=None, instruction=None, 
        context=None, name=None
    ):
        """
        Initiates a new conversation, erase previous messages and responses.

        Parameters:
            system (Any, optional): System information to include in the initial message. Defaults to None.
            instruction (Any, optional): Instruction details to include in the conversation. Defaults to None.
            context (Any, optional): Contextual information relevant to the conversation. Defaults to None.
            name (str, optional): The name associated with the conversation. Defaults to None.

        Returns:
            None
        """
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context, name=name)

    # modify the message adding to accomodate tools
    def add_messages(
        self, system=None, instruction=None, 
        context=None, response=None, name=None
    ):
        """
        Adds a new message object to the conversation messages list based on the provided parameters.

        Parameters:
            system (Any, optional): System information to include in the message. Defaults to None.
            instruction (Any, optional): Instruction details to include in the message. Defaults to None.
            context (Any, optional): Contextual information relevant to the message. Defaults to None.
            response (Any, optional): Response details to include in the message. Defaults to None.
            name (str, optional): The name associated with the message. Defaults to None.

        Returns:
            None
        """
        msg = self.msgr.create_message(
            system=system, instruction=instruction, 
            context=context, response=response, name=name
        )
        self.messages.append(msg)

    def change_system(self, system):
        """
        Changes the system information of the first message in the conversation.

        Parameters:
            system (Any): The new system information to be set.

        Returns:
            None
        """
        self.messages[0] = self.msgr.create_message(system=system)


    def keep_last_n_exchanges(self, n: int):
        """
        Keeps only the last n exchanges in the conversation, where an exchange starts with a user message. This function trims the conversation to retain only the specified number of the most recent exchanges. 
        An exchange is defined as a sequence of messages starting with a user message. 
        The first message in the conversation, typically a system message, is always retained.

        Parameters:
            n (int): The number of exchanges to keep in the conversation.

        Returns:
            None: The method modifies the conversation in place and does not return a value.

        Raises:
            ValueError: If n is not a positive integer.

        Note:
            This function assumes the first message in the conversation is a system message and each user message 
            marks the beginning of a new exchange.
        """
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) 
            if message.role == "user"
        ]
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n] + 1
            self.messages = [self.system] + self.messages[first_index_to_keep:]
            