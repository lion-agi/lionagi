from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional, Union, List

from pandas import DataFrame, Series

from lionagi.util import to_dict, to_df, lcall
from lionagi.schema import BaseNode, DataLogger
from lionagi.message import System, Instruction, Response, BaseMessage
from lionagi.branch.util import MessageUtil


class Conversation(BaseNode):
    """
    Manages structured conversation data for chat or messaging app functionalities.
    Provides an interface for adding, updating, retrieving, and manipulating messages
    stored in a pandas DataFrame. Supports operations like message retrieval by various
    criteria, manipulation, and exporting data to external formats, making it a versatile
    component for conversation management.

    Since Conversation inherits from the BaseNode class, it includes all methods and
    attributes of its parent. For a comprehensive list of inherited functionalities,
    please refer to the BaseNode class documentation.

    Attributes:
        messages (DataFrame):
            Holds the conversation's messages.

        datalogger (DataLogger):
            Instance for logging conversation activities.

        columns (List[str]):
            Defines the columns of the messages DataFrame.
            Default columns include 'node_id', 'sender', 'recipient', 'timestamp',
            'content', 'role', 'metadata', and 'relationships'.

    Properties:
        chat_messages:
            Retrieves messages formatted without sender info.

        chat_messages_with_sender:
            Retrieves messages with sender info.

        last_message:
            Gets the last message as a pandas Series.

        last_message_content:
            Extracts content of the last message.

        first_system:
            Retrieves the first system message.

        last_response:
            Retrieves the last response message.

        last_response_content:
            Extracts content of the last response.

        action_request:
            Retrieves all action request messages.

        action_response:
            Retrieves all action response messages.

        responses:
            Retrieves all response messages.

        assistant_responses:
            Retrieves assistant responses, excluding action messages.

        info:
            Summarizes messages categorized by role.

        sender_info:
            Summarizes messages categorized by sender.

        describe:
            Provides a descriptive summary of the conversation.

    Methods:
        __init__(self, messages=None, datalogger=None, persist_path=None, **kwargs):
            Initializes a conversation instance with structured data.

        to_csv(self, filepath='messages.csv', file_exist_ok=False, timestamp=True,
               time_prefix=False, verbose=True, clear=True, **kwargs):
            Saves messages to a CSV file.

        to_json(self, filename='messages.json', file_exist_ok=False, timestamp=True,
                time_prefix=False, verbose=True, clear=True, **kwargs):
            Saves messages to a JSON file.

        log_to_csv(self, filename='log.csv', file_exist_ok=False, timestamp=True,
                   time_prefix=False, verbose=True, clear=True, **kwargs):
            Saves log data to a CSV file.

        log_to_json(self, filename='log.json', file_exist_ok=False, timestamp=True,
                    time_prefix=False, verbose=True, clear=True, **kwargs):
            Saves log data to a JSON file.

        add_message(self, system=None, instruction=None, context=None, response=None,
                    sender=None):
            Adds a new message to the conversation.

        remove_message(self, node_id):
            Removes a message by its node ID.

        update_message(self, value, node_id=None, col='node_id'):
            Updates a specific message detail.

        change_first_system_message(self, system, sender=None):
            Changes the first system message.

        rollback(self, steps):
            Removes the last 'n' messages.

        clear_messages(self):
            Clears all messages, resetting to an empty state.

        replace_keyword(self, keyword, replacement, col='content',
                        case_sensitive=False):
            Replaces a keyword in a specified column.

        search_keywords(self, keywords, case_sensitive=False, reset_index=False,
                        dropna=False):
            Searches for messages containing specified keywords.

        extend(self, messages, **kwargs):
            Appends new messages to the conversation.

        filter_by(self, role=None, sender=None, start_time=None, end_time=None,
                  content_keywords=None, case_sensitive=False):
            Filters messages based on specified criteria.

    Class Methods:
        from_csv(cls, **kwargs):
            Creates an instance from a CSV file.

        from_json(cls, **kwargs):
            Creates an instance from a JSON file.

    Example Usage:
        >>> conversation = Conversation()
        >>> conversation.add_message(response={'text': 'Hello, world!'}, sender='assistant')
        >>> conversation.to_csv("exported_messages.csv", timestamp=True)
        >>> conversation.clear_messages()

    Leverages pandas for data manipulation and storage, emphasizing efficient data
    handling and analysis for conversation management applications.
    """

    columns: List[str] = ['node_id', 'timestamp','role', 'sender',
                          'content',  ]

    # 'metadata', 'relationships', 'recipient',
    def __init__(
            self,
            messages: Optional[DataFrame] = None,
            datalogger: Optional[DataLogger] = None,
            persist_path: Optional[Union[str, Path]] = None,
            **kwargs
    ) -> None:
        """
        Initializes a conversation instance with structured conversation data.

        This constructor initializes a conversation instance, managing structured
        conversation data, including messages, a data datalogger for activity logging, and
        a path for persisting data.

        Args:
            messages:
                Initial conversation messages as a pandas DataFrame. If None, an
                empty DataFrame with predefined columns is used.
            datalogger:
                A DataLogger instance for logging conversation activities.
                If None, a new DataLogger instance is initialized with `persist_path`.
            persist_path:
                Path for persisting conversation data and logs.
                Used by `datalogger` if provided. Defaults to 'data/logs/' if None.
            **kwargs:
                Additional keyword arguments for parent class initialization.

        """
        super().__init__(**kwargs)
        self.messages: DataFrame = messages or DataFrame(columns=self.columns)
        self.datalogger: DataLogger = datalogger or DataLogger(persist_path=persist_path)

    @property
    def chat_messages(self):
        """
        Prepares and retrieves chat messages formatted for chat completion tasks with LLMs

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a chat
            message formatted, for LLM processing. Each dictionary contains keys for
            message attributes such as 'role' and 'content'.
        """
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self):
        """
        Prepares and retrieves chat messages formatted for chat completion tasks with
        LLMs, including sender information added into message content to clarify the
        sender of each message.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a chat
            message formatted, for LLM processing. Each dictionary contains keys for
            message attributes such as 'role' and 'content'.
            Each message content includes the sender information.
        """
        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> Series:
        """
        Retrieves the last message from the conversation as a pandas Series.

        This property fetches the most recent message from the conversation's history,
        returning it in a format that includes all columns of the message DataFrame.

        Returns:
            The last message in the conversation history as a pandas Series, including
            details like sender, recipient, timestamp, and content.
        """
        return MessageUtil.get_message_rows(self.messages, n=1, from_='last')

    @property
    def last_message_content(self):
        """
        Extracts and returns the most recent message content in the conversation as a
        dictionary. Designed for quick access to the last message for processing or
        analysis.
        The content is returned in a dictionary format, aiding cases where structured data
        is involved and might be needed for language models or other processing tasks.

        Returns:
            Dict[str, Any]: The content of the last message, formatted as a dictionary.
            Attempts to parse string content as a JSON object for compatibility with
            structured message formats, facilitating use in subsequent operations.
        """
        return to_dict(self.messages.content.iloc[-1])

    @property
    def first_system(self) -> Series:
        """
        Retrieves the first system message from the conversation.

        This property fetches the earliest message in the conversation history that is
        marked with the role 'system', providing it as a pandas Series.

        Returns:
            The first system message in the conversation history, encompassing all
            relevant details such as sender, recipient, timestamp, and content.
        """
        return MessageUtil.get_message_rows(self.messages, role='system', n=1,
                                            from_='front')

    @property
    def last_response(self) -> Series:
        """
        Retrieves the last response message from the conversation.

        This property fetches the most recent message in the conversation history that
        has been tagged as a response by the assistant, returning it as a pandas Series.

        Returns:
            The last response message, including sender, recipient, timestamp, and content
            facilitating detailed analysis or further processing.
        """
        return MessageUtil.get_message_rows(self.messages, role='assistant', n=1,
                                            from_='last')

    @property
    def last_response_content(self) -> Dict:
        """
        Extracts the content of the last response message in the conversation.

        This method parses the last response message, specifically extracting its content
        and returning it in a dictionary format for easy access to message details.

        Returns:
            A dictionary representing the content of the last response message, allowing
            for easy retrieval of message specifics such as text or metadata.
        """
        return to_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> DataFrame:
        """
        Retrieves all action package messages from the conversation.

        Filters the conversation's messages to return only those marked as
        'action_request', facilitating analysis or processing of user-initiated action
        requests.

        Returns:
            A DataFrame containing all messages classified as action requests, including
            details like sender, recipient, timestamp, and content.
        """
        return to_df(self.messages[self.messages.sender == 'action_request'])

    @property
    def action_response(self) -> DataFrame:
        """
        Retrieves all action response messages from the conversation.

        This method filters the conversation messages to return only those that are
        marked as 'action_response', typically representing responses to previously
        issued action requests.

        Returns:
            A DataFrame containing all action response messages, complete with details
            such as sender, recipient, timestamp, and content, useful for analyzing
            responses or automating follow-up actions.
        """
        return to_df(self.messages[self.messages.sender == 'action_response'])

    @property
    def responses(self) -> DataFrame:
        """
        Retrieves all response messages from the conversation.

        Filters the conversation's messages to include only those with a role of
        'assistant', which are considered responses to user queries or system prompts.

        Returns:
            A DataFrame of all response messages, detailing sender, recipient, timestamp,
            and content, aiding in response analysis or further processing needs.
        """
        return to_df(self.messages[self.messages.role == 'assistant'])

    @property
    def assistant_responses(self) -> DataFrame:
        """
        Retrieves all assistant responses, excluding action requests and responses.

        This method focuses on filtering messages to those sent by the assistant that
        are not part of action requests or responses, allowing for analysis of pure
        conversation or informational exchanges.

        Returns: A DataFrame containing assistant response messages, excluding any
        action-related messages, detailed with sender, recipient, timestamp, and content.
        """

        a_responses = self.responses[self.responses.sender != 'action_response']
        a_responses = a_responses[a_responses.sender != 'action_request']
        return to_df(a_responses)

    @property
    def info(self) -> dict:
        """
        Provides a summary of conversation messages categorized by role.

        Generates a dictionary summary of the conversation, counting messages based on
        their assigned roles (e.g., user, assistant, system), offering insights into
        conversation dynamics.

        Returns: A dictionary with keys as message roles (e.g., 'user', 'assistant',
        'system') and values representing the count of messages for each role,
        including a total message count.
        """

        return self._info()

    @property
    def sender_info(self) -> Dict[str, int]:
        """
        Summarizes conversation messages by sender.

        Generates a summary of the conversation, providing a count of messages segmented
        by sender. Useful for analyzing message origin distribution within the conversation.

        Returns:
            Dict[str, int]: A dictionary with keys as sender types (e.g., 'user', 'assistant')
            and values as the count of messages for each sender, including a total message count.
        """
        return self._info(use_sender=True)

    @property
    def describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of the conversation.

        Compiles a detailed summary, including total message count, breakdown by role, and
        a preview of the first five messages, if applicable. Useful for a quick overview
        or detailed analysis of the conversation dynamics.

        Returns:
            Dict[str, Any]: Key details of the conversation, including total number of messages,
            summary by role, and a list of dictionaries for the first five messages, detailing
            sender, recipient, timestamp, and content.
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
        Creates a new Conversation instance from a CSV file.

        This class method reads conversation data from a specified CSV file and initializes
        a Conversation instance with this data. It allows for additional customization of the CSV
        reading process through keyword arguments, such as specifying delimiters or which
        columns to import.

        Args:
            **kwargs: Keyword arguments for customizing the CSV reading process, passed
            directly to the internal method responsible for reading the CSV file.

        Returns:
            Conversation: An instance of Conversation populated with data from the CSV file.
        """
        return cls._from_csv(**kwargs)

    @classmethod
    def from_json(cls, **kwargs) -> 'Conversation':
        """
        Creates a new Conversation instance from a JSON file.

        This method reads conversation data from a JSON file and uses it to initialize a
        Conversation instance. The process can be customized with additional keyword
        arguments, such as specifying the structure of the JSON data (e.g., 'records',
        'index').

        Args:
            **kwargs: Keyword arguments for customizing the JSON reading process, passed
            directly to the internal method responsible for reading the JSON file.

        Returns:
            Conversation: An instance populated with data from the JSON file.
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
        Saves the conversation's messages to a CSV file.

        This method exports the current state of conversation messages to a CSV file,
        with options for naming, timestamping, and verbosity during the save process.

        Args:
            filepath: The name of the output CSV file. Defaults to 'messages.csv'.
            file_exist_ok: If True, doesn't raise an error if the output directory exists.
            timestamp: If True, appends a timestamp to the filename for uniqueness.
            time_prefix: If True, adds a timestamp prefix to the filename.
            verbose: If True, prints a success message upon completion.
            clear: If True, clears the messages from the conversation after saving.
            **kwargs: Additional keyword arguments passed to `pd.DataFrame.to_csv()`.

        Examples:
            >>> conversation.to_csv("exported_messages.csv")
            >>> conversation.to_csv("backup.csv", timestamp=True, verbose=True)
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
        Saves the conversation's messages to a JSON file.

        Exports the conversation messages into a JSON file, providing flexibility
        in file naming, timestamping, and verbosity of the output process.

        Args:
            filename: The name of the output JSON file, defaults to 'messages.json'.
            file_exist_ok: Allows existing directory without raising an error if True.
            timestamp: Appends a timestamp to the filepath if True, for uniqueness.
            time_prefix: Adds a timestamp prefix to the filepath if True.
            verbose: Prints a message upon successful save if True.
            clear: Clears the messages in the conversation after saving if True.
            **kwargs: Additional arguments passed to `pd.DataFrame.to_json()`.

        Examples:
            >>> conversation.to_json("exported_conversation.json")
            >>> conversation.to_json("conversation_backup.json", timestamp=True)
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
        Saves the conversation's log data to a CSV file.

        This method is designed to export log data, potentially including operations
        and interactions, to a CSV file for analysis or record-keeping.

        Args:
            filename: The name of the output CSV file, defaults to 'log.csv'.
            file_exist_ok: If True, won't raise error if output directory exists.
            timestamp: Appends a unique timestamp to the filepath if True.
            time_prefix: Adds a timestamp prefix to the filepath if True.
            verbose: Prints a success message upon completion if True.
            clear: Clears the log after saving if True.
            **kwargs: Additional keyword arguments for `DataFrame.to_csv()`.

        Examples:
            >>> conversation.log_to_csv("detailed_log.csv", verbose=True, timestamp=True)
        """

        self.logger.to_csv(
            filepath=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(self, filename: str = 'log.json', file_exist_ok: bool = False,
                    timestamp: bool = True, time_prefix: bool = False,
                    verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Saves the conversation's log data to a JSON file.

        Exports log data in JSON format, suitable for integration with web applications
        or for detailed record-keeping of conversation operations and interactions.

        Args:
            filename: The name of the output JSON file, defaults to 'log.json'.
            file_exist_ok: If True, existing directory issues won't raise an error.
            timestamp: Appends a timestamp to the filepath for uniqueness if True.
            time_prefix: If True, add a timestamp as a prefix to the filepath.
            verbose: If True, prints a success message upon file save.
            clear: Clears the conversation log after saving if True.
            **kwargs: Additional keyword arguments for `DataFrame.to_json()`.

        Examples:
            >>> conversation.log_to_json("conversation_operations_log.json")
        """

        self.logger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def add_message(self, system: Optional[Dict | List | System] = None,
                    instruction: Optional[Dict | List | Instruction] = None,
                    context: Optional[str | Dict[str, Any]] = None,
                    response: Optional[Dict | List | Response] = None,
                    sender: Optional[str] = None) -> None:
        """
        Adds a new message to the conversation with specified details.

        Enables adding a message of various types (system, instruction, response) with
        optional context and sender information. This method is flexible in accepting
        different formats for message components.

        Args:
            system: Optional system message as dict, list, or System object.
            instruction: Optional instruction message as dict, list, or Instruction object.
            context: Optional context for the message, as string or dict.
            response: Optional response message as dict, list, or Response object.
            sender: Optional identifier for the message sender.

        Examples:
            >>> conversation.add_message(response={'text': 'Hello, world!'}, sender='assistant')
        """

        msg = self._create_message(self,
            system=system, instruction=instruction,
            context=context, response=response, sender=sender)

        message_dict = msg.to_dict()
        if isinstance(to_dict(message_dict['content']), dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now().isoformat()
        self.messages.loc[len(self.messages)] = message_dict

    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the conversation by its node ID.

        This method allows for the removal of a specific message from the conversation,
        identified by its unique node ID.

        Args:
            node_id: The unique identifier of the message to be removed.

        Examples:
            >>> conversation.remove_message("12345")
        """

        MessageUtil.remove_message(self.messages, node_id)

    def update_message(self, value: Any, node_id: Optional[str] = None,
                       col: str = 'node_id') -> None:
        """
        Updates a specific detail of a message in the conversation.

        This method enables the updating of a message's content or any other detail,
        identified by the node ID and the specific column to be updated.

        Args: value: The new value for the specified detail of the message. node_id:
        The unique identifier of the message to be updated. Optional if updating by
        column. col: The column of the message detail to update. Defaults to 'node_id'.

        Examples:
            >>> conversation.update_message('Updated message content', node_id='12345',
            ... col='content')
        """

        return MessageUtil.update_row(self.messages, node_id=node_id, col=col,
                                      value=value)

    def change_first_system_message(self, system: str | Dict[str, Any] | System,
                                    sender: Optional[str] = None) -> None:
        """
        Changes the first system message in the conversation.

        This method is used to modify the first message in the conversation that is
        marked as a system message, allowing updates to its content or sender.

        Args:
            system: The new system message content, as a string, dictionary, or 'System'
                    object.
            sender: The identifier for the sender of the message. Optional.

        Raises:
            ValueError: If there are no system messages in the conversation or if the
                    input cannot be converted into a system message.

        Examples:
            >>> conversation.change_first_system_message({'text': 'System update'},
            ... sender='system')
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
        Removes the last 'n' messages from the conversation.

        This method enables the removal of the most recent messages from the conversation,
        specified by the number of steps or messages to roll back.

        Args:
            steps: The number of messages to remove from the end of the conversation.

        Raises:
            ValueError: If 'steps' is not a positive integer or exceeds the number of
            messages in the conversation.

        Examples:
            >>> conversation.rollback(2)  # Removes the last two messages
        """

        return MessageUtil.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the conversation, resetting it to an empty state.

        This method removes all messages from the conversation, effectively resetting
        the conversation's state to be empty.

        Examples:
            >>> conversation.clear_messages()
        """

        self.messages = DataFrame(columns=Conversation.columns)

    def replace_keyword(self, keyword: str, replacement: str, col: str = 'content',
                        case_sensitive: bool = False) -> None:
        """
        Replaces all occurrences of a keyword in a specified column of the messages.

        Searches and replaces instances of a keyword in a conversation's message column,
        like 'content', with an option for case sensitivity.

        Args:
            keyword: Keyword to be replaced.
            replacement: Replacement string.
            col: Column to search (default: 'content').
            case_sensitive: If True, search is case-sensitive (default: False).

        Examples:
            >>> conversation.replace_keyword('hello', 'hi')
        """

        MessageUtil.replace_keyword(
            self.messages, keyword, replacement, col=col,
            case_sensitive=case_sensitive
        )

    def search_keywords(self, keywords: str | List[str],
                        case_sensitive: bool = False,
                        reset_index: bool = False, dropna: bool = False) -> DataFrame:
        """
        Searches for messages containing specified keywords within the conversation.

        This method filters the conversation's messages to find those containing one or
        more specified keywords, returning a DataFrame of matching messages.

        Args:
            keywords: The keyword or list of keywords to search for within the messages.
            case_sensitive: If True, the search will be case sensitive. Defaults to False.
            reset_index: If True, the returned DataFrame will have a reset index.
                Defaults to False.
            dropna: If True, messages with NA values will be dropped before the search.
                Defaults to False.

        Returns:
            A DataFrame containing messages that match the search criteria.

        Examples:
            >>> matching_messages = conversation.search_keywords(['urgent', 'asap'],
            ... case_sensitive=True)
        """

        return MessageUtil.search_keywords(
            self.messages, keywords, case_sensitive, reset_index, dropna
        )

    def extend(self, messages: DataFrame, **kwargs) -> None:
        """
        Extends the conversation by appending new messages, optionally avoiding duplicates.

        This method allows for the addition of a collection of new messages to the
        conversation, with optional parameters to handle duplicates according to
        specified criteria.

        Args:
            messages: A DataFrame containing new messages to be appended to the
                    conversation.
            **kwargs: Additional keyword arguments passed to pandas' `drop_duplicates`
                    method if handling of duplicates is desired.

        Examples:
            >>> new_messages = pd.DataFrame([...])
            >>> conversation.extend(new_messages, ignore_index=True)
        """

        self.messages = MessageUtil.extend(self.messages, messages, **kwargs)

    def filter_by(self, role: Optional[str] = None, sender: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  content_keywords: Optional[str | List[str]] = None,
                  case_sensitive: bool = False) -> DataFrame:
        """
        Filters the conversation's messages based on specified criteria.

        This method enables filtering of the conversation messages by various criteria
        such as role, sender, time range, and content keywords, returning a DataFrame
        of messages that match the specified conditions.

        Args:
            role: Filter messages by the specified role (e.g., 'user', 'assistant').
            sender: Filter messages by the sender identifier.
            start_time: Filter messages sent after this datetime.
            end_time: Filter messages sent before this datetime.
            content_keywords: Filter messages containing these keywords in their content.
            case_sensitive: If True, keyword search will be case sensitive. Defaults to
            False.

        Returns:
            A DataFrame of messages that match the filter criteria.

        Examples:
            >>> filtered_messages = conversation.filter_by(role='user',
            ... content_keywords='help')
        """

        return MessageUtil.filter_messages_by(
            self.messages, role=role, sender=sender,
            start_time=start_time, end_time=end_time,
            content_keywords=content_keywords, case_sensitive=case_sensitive
        )

    def _to_chatcompletion_message(self, with_sender=False) -> List[Dict[str, Any]]:
        """
        Internal method to format messages for chat completion tasks.

        Prepares and formats the conversation's messages, optionally including sender
        information, for use in tasks such as chat completion or AI training.

        Args:
            with_sender: Includes sender information in the formatted messages if True.

        Returns:
            A list of dictionaries, each representing a formatted chat message.

        Note:
            This is an internal method and should not be called directly by end users.
        """

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
        """
        Internal method to create a message object from given parameters.

        Constructs a new message object for the conversation, based on the specified
        type (system, instruction, or response), context, and sender.

        Args:
            system: System message content or object.
            instruction: Instruction message content or object.
            context: Context for the instruction message.
            response: Response message content or object.
            sender: Identifier for the sender of the message.

        Returns:
            A newly created Message object populated with the given details.

        Note:
            This is an internal method and is intended for use within class methods only.
        """

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
        """
        Generates a summary of the conversation's messages, either by role or sender.

        Args:
            use_sender (bool, optional): If True, generates the summary based on sender.
            If False, uses a role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary with counts of messages, categorized either by
            role or sender.
        """
        messages = self.messages['sender'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.len_messages)

        return result
