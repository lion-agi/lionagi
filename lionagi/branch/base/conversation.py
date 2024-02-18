from datetime import datetime
from typing import Dict, Any, Optional

import pandas as pd
from pandas import DataFrame

from lionagi.schema import BaseNode, DataLogger
from ..util import MessageUtil, search_keywords, replace_keyword


class Conversation(BaseNode):
    """
    Manages structured conversation data, supporting operations like adding, updating,
    and retrieving messages. Designed for use in applications involving chat or messaging
    functionalities.

    Attributes:
        messages (pd.DataFrame): A DataFrame holding the conversation's messages.
        datalogger (DataLogger): A DataLogger instance for logging conversation activities.

    Methods are designed to interact with conversation data, providing functionalities
    such as message retrieval by various criteria, message manipulation, and exporting
    conversation data to external formats.
    """
    messages: DataFrame

    columns = ['node_id', 'sender', 'recipient', 'timestamp',
               'content', 'role', 'metadata', 'relationships']

    class Conversation(BaseNode):
        columns: List[str] = [
            'node_id', 'sender', 'recipient', 'timestamp',
            'content', 'role', 'metadata', 'relationships'
        ]

        def __init__(
                self,
                messages: Optional[pd.DataFrame] = None,
                datalogger: Optional[DataLogger] = None,
                persist_path: Optional[Union[str, Path]] = None,
                **kwargs
        ) -> None:
            """
            Initializes a conversation instance with structured conversation data.

            This constructor initializes a conversation instance, managing structured
            conversation data, including messages, a data logger for activity logging, and
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
            self.messages = messages or pd.DataFrame(columns=self.columns)
            self.datalogger = datalogger or DataLogger(persist_path=persist_path)

    @property
    def chat_messages(self):
        """
        Prepares and retrieves chat messages formatted for completion without sender info.

        This property prepares the conversation's chat messages, stripping sender
        information, suitable for scenarios where sender details are not required.

        Returns:
            A list of dictionaries, each representing a chat message without sender
            information.
        """
        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self):
        """
        Prepares and retrieves chat messages formatted for completion, including sender.

        This property prepares the conversation's chat messages for scenarios where
        including sender details is necessary, formatting each message with sender
        information.

        Returns:
            A list of dictionaries, each representing a chat message with sender details.
        """
        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> pd.Series:
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
    def first_system(self) -> pd.Series:
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
    def last_response(self) -> pd.Series:
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
    def action_request(self) -> pd.DataFrame:
        """
        Retrieves all action request messages from the conversation.

        Filters the conversation's messages to return only those marked as
        'action_request', facilitating analysis or processing of user-initiated action
        requests.

        Returns:
            A DataFrame containing all messages classified as action requests, including
            details like sender, recipient, timestamp, and content.
        """
        return to_df(self.messages[self.messages.sender == 'action_request'])

    @property
    def action_response(self) -> pd.DataFrame:
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
    def responses(self) -> pd.DataFrame:
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
    def assistant_responses(self) -> pd.DataFrame:
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
        Provides a summary of conversation messages categorized by sender.

        This method generates a summary of the conversation, offering a count of messages
        segmented by the sender, which can be useful for understanding the distribution of
        message origins within the conversation.

        Returns:
            A dictionary with keys representing the sender of the messages (e.g., 'user', 'assistant')
            and values as the count of messages for each sender. Includes a total count of all messages.
        """
        return self._info(use_sender=True)

    @property
    def describe(self) -> Dict[str, Any]:
        """
        Provides a comprehensive descriptive summary of the conversation.

        This method compiles a detailed summary of the conversation, including the total
        number of messages, a breakdown by role, and a preview of the first up to five messages.

        Returns:
            A dictionary containing key details of the conversation: total number of messages,
            a summary by message role, and a list of dictionaries for the first five messages
            (if applicable), detailing sender, recipient, timestamp, and content.
        """

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [
                            msg.to_dict() for _, msg in self.messages.iterrows()
                        ][: self.len_messages - 1 if self.len_messages < 5 else 5],
        }

    def to_csv(self, filename: str = 'messages.csv', file_exist_ok: bool = False,
               timestamp: bool = True, time_prefix: bool = False,
               verbose: bool = True, clear: bool = True, **kwargs) -> None:
        """
        Saves the conversation's messages to a CSV file.

        This method exports the current state of conversation messages to a CSV file,
        with options for naming, timestamping, and verbosity during the save process.

        Args:
            filename: The name of the output CSV file. Defaults to 'messages.csv'.
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

        if not filename.endswith('.csv'):
            filename += '.csv'

        filepath = create_path(
            self.logger.dir, filename, timestamp=timestamp,
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
            timestamp: Appends a timestamp to the filename if True, for uniqueness.
            time_prefix: Adds a timestamp prefix to the filename if True.
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
            timestamp: Appends a unique timestamp to the filename if True.
            time_prefix: Adds a timestamp prefix to the filename if True.
            verbose: Prints a success message upon completion if True.
            clear: Clears the log after saving if True.
            **kwargs: Additional keyword arguments for `DataFrame.to_csv()`.

        Examples:
            >>> conversation.log_to_csv("detailed_log.csv", verbose=True, timestamp=True)
        """

        self.logger.to_csv(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
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
            timestamp: Appends a timestamp to the filename for uniqueness if True.
            time_prefix: If True, add a timestamp as a prefix to the filename.
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

    def add_message(self, system: Optional[Union[dict, list, System]] = None,
                    instruction: Optional[Union[dict, list, Instruction]] = None,
                    context: Optional[Union[str, Dict[str, Any]]] = None,
                    response: Optional[Union[dict, list, Response]] = None,
                    sender: Optional[str] = None) -> None:
        """
        Adds a new message to the conversation.

        This method allows for adding a new message to the conversation, with the
        flexibility to specify the type of message (system, instruction, or response),
        its context, and the sender.

        Args:
            system: A system message, optionally as a dictionary, list, or 'System' object.
            instruction: An instruction message, optionally as a dictionary, list, or 'Instruction' object.
            context: Contextual information for the instruction message, if applicable.
            response: A response message, optionally as a dictionary, list, or 'Response' object.
            sender: The identifier for the sender of the message.

        Examples:
            >>> conversation.add_message(response={'text': 'Hello, world!'}, sender='assistant')
        """

        msg = self._create_message(
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

    def change_first_system_message(self, system: Union[str, Dict[str, Any], 'System'],
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
            ValueError: If 'steps' is not a positive integer or exceeds the number of messages in the conversation.

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

        self.messages = pd.DataFrame(columns=Conversation.columns)

    def replace_keyword(self, keyword: str, replacement: str, col: str = 'content',
                        case_sensitive: bool = False) -> None:
        """
        Replaces all occurrences of a keyword in a specified column of the conversation's messages.

        This method searches for and replaces all instances of a specified keyword within
        a given column of the conversation's messages, such as the content column.

        Args:
            keyword: The keyword to be replaced.
            replacement: The string to replace the keyword with.
            col: The column in which to search and replace the keyword. Defaults to 'content'.
            case_sensitive: Specifies whether the search should be case-sensitive. Defaults to False.

        Examples:
            >>> conversation.replace_keyword('hello', 'hi')
        """

        replace_keyword(
            self.messages, keyword, replacement, col=col,
            case_sensitive=case_sensitive
        )

    def search_keywords(self, keywords: Union[str, List[str]],
                        case_sensitive: bool = False,
                        reset_index: bool = False, dropna: bool = False) -> pd.DataFrame:
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

        return search_keywords(
            self.messages, keywords, case_sensitive, reset_index, dropna
        )

    def extend(self, messages: pd.DataFrame, **kwargs) -> None:
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
                  content_keywords: Optional[Union[str, List[str]]] = None,
                  case_sensitive: bool = False) -> pd.DataFrame:
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
