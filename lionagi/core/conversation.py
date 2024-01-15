import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Type
from .messages import Message

class Conversation:
    """
    Manages the flow and archival of a conversation using Pandas DataFrame.
    """

    def __init__(self, dir: Optional[str] = None) -> None:
        self.messages = pd.DataFrame(
            columns=["id_", "role", "name", "timestamp", "content", "type"]
        )
        self.dir = dir

    def add_message(self, message: Message) -> None:
        """
        Adds a new message to the DataFrame.

        Args:
            message (Message): The message object to be added.
        """
        message_dict = message.to_dict()
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[len(self.messages)] = message_dict

    def get_messages_by_role(self, role: str) -> pd.DataFrame:
        """
        Retrieves messages sent by a specific role.

        Args:
            role (str): The role to filter messages by.

        Returns:
            pd.DataFrame: DataFrame of messages matching the role.
        """
        return self.messages[self.messages["role"] == role]

    def reset(self) -> None:
        """Clears all messages in the DataFrame."""
        self.messages = pd.DataFrame(columns=self.messages.columns)

    def last_message_of_type(self, message_type: Type[Message]) -> Optional[Message]:
        """
        Retrieves the last message of a specific type.

        Args:
            message_type (Type[Message]): The message type class.

        Returns:
            Optional[Message]: The last message of the given type, if exists.
        """
        filtered_messages = self.messages[
            self.messages["type"] == message_type.__name__
        ]
        if not filtered_messages.empty:
            return Message(**filtered_messages.iloc[-1].to_dict())
        return None

    def search_messages(self, keyword: str, case_sensitive: bool = False) -> pd.DataFrame:
        """
        Searches for messages containing a specific keyword.

        Args:
            keyword (str): The keyword to search for.
            case_sensitive (bool, optional): Whether the search should be case-sensitive. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame of messages containing the keyword.
        """
        if not case_sensitive:
            keyword = keyword.lower()
            return self.messages[
                self.messages["content"].str.lower().str.contains(keyword)
            ]
        return self.messages[self.messages["content"].str.contains(keyword)]

    def save_conversation_to_csv(self, filepath: str) -> None:
        """
        Saves the conversation to a CSV file.

        Args:
            filepath (str): The path to the file where the conversation should be saved.
        """
        self.messages.to_csv(filepath, index=False)

    def load_conversation_from_csv(self, filepath: str) -> None:
        """
        Loads messages from a CSV file into the conversation.

        Args:
            filepath (str): The path to the file from which to load the conversation.
        """
        self.messages = pd.read_csv(filepath)

    def delete_message(self, message_id: str) -> bool:
        """
        Deletes a message by its unique identifier.

        Args:
            message_id (str): The unique identifier of the message.

        Returns:
            bool: True if a message was deleted, False otherwise.
        """
        initial_length = len(self.messages)
        self.messages = self.messages[self.messages["id_"] != message_id]
        return len(self.messages) < initial_length

    def update_message_content(self, message_id: str, new_content: str) -> bool:
        """
        Updates the content of a specific message by its unique identifier.

        Args:
            message_id (str): The unique identifier of the message.
            new_content (str): The new content for the message.

        Returns:
            bool: True if the content was updated, False otherwise.
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
        """
        message_df = self.messages[self.messages["id_"] == message_id]
        if not message_df.empty:
            return Message.from_json(message_df.iloc[0].to_dict())
        return None

    def summarize_conversation_by_role(self) -> Dict[str, int]:
        """
        Provides a summary of the conversation grouped by role.

        Returns:
            Dict[str, int]: A dictionary with roles as keys and message counts as values.
        """
        return self.messages["role"].value_counts().to_dict()

    def generate_conversation_report(self) -> Dict[str, Any]:
        """
        Generates a detailed report of the conversation.

        Returns:
            Dict[str, Any]: A dictionary with various details about the conversation.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.summarize_conversation_by_role(),
            "messages": [
                Message.from_json(msg).to_plain_text() for _, msg in self.messages.iterrows()
            ],
        }

    def get_conversation_history(
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
        if start_date and end_date:
            return self.messages[
                (self.messages["timestamp"] >= start_date)
                & (self.messages["timestamp"] <= end_date)
            ]
        return self.messages

    def save_conversation_to_json(self, filepath: str) -> None:
        """
        Saves the entire conversation as a JSON file.

        Args:
            filepath (str): The file path where the conversation will be saved.
        """
        self.messages.to_json(
            filepath, orient="records", lines=True, date_format="iso"
        )

    def load_conversation_from_json(self, filepath: str) -> None:
        """
        Loads messages from a JSON file into the conversation.

        Args:
            filepath (str): The file path from which to load the conversation.
        """
        self.reset()
        self.messages = pd.read_json(filepath, orient="records", lines=True)

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

    def export_conversation(self, filename: str) -> None:
        """
        Exports the conversation to a file.

        Args:
            filename (str): The filename where the conversation should be exported.
        """
        self.messages.to_csv(filename, index=False)

    def import_conversation(self, filename: str) -> None:
        """
        Imports messages from a file into the conversation.

        Args:
            filename (str): The filename from which to import the conversation.
        """
        self.reset()
        self.messages = pd.read_csv(filename)

    def clone(self) -> 'Conversation':
        """
        Creates a shallow copy of the conversation.

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
        self.messages = pd.concat([self.messages, other.messages]).reset_index(drop=True)

    def get_message_count(self) -> int:
        """
        Gets the total number of messages in the conversation.

        Returns:
            int: The total number of messages.
        """
        return len(self.messages)

    def archive_conversation(self, archive_path: str) -> None:
        """
        Archives the entire conversation as a JSON file and resets the conversation.

        Args:
            archive_path (str): The file path where the conversation will be saved.
        """
        self.save_conversation_to_json(archive_path)
        self.reset()
