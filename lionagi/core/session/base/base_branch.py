from datetime import datetime
import json
from typing import Dict, Any, Optional, Union, List

from pandas import DataFrame, Series

from lionagi.util import to_dict, to_df, lcall
from lionagi.schema import BaseNode, DataLogger
from lionagi.core.session.message import System, Instruction, Response, BaseMessage
from lionagi.core.session.branch.util import MessageUtil


class Conversation(BaseNode):
    """
    Manages a conversation by storing, manipulating, and analyzing chat messages.

    This class provides functionalities to add, update, remove, and search messages within
    a conversation. It supports exporting and importing the conversation data to and from
    CSV and JSON formats. Various properties are available to access specific subsets or
    characteristics of the conversation, such as the last message or all responses.

    Attributes:
        columns (list[str]): Names of the columns in the messages DataFrame.
        messages (pandas.DataFrame): DataFrame storing the messages of the conversation.
        datalogger (DataLogger): Object to log conversation data.
        persist_path (str | pathlib.Path | None): Path to persist conversation data.

    Args:
        messages (pandas.DataFrame | None): Initial set of messages for the conversation.
        Defaults to None, creating an empty DataFrame.
        datalogger (DataLogger | None): DataLogger instance for logging purposes.
        Defaults to None, initiating a new DataLogger.
        persist_path (str | pathlib.Path | None): Optional path for data persistence. Defaults to None.
    """
    columns: List[str] = ['node_id', 'timestamp', 'role', 'sender',
                          'content', ]

    # 'metadata', 'relationships', 'recipient',
    def __init__(self, messages: DataFrame | None = None,
                 datalogger: DataLogger | None = None,
                 persist_path: str | pathlib.Path | None = None, **kwargs) -> None:
        """
        Initializes a new Conversation instance.

        Sets up a conversation with an optional initial set of messages, a data logger for logging, and a persistence path for data storage.

        Args:
            messages (pandas.DataFrame | None): Initial DataFrame of messages. If None, an empty DataFrame is created. Defaults to None.
            datalogger (DataLogger | None): An instance of DataLogger for logging conversation events. If None, a new DataLogger is instantiated. Defaults to None.
            persist_path (str | pathlib.Path | None): File system path to persist conversation data. If None, persistence is not set up. Defaults to None.
        """

        super().__init__(**kwargs)
        self.messages: DataFrame = messages or DataFrame(columns=self.columns)
        self.datalogger: DataLogger = datalogger or DataLogger(persist_path=persist_path)

    @property
    def chat_messages(self) -> list[dict[str, Any]]:
        """
        Gets a list of chat messages formatted for chat completions.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing a message in the conversation formatted for chat completions. Each dictionary contains 'role' and 'content' keys.
        """

        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self) -> list[dict[str, Any]]:
        """
        Gets a list of chat messages with sender information, formatted for chat completions.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing a message in the conversation with sender information, formatted for chat completions. Each dictionary includes 'role', 'content', and 'sender' keys.
        """

        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> Series:
        """
        Retrieves the last message in the conversation as a pandas Series.

        This property provides access to the last message sent in the conversation, returning it as a Series object which includes all columns of the message DataFrame, such as 'node_id', 'timestamp', 'role', 'sender', and 'content'.

        Returns:
            pandas.Series: The last message in the conversation.
        """

        return MessageUtil.get_message_rows(self.messages, n=1, from_='last')

    @property
    def last_message_content(self) -> dict:
        """
        Retrieves the content of the last message in the conversation.

        This property decodes the content of the last message from the conversation's DataFrame, converting serialized JSON strings back into Python dictionaries if necessary.

        Returns:
            dict: A dictionary representing the content of the last message. If the message's content is a serialized JSON string, it is deserialized into a dictionary.
        """

        return to_dict(self.messages.content.iloc[-1])

    @property
    def first_system(self) -> Series:
        """
        Retrieves the first system message in the conversation as a pandas Series.

        This property searches the conversation's DataFrame for the first message with a role of 'system', providing it as a Series object. The Series includes all relevant columns such as 'node_id', 'timestamp', 'role', 'sender', and 'content'.

        Returns:
            pandas.Series: The first system message in the conversation, if one exists. If no system message is found, an empty Series is returned.
        """

        return MessageUtil.get_message_rows(self.messages, role='system', n=1,
                                            from_='front')

    @property
    def last_response(self) -> Series:
        """
        Retrieves the last response message from the assistant in the conversation.

        This property searches the conversation's DataFrame for the most recent message with a role of 'assistant', returning it as a pandas Series. The Series includes all relevant details such as 'node_id', 'timestamp', 'role', 'sender', and 'content'.

        Returns:
            pandas.Series: The last response message sent by the assistant in the conversation.
        """

        return MessageUtil.get_message_rows(self.messages, role='assistant', n=1,
                                            from_='last')

    @property
    def last_response_content(self) -> dict:
        """
        Retrieves the content of the last assistant response message in the conversation.

        This method decodes the content of the last response message from the conversation's DataFrame, deserializing JSON strings into Python dictionaries if necessary.

        Returns:
            dict: A dictionary representing the content of the last response message. Deserializes JSON content if applicable.

        Raises:
            ValueError: If the last response message's content cannot be deserialized.
        """

        return to_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> DataFrame:
        """
        Retrieves all messages marked as 'action_request' sent in the conversation.

        Filters the conversation's DataFrame to include only those messages where the sender is identified as 'action_request', returning them as a new DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame containing all 'action_request' messages.
        """

        return to_df(self.messages[self.messages.sender == 'action_request'])

    @property
    def action_response(self) -> DataFrame:
        """
        Retrieves all messages marked as 'action_response' sent in the conversation.

        Filters the conversation's DataFrame for messages where the sender is identified as 'action_response', returning these messages as a new DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame containing all 'action_response' messages.
        """

        return to_df(self.messages[self.messages.sender == 'action_response'])

    @property
    def responses(self) -> DataFrame:
        """
        Retrieves all messages in the conversation with the role of 'assistant'.

        This property filters the conversation's DataFrame to include only messages where the role is set to 'assistant', returning them as a new DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame containing all messages with the role of 'assistant'.
        """

        return to_df(self.messages[self.messages.role == 'assistant'])

    @property
    def assistant_responses(self) -> DataFrame:
        """
        Retrieves assistant responses excluding 'action_response' and 'action_request' messages.

        Filters the `responses` DataFrame to exclude messages where the sender is 'action_response' or 'action_request', providing a cleaner view of pure assistant responses.

        Returns:
            pandas.DataFrame: A DataFrame of assistant responses, excluding 'action_response' and 'action_request' messages.
        """

        a_responses = self.responses[self.responses.sender != 'action_response']
        a_responses = a_responses[a_responses.sender != 'action_request']
        return to_df(a_responses)

    @property
    def info(self) -> dict:
        """
        Compiles summary information about the conversation's messages based on their roles.

        Utilizes the internal `_info` method without sender differentiation, aggregating message counts by their roles (e.g., 'assistant', 'user').

        Returns:
            dict: A dictionary with roles as keys and counts of messages as values, including a total message count.
        """

        return self._info()

    @property
    def sender_info(self) -> dict[str, int]:
        """
        Compiles summary information about the conversation's messages based on their senders.

        Utilizes the internal `_info` method with sender differentiation, offering a detailed view of message counts attributed to each sender type (e.g., 'assistant', 'user', 'action_request').

        Returns:
            dict[str, int]: A dictionary with sender types as keys and counts of messages as values, providing insights into the distribution of message origins.
        """

        return self._info(use_sender=True)

    @property
    def describe(self) -> dict[str, Any]:
        """
        Provides a summary description of the conversation.

        This property compiles key statistics about the conversation, including the total number of messages, a summary by role, and a preview of the first few messages.

        Returns:
            dict[str, Any]: A dictionary containing the total number of messages, a role-based summary, and a list of up to five message dictionaries.
        """

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [
                            msg.to_dict() for _, msg in self.messages.iterrows()
                        ][: self.len_messages - 1 if self.len_messages < 5 else 5],
        }

    @classmethod
    def _from_csv(cls, filepath: str, read_kwargs=None, **kwargs) -> 'Conversation':
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = MessageUtil.read_csv(filepath, **read_kwargs)
        return cls(messages=messages, **kwargs)

    @classmethod
    def from_csv(cls, **kwargs) -> 'Conversation':
        """
        Creates a Conversation instance from a CSV file.

        Reads messages from a specified CSV file and initializes a Conversation object with these messages.

        Args:
            **kwargs: Keyword arguments that are passed to the `_from_csv` helper method, including 'filepath' and 'read_kwargs'.

        Returns:
            Conversation: An instance of the Conversation class populated with messages from the specified CSV file.
        """

        return cls._from_csv(**kwargs)

    @classmethod
    def from_json(cls, **kwargs) -> 'Conversation':
        """
        Creates a Conversation instance from a JSON file.

        Reads messages from a specified JSON file and initializes a Conversation object with these messages.

        Args:
            **kwargs: Keyword arguments that are passed to the `_from_json` helper method, including 'filepath' and 'read_kwargs'.

        Returns:
            Conversation: An instance of the Conversation class populated with messages from the specified JSON file.
        """

        return cls._from_json(**kwargs)

    @classmethod
    def _from_json(cls, filepath: str, read_kwargs=None, **kwargs) -> 'Conversation':
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = MessageUtil.read_json(filepath, **read_kwargs)
        return cls(messages=messages, **kwargs)

    def to_csv(self, filepath: str = 'messages.csv', file_exist_ok: bool = False,
               timestamp: bool = True, time_prefix: bool = False,
               verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Exports the conversation's messages to a CSV file.

        Allows for the customization of the export process through various parameters, including the ability to timestamp the file name and to clear the messages DataFrame after exporting.

        Args:
            filepath (str): Path and name of the file to save the messages. Automatically appends '.csv' if not present. Defaults to 'messages.csv'.
            file_exist_ok (bool): If True, overwrites the file if it already exists. Defaults to False.
            timestamp (bool): If True, appends a timestamp to the filename to ensure uniqueness. Defaults to True.
            time_prefix (bool): If True, places the timestamp at the beginning of the filename. Defaults to False.
            verbose (bool): If True, prints a confirmation message upon successful export. Defaults to True.
            clear (bool): If True, clears the messages DataFrame after exporting. Defaults to True.
            **kwargs: Additional keyword arguments passed to pandas.DataFrame.to_csv().

        Raises:
            ValueError: If an error occurs during the saving process.
        """

        if not filepath.endswith('.csv'):
            filepath += '.csv'

        filepath = create_path(
            self.logger.dir, filepath, timestamp=timestamp,
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )

        try:
            self.messages.to_csv(filepath, **kwargs)
            if verbose:
                print(f"{len(self.messages)} messages saved to {filepath}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")

    def to_json(self, filename: str = 'messages.json', file_exist_ok: bool = False,
                timestamp: bool = True, time_prefix: bool = False,
                verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Exports the conversation's messages to a JSON file.

        This method provides flexibility in exporting messages to JSON format, including options for timestamping the filename and clearing the messages DataFrame after export.

        Args:
            filename (str): Path and name of the file to save the messages. Automatically appends '.json' if not present. Defaults to 'messages.json'.
            file_exist_ok (bool): If True, allows overwriting of the file if it exists. Defaults to False.
            timestamp (bool): If True, appends a timestamp to the filename for uniqueness. Defaults to True.
            time_prefix (bool): If True, places the timestamp at the file name's start. Defaults to False.
            verbose (bool): If True, prints a message upon successful export. Defaults to True.
            clear (bool): If True, clears the DataFrame after exporting the messages. Defaults to True.
            **kwargs: Additional keyword arguments passed to pandas.DataFrame.to_json().

        Raises:
            ValueError: If an error occurs during the saving process.
        """

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = create_path(
            self.dir, filename, timestamp=timestamp,
            dir_exist_ok=file_exist_ok, time_prefix=time_prefix
        )

        try:
            self.messages.to_json(
                filepath, orient="records", lines=True,
                date_format="iso", **kwargs
            )
            if clear:
                self.clear_messages()
            if verbose:
                print(f"{len(self.messages)} messages saved to {filepath}")
        except Exception as e:
            raise ValueError(f"Error in saving to json: {e}")

    def log_to_csv(self, filename: str = 'log.csv', file_exist_ok: bool = False,
                   timestamp: bool = True, time_prefix: bool = False,
                   verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Exports the conversation's log data to a CSV file.

        This method delegates to the logger's `to_csv` function, allowing for the export of log data with customizable options for file naming and management.

        Args:
            filename (str): The path and name for the log file. Defaults to 'log.csv'. Automatically appends '.csv' if not present.
            file_exist_ok (bool): If True, allows the method to overwrite the file if it already exists. Defaults to False.
            timestamp (bool): If True, appends a timestamp to the filename to ensure uniqueness. Defaults to True.
            time_prefix (bool): If True, places the timestamp at the beginning of the filename. Defaults to False.
            verbose (bool): If True, prints a confirmation message upon successful export. Defaults to True.
            clear (bool): If True, clears the logger's data after exporting. Defaults to True.
            **kwargs: Additional keyword arguments passed to `logger.to_csv()`.

        Raises:
            ValueError: If an error occurs during the file saving process.
        """

        self.logger.to_csv(
            filepath=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(self, filename: str = 'log.json', file_exist_ok: bool = False,
                    timestamp: bool = True, time_prefix: bool = False,
                    verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Exports the conversation's log data to a JSON file.

        Utilizes the logger's `to_json` function to export log data, providing various options for the file's naming and handling.

        Args:
            filename (str): The path and name for the log file. Defaults to 'log.json'. Automatically appends '.json' if not present.
            file_exist_ok (bool): If True, overwrites the file if it exists. Defaults to False.
            timestamp (bool): If True, includes a timestamp in the filename for uniqueness. Defaults to True.
            time_prefix (bool): If True, adds the timestamp as a prefix in the filename. Defaults to False.
            verbose (bool): If True, displays a message upon successful export. Defaults to True.
            clear (bool): If True, clears the logger's data after exporting. Defaults to True.
            **kwargs: Additional keyword arguments passed to `logger.to_json()`.

        Raises:
            ValueError: If an error occurs during the saving process.
        """

        self.logger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def add_message(self, system: dict | list | System | None = None,
                    instruction: dict | list | Instruction | None = None,
                    context: str | dict[str, Any] | None = None,
                    response: dict | list | Response | None = None,
                    sender: str | None = None) -> None:
        """
        Adds a new message to the conversation's DataFrame.

        This method allows adding a message of a specific role (system, instruction, or response) to the conversation. The message is appended to the `messages` DataFrame with additional metadata such as timestamp and sender.

        Args:
            system (dict | list | System | None): System message content. Defaults to None.
            instruction (dict | list | Instruction | None): Instruction message content. Defaults to None.
            context (str | dict[str, Any] | None): Context for the instruction, if any. Defaults to None.
            response (dict | list | Response | None): Response message content. Defaults to None.
            sender (str | None): Identifier for the sender of the message. Defaults to None.

        Raises:
            ValueError: If more than one of `system`, `instruction`, or `response` is provided, or if the content cannot be serialized.
        """

        msg = self._create_message(
            self, system=system, instruction=instruction,
            context=context, response=response, sender=sender)

        message_dict = msg.to_dict()
        if isinstance(to_dict(message_dict['content']), dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now().isoformat()
        self.messages.loc[len(self.messages)] = message_dict

    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the conversation's DataFrame based on its node_id.

        This method looks up a message by its unique identifier (node_id) and removes it from the conversation.

        Args:
            node_id (str): The unique identifier of the message to be removed.
        """

        MessageUtil.remove_message(self.messages, node_id)

    def update_message(self, value: Any, node_id: Optional[str] = None,
                       col: str = 'node_id') -> None:
        """
        Updates the value of a specified column for a message in the conversation's DataFrame.

        This method identifies a message by its node_id and updates a specified column with a new value.

        Args:
            value (Any): The new value to update the message with.
            node_id (Optional[str]): The unique identifier of the message to be updated. If None, defaults to updating the 'node_id' column.
            col (str): The column to update. Defaults to 'node_id'.

        Returns:
            None. The specified message's column is updated with the new value.
        """

        return MessageUtil.update_row(self.messages, node_id=node_id, col=col,
                                      value=value)

    def change_first_system_message(self, system: str | dict[str, Any] | System,
                                    sender: Optional[str] = None) -> None:
        """
        Modifies the first system message in the conversation.

        This method updates the content and optionally the sender of the first system message. If no system message exists, it raises an error.

        Args:
            system (str | Dict[str, Any] | System): The new content for the system message, either as a string, a dictionary, or a System object.
            sender (Optional[str]): The new sender of the system message. If None, the sender is not updated.

        Raises:
            ValueError: If there are no system messages in the conversation or if the input cannot be converted into a system message.
        """

        if self.len_systems == 0:
            raise ValueError("There is no system message in the messages.")

        if not isinstance(system, (str, Dict, System)):
            raise ValueError("Input cannot be converted into a system message.")

        elif isinstance(system, (str, Dict)):
            system = System(system, sender=sender)

        elif isinstance(system, System):
            message_dict = system.to_dict()
            if sender:
                message_dict['sender'] = sender
            message_dict['timestamp'] = datetime.now().isoformat()
            sys_index = self.messages[self.messages.role == 'system'].index
            self.messages.loc[sys_index[0]] = message_dict

    def rollback(self, steps: int) -> None:
        """
        Removes the specified number of latest messages from the conversation.

        This method is used to undo recent additions by removing a defined number of messages from the end of the conversation's DataFrame.

        Args:
            steps (int): The number of messages to remove from the end of the conversation.

        Returns:
            None. The last 'steps' messages are removed from the conversation.
        """

        return MessageUtil.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the conversation's DataFrame.

        This method resets the `messages` DataFrame, removing all stored messages. It is useful for resetting the conversation state or preparing the conversation object for a new set of messages.
        """

        self.messages = DataFrame(columns=Conversation.columns)

    def replace_keyword(self, keyword: str, replacement: str, col: str = 'content',
                        case_sensitive: bool = False) -> None:
        """
        Replaces occurrences of a specified keyword in a given column with a replacement string.

        This method scans the specified column for the keyword and replaces it with the provided replacement string, with an option to make the search case-sensitive.

        Args:
            keyword (str): The keyword to search for in the column.
            replacement (str): The string to replace the keyword with.
            col (str): The column to search for the keyword. Defaults to 'content'.
            case_sensitive (bool): If True, the search is case-sensitive; otherwise, it's case-insensitive. Defaults to False.
        """

        MessageUtil.replace_keyword(
            self.messages, keyword, replacement, col=col,
            case_sensitive=case_sensitive
        )

    def search_keywords(self, keywords: str | list[str],
                        case_sensitive: bool = False,
                        reset_index: bool = False,
                        dropna: bool = False) -> DataFrame:
        """
        Searches for messages containing specified keywords.

        Filters the conversation's messages to include only those containing the specified keywords, with options for case sensitivity, index resetting, and NaN dropping.

        Args:
            keywords (str | list[str]): The keyword or list of keywords to search for.
            case_sensitive (bool): If True, the search is case-sensitive. Defaults to False.
            reset_index (bool): If True, resets the DataFrame's index after filtering. Defaults to False.
            dropna (bool): If True, drops rows with NaN values after filtering. Defaults to False.

        Returns:
            pandas.DataFrame: A DataFrame containing messages that match the search criteria.
        """

        return MessageUtil.search_keywords(
            self.messages, keywords, case_sensitive, reset_index, dropna
        )

    def extend(self, messages: DataFrame, **kwargs) -> None:
        """
        Extends the conversation's messages DataFrame with additional messages.

        This method appends a given DataFrame of messages to the existing messages DataFrame, allowing for the incorporation of new data into the conversation.

        Args:
            messages (pandas.DataFrame): The DataFrame containing messages to be added.
            **kwargs: Additional keyword arguments for customization.
        """

        self.messages = MessageUtil.extend(self.messages, messages, **kwargs)

    def filter_by(self, role: Optional[str] = None, sender: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  content_keywords: Optional[str | list[str]] = None,
                  case_sensitive: bool = False) -> pandas.DataFrame:
        """
        Filters the conversation's messages based on various criteria.

        Allows for filtering by message role, sender, time range, and content keywords, with an option for case-sensitive content searches.

        Args:
            role (Optional[str]): The role to filter messages by (e.g., 'assistant', 'user'). Defaults to None.
            sender (Optional[str]): The sender to filter messages by. Defaults to None.
            start_time (Optional[datetime]): The starting point of the time range filter. Defaults to None.
            end_time (Optional[datetime]): The ending point of the time range filter. Defaults to None.
            content_keywords (Optional[str | list[str]]): Keywords to filter messages by their content. Defaults to None.
            case_sensitive (bool): If True, content keyword search is case-sensitive. Defaults to False.

        Returns:
            pandas.DataFrame: A DataFrame of messages that meet the specified criteria.
        """

        return MessageUtil.filter_messages_by(
            self.messages, role=role, sender=sender,
            start_time=start_time, end_time=end_time,
            content_keywords=content_keywords, case_sensitive=case_sensitive
        )

    def _to_chatcompletion_message(self, with_sender=False) -> List[Dict[str, Any]]:

        message = []

        for _, row in self.messages.iterrows():
            content_ = row['content']
            if content_.startswith('Sender'):
                content_ = content_.split(':', 1)[1]

            if isinstance(content_, str):
                try:
                    content_ = json.dumps(to_dict(content_))
                except Exception as e:
                    raise ValueError(
                        f"Error in serializing, {row['node_id']} {content_}: {e}")

            out = {"role": row['role'], "content": content_}
            if with_sender:
                out['content'] = f"Sender {row['sender']}: {content_}"

            message.append(out)
        return message

    @staticmethod
    def _create_message(self: object,
                        system: Optional[Union[Dict, List, 'System']] = None,
                        instruction: Optional[Union[Dict, List, 'Instruction']] = None,
                        context: Optional[Union[str, Dict[str, Any]]] = None,
                        response: Optional[Union[Dict, List, 'Response']] = None,
                        sender: Optional[str] = None) -> 'Message':

        if sum(lcall([system, instruction, response], bool)) != 1:
            raise ValueError("Error: Message must have one and only one role.")

        else:
            if isinstance(any([system, instruction, response]), BaseMessage):
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

    # noinspection PyTestUnpassedFixture
    def _info(self, use_sender: bool = False) -> Dict[str, int]:

        messages = self.messages['sender'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.len_messages)

        return result
