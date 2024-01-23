import json
import pandas as pd
from datetime import datetime
from typing import Any, Optional, Dict
from lionagi.schema import DataLogger
from lionagi.utils import lcall
from ..messages.messages import Message, System, Instruction, Response



class Conversation:
    """
        Represents a conversation with messages, tools, and instructions.

        A `Conversation` is a container for messages exchanged in a conversation, as well as tools and instructions
        for interacting with external services or tools.

        Attributes:
            messages (pd.DataFrame): A DataFrame containing conversation messages.
            _logger (DataLogger): An instance of DataLogger for logging.

        """

    def __init__(self, dir=None) -> None:
        """
        Initializes a Conversation object.

        Args:
            dir (str, optional): The directory path for storing logs.

        """
        self.messages = pd.DataFrame(columns=["node_id", "role", "sender", "timestamp", "content"])
        self._logger = DataLogger(dir=dir)

    def _create_message(
        self, 
        system: Optional[Any] = None, 
        instruction: Optional[Any] = None, 
        context: Optional[Any] = None, 
        response: Optional[Any] = None, 
        sender: Optional[str] = None
        ) -> Message:
        """
        Creates a message object based on given input.

        This method is designed to create a message object from the given parameters. It ensures that
        exactly one of system, instruction, or response is provided to create a valid message.

        Args:
            system (Optional[Any]): The system message content.
            instruction (Optional[Any]): The instruction content.
            context (Optional[Any]): The context associated with the instruction.
            response (Optional[Any]): The response content.
            sender (Optional[str]): The sender of the message.

        Returns:
            Message: A message object created from the provided parameters.

        Raises:
            ValueError: If more than one or none of the parameters (system, instruction, response) are provided.
        """
        
        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")
        else:
            if isinstance(any([system, instruction, response]), Message):
                if system:
                    return system
                elif instruction:
                    return instruction
                elif response:
                    return response

            msg = 0
            if response:
                msg = Response(response=response, sender=sender)
            elif instruction:
                msg = Instruction(instruction=instruction, 
                                  context=context, sender=sender)
            elif system:
                msg = System(system=system, sender=sender)
            return msg

    def add_message(
        self, system=None, instruction=None, 
        context=None, response=None, sender=None):
        """
        Adds a message to the conversation.

        This method creates and adds a new message to the conversation's message DataFrame.

        Args:
            system: Content for a system message.
            instruction: Content for an instruction message.
            context: Context for the instruction message.
            response: Content for a response message.
            sender: The sender of the message.
        """
        msg = self._create_message(
            system=system, instruction=instruction, 
            context=context, response=response, sender=sender
        )
        message_dict = msg.to_dict()
        if isinstance(message_dict['content'], dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[len(self.messages)] = message_dict

    @property
    def last_content(self):
        """
        Returns the content of the last message in the conversation.

        Returns:
            The content of the last message.
        """
        return self.messages.iloc[-1]['content']
    
    def last_row(self, sender=None, role=None):
        """
        Retrieves the last row of the conversation based on either the sender or the role.

        Args:
            sender (Optional[str]): The sender to filter the messages.
            role (Optional[str]): The role to filter the messages.

        Returns:
            The last row of the conversation filtered by the given criteria.

        Raises:
            ValueError: If both or neither of sender and role are provided.
        """
        if sum(lcall([sender, role], bool)) != 1:
            raise ValueError("Error: can only get last row by one criteria.")
        if sender:
            return self.messages[self.messages.sender == sender].iloc[-1]
        else:
            return self.messages[self.messages.role == role].iloc[-1]

    def get_messages_by(self, node_id=None, role=None, sender=None, timestamp=None ,content=None):
        """
        Retrieves messages filtered by a specific criterion.

        Args:
            node_id (Optional[str]): The node ID to filter the messages.
            role (Optional[str]): The role to filter the messages.
            sender (Optional[str]): The sender to filter the messages.
            timestamp (Optional[datetime]): The timestamp to filter the messages.
            content (Optional[str]): The content to filter the messages.

        Returns:
            pd.DataFrame: A DataFrame containing filtered messages.

        Raises:
            ValueError: If more than one or none of the filtering criteria are provided.
        """
        if sum(lcall([node_id, role, sender, timestamp, content], bool)) != 1:
            raise ValueError("Error: can only get DataFrame by one criteria.")
        if node_id:
            return self.messages[self.messages["node_id"] == node_id]
        elif role:
            return self.messages[self.messages["role"] == role]
        elif sender:
            return self.messages[self.messages["sender"] == sender]
        elif timestamp:
            return self.messages[self.messages["timestamp"] == timestamp]
        elif content:
            return self.messages[self.messages["content"] == content]

    def replace_keyword(self, keyword: str, replacement: str, case_sensitive: bool = False) -> None:
        """
        Replaces a keyword in the content of all messages with a replacement string.

        Args:
            keyword (str): The keyword to replace.
            replacement (str): The string to replace the keyword with.
            case_sensitive (bool, optional): Flag to indicate if the replacement should be case sensitive. Defaults to False.
        """
        if not case_sensitive:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement, case=False
            )
        else:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement
            )

    def search_keyword(self, keyword: str, case_sensitive: bool = False) -> pd.DataFrame:
        """
        Searches for a keyword in the content of all messages and returns the messages containing it.

        Args:
            keyword (str): The keyword to search for.
            case_sensitive (bool, optional): Flag to indicate if the search should be case sensitive. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages with the specified keyword.
        """
        if not case_sensitive:
            keyword = keyword.lower()
            return self.messages[
                self.messages["content"].str.lower().str.contains(keyword)
            ]
        return self.messages[self.messages["content"].str.contains(keyword)]

    def remove_from_messages(self, message_id: str) -> bool:
        """
        Removes a message from the conversation based on its message ID.

        Args:
            message_id (str): The ID of the message to be removed.

        Returns:
            bool: True if the message was successfully removed, False otherwise.
        """
        initial_length = len(self.messages)
        self.messages = self.messages[self.messages["node_id"] != message_id]
        return len(self.messages) < initial_length

    def update_messages_content(self, message_id: str, col: str, value) -> bool:
        """
        Updates the content of a specific message in the conversation.

        Args:
            message_id (str): The ID of the message to be updated.
            col (str): The column of the message that needs to be updated.
            value: The new value to be set for the specified column.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        index = self.messages.index[self.messages["id_"] == message_id].tolist()
        if index:
            self.messages.at[index[0], col] = value
            return True
        return False

    def info(self, use_sender=False) -> Dict[str, int]:
        """
        Provides a summary of the conversation messages.

        Args:
            use_sender (bool, optional): Determines whether to summarize by sender or by role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary containing counts of messages either by role or sender.
        """
        messages = self.messages['name'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.messages)
        return result

    def describe(self) -> Dict[str, Any]:
        """
        Describes the conversation with various statistics and information.

        Returns:
            Dict[str, Any]: A dictionary containing information such as total number of messages, summary by role, and individual messages.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def history(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieves a history of messages within a specified date range.

        Args:
            start_date (Optional[datetime], optional): The start date of the message history. Defaults to None.
            end_date (Optional[datetime], optional): The end date of the message history. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing messages within the specified date range.
        """
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if start_date and end_date:
            return self.messages[
                (self.messages["timestamp"].dt.date >= start_date.date())
                & (self.messages["timestamp"].dt.date <= end_date.date())
            ]
        elif start_date:
            return self.messages[(self.messages["timestamp"].dt.date >= start_date.date())]
        elif end_date:
            return self.messages[(self.messages["timestamp"].dt.date <= end_date.date())]
        return self.messages

    def clone(self) -> 'Conversation':
        """
        Creates a clone of the current conversation.

        Returns:
            Conversation: A new Conversation object that is a clone of the current conversation.
        """
        cloned = Conversation()
        cloned._logger.set_dir(self._logger.dir)
        cloned.messages = self.messages
        cloned.messages = self.messages.copy()
        return cloned

    def merge(self, other: 'Conversation') -> None:
        """
        Merges another Conversation object into this one.

        Args:
            other (Conversation): Another Conversation object to be merged.
        """
        self.messages = self.messages.merge(other.messages, how='outer')

    def rollback(self, steps: int) -> None:
        """
        Rollbacks the conversation by a specified number of steps (messages).

        Args:
            steps (int): The number of steps to rollback.

        Raises:
            ValueError: If steps are not a non-negative integer or greater than the number of messages.
        """
        if steps < 0 or steps > len(self.messages):
            raise ValueError("Steps must be a non-negative integer less than or equal to the number of messages.")
        self.messages = self.messages[:-steps].reset_index(drop=True)

    def reset(self) -> None:
        """
        Resets the conversation, clearing all messages.
        """
        self.messages = pd.DataFrame(columns=self.messages.columns)

    def to_csv(self, filepath: str, **kwargs) -> None:
        """
        Exports the conversation messages to a CSV file.

        Args:
            filepath (str): The file path where the CSV will be saved.
            **kwargs: Additional keyword arguments for `pandas.DataFrame.to_csv` method.
        """
        self.messages.to_csv(filepath, **kwargs)

    def from_csv(self, filepath: str, **kwargs) -> None:
        """
        Imports conversation messages from a CSV file.

        Args:
            filepath (str): The file path of the CSV to be read.
            **kwargs: Additional keyword arguments for `pandas.read_csv` method.
        """
        self.messages = pd.read_csv(filepath, **kwargs)

    def to_json(self, filepath: str) -> None:
        """
        Exports the conversation messages to a JSON file.

        Args:
            filepath (str): The file path where the JSON will be saved.
        """
        self.messages.to_json(
            filepath, orient="records", lines=True, date_format="iso")

    def from_json(self, filepath: str) -> None:
        """
        Imports conversation messages from a JSON file.

        Args:
            filepath (str): The file path of the JSON to be read.
        """
        self.reset()
        self.messages = pd.read_json(filepath, orient="records", lines=True)
