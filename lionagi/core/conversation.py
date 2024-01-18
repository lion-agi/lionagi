import json
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

from .messages import Message

class Conversation:
    """
    Manages the flow and archival of a conversation using Pandas DataFrame.

    Attributes:
        messages (pd.DataFrame): A DataFrame to store messages.
        dir (Optional[str]): The directory path for saving files, if provided.

    Examples:
        >>> conv = Conversation()
        >>> msg = Message(node_id="1", role="user", name="Alice", content="Hi there!")
        >>> conv.add_message(msg)
        >>> conv.get_message_by_role("user")
        >>> conv.last_message()
        >>> conv.search_message("Hi")
        >>> conv.message_counts()
    """

    def __init__(self, dir: Optional[str] = None) -> None:
        self.messages = pd.DataFrame(
            columns=["node_id", "role", "name", "timestamp", "content"]
        )
        self.dir = dir

    def add_message(self, message: Message) -> None:
        """
        Adds a new message to the DataFrame.

        Args:
            message (Message): The message object to be added.

        Examples:
            >>> conv = Conversation()
            >>> msg = Message(node_id="1", role="user", name="Alice", content="Hi there!")
            >>> conv.add_message(msg)
        """
        message_dict = message.to_dict()
        if isinstance(message_dict['content'], dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[len(self.messages)] = message_dict

    def get_message_by_role(self, role: str) -> pd.DataFrame:
        """
        Retrieves messages sent by a specific role.

        Args:
            role (str): The role to filter messages by.

        Returns:
            pd.DataFrame: DataFrame of messages matching the role.

        Examples:
            >>> conv = Conversation()
            >>> conv.get_message_by_role("user")
        """
        return self.messages[self.messages["role"] == role]

    def last_message(self):
        """
        Retrieves the last message from the conversation.

        Returns:
            Message: The last message object, if the DataFrame is not empty.

        Examples:
            >>> conv = Conversation()
            >>> conv.last_message()
        """
        if not self.messages.empty:
            return Message(**self.messages.iloc[-1].to_dict())

    def last_message_by_role(self, role: str) -> Optional[Message]:
        """
        Retrieves the last message of a specific role.

        Args:
            role (str): The role to get messages by.

        Returns:
            Optional[Message]: The last message of the given role, if exists.

        Examples:
            >>> conv = Conversation()
            >>> conv.last_message_by_role("user")
        """
        filtered_messages = self.messages[
            self.messages["role"] == role
        ]
        if not filtered_messages.empty:
            return Message(**filtered_messages.iloc[-1].to_dict())
        return None

    def search_message(self, keyword: str, case_sensitive: bool = False) -> pd.DataFrame:
        """
        Searches for messages containing a specific keyword.

        Args:
            keyword (str): The keyword to search for.
            case_sensitive (bool, optional): Whether the search should be case-sensitive. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame of messages containing the keyword.

        Examples:
            >>> conv = Conversation()
            >>> conv.search_message("Hi")
            >>> conv.search_message("Hi", case_sensitive=True)
        """
        if not case_sensitive:
            keyword = keyword.lower()
            return self.messages[
                self.messages["content"].str.lower().str.contains(keyword)
            ]
        return self.messages[self.messages["content"].str.contains(keyword)]

    def delete_message(self, message_id: str) -> bool:
        """
        Deletes a message by its unique identifier.

        Args:
            message_id (str): The unique identifier of the message.

        Returns:
            bool: True if a message was deleted, False otherwise.

        Examples:
            >>> conv = Conversation()
            >>> conv.delete_message("1")
        """
        initial_length = len(self.messages)
        self.messages = self.messages[self.messages["node_id"] != message_id]
        return len(self.messages) < initial_length

    def update_message_content(self, message_id: str, new_content: str) -> bool:
        """
        Updates the content of a specific message by its unique identifier.

        Args:
            message_id (str): The unique identifier of the message.
            new_content (str): The new content for the message.

        Returns:
            bool: True if the content was updated, False otherwise.

        Examples:
            >>> conv = Conversation()
            >>> conv.update_message_content("1", "New content")
        """
        index = self.messages.index[self.messages["id_"] == message_id].tolist()
        if index:
            self.messages.at[index[0], "content"] = new_content
            return True
        return False

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """
        Retrieves a message by its unique identifier.

        Args:
            message_id (str): The unique identifier of the message.

        Returns:
            Optional[Message]: The message if found, None otherwise.

        Examples:
            >>> conv = Conversation()
            >>> conv.get_message_by_id("1")
        """
        message_df = self.messages[self.messages["id_"] == message_id]
        if not message_df.empty:
            return Message.from_json(message_df.iloc[0].to_dict())
        return None

    def message_counts(self, use_name=False) -> Dict[str, int]:
        """
        Provides a summary of message counts in the conversation, optionally grouped by sender's name.

        Args:
            use_name (bool, optional): If True, groups by sender's name instead of role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary with roles or names as keys and their associated message counts as values.

        Examples:
            >>> conv = Conversation()
            >>> conv.message_counts()  # Group by role
            >>> conv.message_counts(use_name=True)  # Group by sender's name
        """
        messages = self.messages['name'] if use_name else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.messages)
        return result

    def report(self) -> Dict[str, Any]:
        """
        Generates a detailed report of the conversation.

        Returns:
            Dict[str, Any]: A dictionary with various details about the conversation.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.message_counts(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def history(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Returns a history of the conversation, optionally filtered by date range.

        Args:
            start_date (Optional[datetime], optional): The start date of the date range filter. Defaults to None.
            end_date (Optional[datetime], optional): The end date of the date range filter. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing the filtered conversation history.
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

    def replace_keyword(self, keyword: str, replacement: str, case_sensitive: bool = False) -> None:
        """
        Replaces a keyword in all messages with a replacement.

        Args:
            keyword (str): The keyword to replace.
            replacement (str): The text to replace the keyword with.
            case_sensitive (bool, optional): Whether the replacement should be case-sensitive. Defaults to False.
        """
        if not case_sensitive:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement, case=False
            )
        else:
            self.messages["content"] = self.messages["content"].str.replace(
                keyword, replacement
            )

    def clone(self) -> 'Conversation':
        """
        Creates a deep copy of the conversation.

        Returns:
            Conversation: A new Conversation instance with the same messages.
        """
        cloned = Conversation(self.dir)
        cloned.messages = self.messages.copy()
        return cloned

    def merge(self, other: 'Conversation') -> None:
        """
        Merges another conversation into this one.

        Args:
            other (Conversation): Another Conversation instance to merge with this one.
        """
        self.messages = self.messages.merge(other.messages, how='outer')

    def rollback(self, steps: int) -> None:
        """
        Rollbacks the conversation to a previous state by the given number of steps.

        Args:
            steps (int): The number of steps to rollback.

        Raises:
            ValueError: If steps are negative or exceed the current number of messages.
        """
        if steps < 0 or steps > len(self.messages):
            raise ValueError("Steps must be a non-negative integer less than or equal to the number of messages.")
        self.messages = self.messages[:-steps].reset_index(drop=True)

    def reset(self) -> None:
        """Clears all messages in the DataFrame."""
        self.messages = pd.DataFrame(columns=self.messages.columns)

    def to_csv(self, filepath: str, **kwargs) -> None:
        """
        Saves the conversation to a CSV file.

        Args:
            filepath (str): The path to the file where the conversation should be saved.
        """
        self.messages.to_csv(filepath, **kwargs)

    def from_csv(self, filepath: str, **kwargs) -> None:
        """
        Loads messages from a CSV file into the conversation.

        Args:
            filepath (str): The path to the file from which to load the conversation.
        """
        self.messages = pd.read_csv(filepath, **kwargs)

    def to_json(self, filepath: str) -> None:
        """
        Saves the entire conversation as a JSON file.

        Args:
            filepath (str): The file path where the conversation will be saved.
        """
        self.messages.to_json(
            filepath, orient="records", lines=True, date_format="iso"
        )

    def from_json(self, filepath: str) -> None:
        """
        Loads messages from a JSON file into the conversation.

        Args:
            filepath (str): The file path from which to load the conversation.
        """
        self.reset()
        self.messages = pd.read_json(filepath, orient="records", lines=True)

    # def append(self, other: 'Conversation'):
    #     self.messages = pd.concat([self.messages, other.messages]).reset_index(drop=True)
