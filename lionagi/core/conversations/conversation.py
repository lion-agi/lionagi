from typing import Any, List, Optional
from lionagi.schema.base_node import BaseNode
from lionagi.messages import Message, Response
from lionagi.objs.messenger import Messenger


class Conversation:
    """
    Represents a conversation, encapsulating messages and responses, 
    and providing functionalities for managing and analyzing the conversation flow.

    Attributes:
        response_counts (int): Counter for the number of responses.
        messages (List[Message]): List of messages in the conversation.
        msgr (Messenger): Messenger object to create and parse messages.
        responses (List[Response]): List of responses in the conversation.

    Methods:
        initiate_conversation: Initializes a new conversation.
        add_messages: Adds messages to the conversation.
        change_system: Changes the system message at the beginning of the conversation.
        keep_last_n_exchanges: Keeps only the last 'n' exchanges in the conversation.
        last_messages: Retrieves the last 'n' messages from the conversation.
        set_messages: Sets the conversation's messages.
        search_messages: Searches for messages containing a specific keyword.
        rate_conversation: Assigns a rating to the conversation.
        get_last_response: Gets the last response in the conversation.
        delete_message: Deletes a message at a specified index.
    """    

    response_counts: int = 0
    
    def __init__(self, messages=None) -> None:
        self.messages = messages
        self.msgr = Messenger()
        self.responses = []

    def initiate_conversation(
        self, system=None, instruction=None, 
        context=None, name=None
    ):
        """
        Initializes a new conversation by resetting messages and responses, 
        and optionally adding initial messages.
        """
        self.messages, self.responses = [], []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context, name=name)

    def add_messages(
        self, system=None, instruction=None, 
        context=None, response=None, name=None
    ):
        """
        Adds a new message to the conversation based on provided parameters.
        """
        msg = self.msgr.create_message(
            system=system, instruction=instruction, 
            context=context, response=response, name=name
        )
        self.messages.append(msg)

    @property
    def message_counts(self):
        return len(self.messages)

    @property
    def last_message(self):
        return self.messages[-1]

    def change_system(self, system):
        """
        Changes the system message at the beginning of the conversation.
        """
        self.messages[0] = self.msgr.create_message(system=system)
        
    def organize_messages(self, n: int, get_last_response: bool = False, verbose: bool = False):
        """
        Manages the conversation by keeping only the last 'n' exchanges and optionally retrieving the last response.

        Args:
            n (int): Number of exchanges (user responses) to keep in the conversation.
            get_last_response (bool, optional): Flag to return the last response message. Defaults to False.
            log (bool, optional): Flag to enable logging of actions. Defaults to False.

        Returns:
            Any: The last response message if get_last_response is True, otherwise None.

        Raises:
            ValueError: If 'n' is more than the total number of messages.
        """
        self._keep_last_n_exchanges(n, verbose=verbose)
        last_response = self._get_last_response(verbose=verbose) if get_last_response else None
        return last_response

    def _keep_last_n_exchanges(self, n: int, verbose: bool = False):
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) 
            if message.role == "user"
        ]
        if len(response_indices) < n:
            raise ValueError(f"Cannot keep last {n} exchanges: insufficient messages.")

        first_index_to_keep = response_indices[-n] + 1
        self.messages = [self.system] + self.messages[first_index_to_keep:]
        if verbose:
            print(f"Kept the last {n} exchanges in the conversation.")

    def _get_last_response(self, verbose: bool = False):
        for msg in reversed(self.messages):
            if isinstance(msg, Response):
                if verbose:
                    print("Retrieved the last response from the conversation.")
                return msg
        if verbose:
            print("No response found in the conversation.")
        return None

    def search_messages(self, keyword: str, case_sensitive: bool = False, log: bool = False):
        """
        Searches for messages in the conversation containing a specific keyword.

        Args:
            keyword (str): Keyword to search for in the messages.
            case_sensitive (bool, optional): If True, search is case-sensitive. Defaults to False.
            log (bool, optional): If True, logs the search operation. Defaults to False.

        Returns:
            List[Message]: List of messages containing the keyword.
        """
        keyword_check = (lambda content, kw: kw in content) if case_sensitive else (lambda content, kw: kw.lower() in content.lower())

        found_messages = [msg for msg in self.messages if keyword_check(msg.content, keyword)]
        if log:
            print(f"Found {len(found_messages)} messages containing '{keyword}'.")

        return found_messages

    def delete_message(self, index: int, confirm: bool = False, range_to_delete: Optional[tuple] = None):
        """
        Deletes a message or a range of messages from the conversation at the specified index or indices.

        Args:
            index (int): The index of the message to delete.
            confirm (bool, optional): If True, requires confirmation before deletion. Defaults to False.
            range_to_delete (tuple, optional): A tuple specifying the start and end indices of a range of messages to delete.

        Raises:
            IndexError: If the index is out of the range of the message list.
            ValueError: If the range_to_delete is invalid.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if range_to_delete:
            start, end = range_to_delete
            if start < 0 or end >= len(self.messages) or start > end:
                raise ValueError("Invalid range to delete.")
            messages_to_delete = self.messages[start:end + 1]
        else:
            if index < 0 or index >= len(self.messages):
                raise IndexError("Index out of range.")
            messages_to_delete = [self.messages[index]]

        if confirm:
            confirmation = input(f"Are you sure you want to delete {len(messages_to_delete)} message(s)? (yes/no): ")
            if confirmation.lower() != 'yes':
                print("Deletion cancelled.")
                return False

        for msg in messages_to_delete:
            self.messages.remove(msg)
            print(f"Deleted message: {msg}")

        return True
