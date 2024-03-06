from abc import ABC
from typing import Any

from lionagi.libs.sys_util import SysUtil, PATH_TYPE

import lionagi.libs.ln_convert as convert
import lionagi.libs.ln_dataframe as dataframe

from lionagi.core.schema.base_node import BaseRelatableNode
from lionagi.core.schema.data_logger import DataLogger, DLog
from lionagi.core.session.base.schema import (
    BranchColumns,
    System,
    Instruction,
    BaseMessage,
)
from lionagi.core.session.base.util import MessageUtil


class BaseBranch(BaseRelatableNode, ABC):
    """
    A base class for managing branches of conversation, which encapsulates messaging and logging functionalities.

    This class provides a structured way to manage conversation messages, including storing, adding, updating,
    and querying messages. It supports functionalities like changing system messages, rolling back messages,
    and exporting or importing message logs.

    Attributes:
        messages (dataframe.ln_DataFrame): Dataframe holding the messages within the branch, with a flexible
                                           schema to accommodate different message types.
        datalogger (DataLogger): Responsible for logging data related to branch operation, useful for tracking
                                 and debugging purposes.
        persist_path (PATH_TYPE): The filesystem path where the branch's data can be persisted, facilitating
                                  data saving and loading operations.
    """

    _columns: list[str] = BranchColumns.COLUMNS.value

    def __init__(
        self,
        messages: dataframe.ln_DataFrame | None = None,
        datalogger: DataLogger | None = None,
        persist_path: PATH_TYPE | None = None,
        **kwargs,
    ) -> None:
        """
        Initializes a BaseBranch instance with optional messages, datalogger, and a persistence path.

        Args:
            messages (dataframe.ln_DataFrame | None): An optional dataframe of messages to initialize the branch.
            datalogger (DataLogger | None): An optional datalogger for tracking branch operations.
            persist_path (PATH_TYPE | None): An optional filesystem path for persisting branch data.
            **kwargs: Additional keyword arguments to pass to the BaseRelatableNode initializer.
        """
        super().__init__(**kwargs)
        if isinstance(messages, dataframe.ln_DataFrame):
            if MessageUtil.validate_messages(messages):
                self.messages = messages
            else:
                raise ValueError("Invalid messages format")
        else:
            self.messages = dataframe.ln_DataFrame(columns=self._columns)

        self.datalogger = (
            datalogger if datalogger else DataLogger(persist_path=persist_path)
        )

    def add_message(
        self,
        system: dict | list | System | None = None,
        instruction: dict | list | Instruction | None = None,
        context: str | dict[str, Any] | None = None,
        response: dict | list | BaseMessage | None = None,
        **kwargs,
    ) -> None:
        """
        Adds a message to the branch with optional system information, instruction, context, and response.

        This method constructs a message from the provided parameters and appends it to the branch's message dataframe.
        It validates and transforms message contents to ensure compatibility with the branch's schema.

        Args:
            system: System message or data to be included in the message.
            instruction: Instruction message or data.
            context: Additional context for the message.
            response: Response message or data.
            **kwargs: Arbitrary keyword arguments for additional message parameters.

        Raises:
            ValueError: If provided messages are in an invalid format.
        """
        _msg = MessageUtil.create_message(
            system=system,
            instruction=instruction,
            context=context,
            response=response,
            **kwargs,
        )

        _msg.content = _msg.msg_content
        self.messages.loc[len(self.messages)] = _msg.to_pd_series()

    def _to_chatcompletion_message(
        self, with_sender: bool = False
    ) -> list[dict[str, Any]]:
        """
        Formats messages in the branch for chat completion, optionally including sender information.

        Converts each message in the branch's dataframe to a dictionary format suitable for chat completion tasks,
        optionally prefixing messages with sender information.

        Args:
            with_sender: If True, includes the sender's information in the message content.

        Returns:
            A list of dictionaries, each representing a message formatted for chat completion.
        """

        message = []

        for _, row in self.messages.iterrows():
            content_ = row["content"]
            if content_.startswith("Sender"):
                content_ = content_.split(":", 1)[1]

            # if isinstance(content_, str):
            #     try:
            #         content_ = json.dumps(to_dict(content_))
            #     except Exception as e:
            #         raise ValueError(
            #             f"Error in serializing, {row['node_id']} {content_}: {e}"
            #         )

            out = {"role": row["role"], "content": content_}
            if with_sender:
                out["content"] = f"Sender {row['sender']}: {content_}"

            message.append(out)
        return message

    @property
    def chat_messages(self) -> list[dict[str, Any]]:
        """
        Retrieves all chat messages without sender information.

        Returns:
            A list of dictionaries representing chat messages.
        """

        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self) -> list[dict[str, Any]]:
        """
        Retrieves all chat messages, including sender information.

        Returns:
            A list of dictionaries representing chat messages, each prefixed with its sender.
        """

        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> dataframe.ln_DataFrame:
        """
        Retrieves the last message from the branch as a pandas Series.

        Returns:
            A pandas Series representing the last message in the branch.
        """

        return MessageUtil.get_message_rows(self.messages, n=1, from_="last")

    @property
    def last_message_content(self) -> dict[str, Any]:
        """
        Extracts the content of the last message in the branch.

        Returns:
            A dictionary representing the content of the last message.
        """

        return convert.to_dict(self.messages.content.iloc[-1])

    @property
    def first_system(self) -> dataframe.ln_DataFrame:
        """
        Retrieves the first message marked with the 'system' role.

        Returns:
            A pandas Series representing the first 'system' message in the branch.
        """

        return MessageUtil.get_message_rows(
            self.messages, role="system", n=1, from_="front"
        )

    @property
    def last_response(self) -> dataframe.ln_DataFrame:
        """
        Retrieves the last message marked with the 'assistant' role.

        Returns:
            A pandas Series representing the last 'assistant' (response) message in the branch.
        """

        return MessageUtil.get_message_rows(
            self.messages, role="assistant", n=1, from_="last"
        )

    @property
    def last_response_content(self) -> dict[str, Any]:
        """
        Extracts the content of the last 'assistant' (response) message.

        Returns:
            A dictionary representing the content of the last 'assistant' message.
        """

        return convert.to_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> dataframe.ln_DataFrame:
        """
        Filters and retrieves all messages sent by 'action_request'.

        Returns:
            A pandas DataFrame containing all 'action_request' messages.
        """

        return convert.to_df(self.messages[self.messages.sender == "action_request"])

    @property
    def action_response(self) -> dataframe.ln_DataFrame:
        """
        Filters and retrieves all messages sent by 'action_response'.

        Returns:
            A pandas DataFrame containing all 'action_response' messages.
        """

        return convert.to_df(self.messages[self.messages.sender == "action_response"])

    @property
    def responses(self) -> dataframe.ln_DataFrame:
        """
        Retrieves all messages marked with the 'assistant' role.

        Returns:
            A pandas DataFrame containing all messages with an 'assistant' role.
        """

        return convert.to_df(self.messages[self.messages.role == "assistant"])

    @property
    def assistant_responses(self) -> dataframe.ln_DataFrame:
        """
        Filters 'assistant' role messages excluding 'action_request' and 'action_response'.

        Returns:
            A pandas DataFrame of 'assistant' messages excluding action requests/responses.
        """

        a_responses = self.responses[self.responses.sender != "action_response"]
        a_responses = a_responses[a_responses.sender != "action_request"]
        return convert.to_df(a_responses)

    @property
    def info(self) -> dict[str, Any]:
        """
        Summarizes branch information, including message counts by role.

        Returns:
            A dictionary containing counts of messages categorized by their role.
        """

        return self._info()

    @property
    def sender_info(self) -> dict[str, int]:
        """
        Provides a summary of message counts categorized by sender.

        Returns:
            A dictionary with senders as keys and counts of their messages as values.
        """

        return self._info(use_sender=True)

    @property
    def describe(self) -> dict[str, Any]:
        """
        Provides a detailed description of the branch, including a summary of messages.

        Returns:
            A dictionary with a summary of total messages, a breakdown by role, and
            a preview of the first five messages.
        """

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [msg.to_dict() for _, msg in self.messages.iterrows()][
                : len(self.messages) - 1 if len(self.messages) < 5 else 5
            ],
        }

    @classmethod
    def _from_csv(cls, filename: str, read_kwargs=None, **kwargs) -> "BaseBranch":
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = dataframe.read_csv(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    @classmethod
    def from_csv(cls, **kwargs) -> "BaseBranch":
        """
        Creates a new branch instance by loading messages from a CSV file.

        This class method initializes a branch with messages imported from a specified CSV file, applying any provided read options.

        Args:
            **kwargs: Keyword arguments to be passed to the underlying pandas `read_csv` function, including the 'filename' and any additional pandas options.

        Returns:
            BaseBranch: A new instance of the class populated with messages loaded from the CSV file.
        """
        return cls._from_csv(**kwargs)

    @classmethod
    def from_json_string(cls, **kwargs) -> "BaseBranch":
        """
        Creates a new branch instance by loading messages from a JSON-formatted string.

        This method allows for the initialization of a branch with messages defined in a JSON string, providing a way to dynamically construct branches from serialized data.

        Args:
            **kwargs: Keyword arguments containing the JSON string and any additional options for JSON deserialization.

        Returns:
            BaseBranch: An instance of the class populated with messages defined in the provided JSON string.
        """
        return cls._from_json(**kwargs)

    @classmethod
    def _from_json(cls, filename: str, read_kwargs=None, **kwargs) -> "BaseBranch":
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = dataframe.read_json(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    def to_csv_file(
        self,
        filename: PATH_TYPE = "messages.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        **kwargs,
    ) -> None:
        """
        Exports the branch's messages to a CSV file.

        Args:
            filename (PATH_TYPE): The name or path of the file where messages will be saved.
            dir_exist_ok (bool): If True, allows directory creation if it doesn't exist.
            timestamp (bool): If True, appends a timestamp to the filename.
            time_prefix (bool): If True, adds a timestamp prefix to the filename.
            verbose (bool): If True, prints a message upon successful saving.
            clear (bool): If True, clears messages from the branch after saving.
            **kwargs: Additional keyword arguments for pandas to_csv method.
        """

        if not filename.endswith(".csv"):
            filename += ".csv"

        filename = SysUtil.create_path(
            self.datalogger.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )

        try:
            self.messages.to_csv(filename, **kwargs)
            if verbose:
                print(f"{len(self.messages)} messages saved to {filename}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to csv: {e}")

    def to_json_file(
        self,
        filename: PATH_TYPE = "messages.json",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        **kwargs,
    ) -> None:
        """
        Exports the branch messages to a JSON file.

        Args:
            filename: Destination path for the JSON file. Defaults to 'messages.json'.
            dir_exist_ok: If False, an error is raised if the dirctory exists. Defaults to True.
            timestamp: If True, appends a timestamp to the filename. Defaults to True.
            time_prefix: If True, prefixes the filename with a timestamp. Defaults to False.
            verbose: If True, prints a message upon successful export. Defaults to True.
            clear: If True, clears the messages after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_json().
        """

        if not filename.endswith(".json"):
            filename += ".json"

        filename = SysUtil.create_path(
            self.datalogger.persist_path,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
        )

        try:
            self.messages.to_json(
                filename, orient="records", lines=True, date_format="iso", **kwargs
            )
            if verbose:
                print(f"{len(self.messages)} messages saved to {filename}")
            if clear:
                self.clear_messages()
        except Exception as e:
            raise ValueError(f"Error in saving to json: {e}")

    def log_to_csv(
        self,
        filename: PATH_TYPE = "log.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep="[^_^]",
        **kwargs,
    ) -> None:
        """
        Exports the data logger contents to a CSV file.

        Args:
            filename: Destination path for the CSV file. Defaults to 'log.csv'.
            dir_exist_ok: If False, an error is raised if the directory exists. Defaults to True.
            timestamp: If True, appends a timestamp to the filename. Defaults to True.
            time_prefix: If True, prefixes the filename with a timestamp. Defaults to False.
            verbose: If True, prints a message upon successful export. Defaults to True.
            clear: If True, clears the logger after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_csv().
        """
        self.datalogger.to_csv_file(
            filename=filename,
            dir_exist_ok=dir_exist_ok,
            timestamp=timestamp,
            time_prefix=time_prefix,
            verbose=verbose,
            clear=clear,
            flatten_=flatten_,
            sep=sep,
            **kwargs,
        )

    def log_to_json(
        self,
        filename: PATH_TYPE = "log.json",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True,
        sep="[^_^]",
        **kwargs,
    ) -> None:
        """
        Exports the data logger contents to a JSON file.

        Args:
            filename: Destination path for the JSON file. Defaults to 'log.json'.
            dir_exist_ok: If False, an error is raised if the directory exists. Defaults to True.
            timestamp: If True, appends a timestamp to the filename. Defaults to True.
            time_prefix: If True, prefixes the filename with a timestamp. Defaults to False.
            verbose: If True, prints a message upon successful export. Defaults to True.
            clear: If True, clears the logger after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_json().
        """

        self.datalogger.to_json_file(
            filename=filename,
            dir_exist_ok=dir_exist_ok,
            timestamp=timestamp,
            time_prefix=time_prefix,
            verbose=verbose,
            clear=clear,
            flatten_=flatten_,
            sep=sep,
            **kwargs,
        )

    def load_log(self, filename, flattened=True, sep="[^_^]", verbose=True, **kwargs):
        """
        Loads logged data into the branch's datalogger from a specified file.

        Args:
            filename (str): The path to the log file (CSV or JSON) to be loaded.
            flattened (bool, optional): Indicates if the log entries are flattened. Default is True.
            sep (str, optional): The separator used if the log entries are flattened. Default is "[^_^]".
            verbose (bool, optional): If True, prints a message upon successful loading of log data. Default is True.
            **kwargs: Additional keyword arguments to pass to the file reading function.

        Raises:
            ValueError: If there's an error loading the log file.
        """
        df = ""
        try:
            if filename.endswith(".csv"):
                df = dataframe.read_csv(filename, **kwargs)

            elif filename.endswith(".json"):
                df = dataframe.read_json(filename, **kwargs)

            for _, row in df.iterrows():
                self.datalogger.log.append(
                    DLog.deserialize(
                        input_str=row.input_data,
                        output_str=row.output_data,
                        unflatten_=flattened,
                        sep=sep,
                    )
                )

            if verbose:
                print(f"Loaded {len(df)} logs from {filename}")
        except Exception as e:
            raise ValueError(f"Error in loading log: {e}")

    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the branch based on its node ID.

        Args:
            node_id: The unique identifier of the message to be removed.
        """
        MessageUtil.remove_message(self.messages, node_id)

    def update_message(self, node_id: str, column: str, value: Any) -> bool:
        """
        Updates a specific column of a message identified by node_id with a new value.

        Args:
            value: The new value to update the message with.
            node_id: The unique identifier of the message to update.
            column: The column of the message to update.
        """

        index = self.messages[self.messages["node_id"] == node_id].index[0]

        return dataframe.update_row(
            self.messages, row=index, column=column, value=value
        )

    def change_first_system_message(
        self, system: str | dict[str, Any] | System, sender: str | None = None
    ) -> None:
        """
        Updates the first system message with new content and/or sender.

        Args:
            system: The new system message content or a System object.
            sender: The identifier of the sender for the system message.
        """

        if len(self.messages[self.messages["role"] == "system"]) == 0:
            raise ValueError("There is no system message in the messages.")

        if not isinstance(system, (str, dict, System)):
            raise ValueError("Input cannot be converted into a system message.")

        if isinstance(system, (str, dict)):
            system = System(system, sender=sender)

        if isinstance(system, System):
            system.timestamp = SysUtil.get_timestamp()
            sys_index = self.messages[self.messages.role == "system"].index
            self.messages.loc[sys_index[0]] = system.to_pd_series()

    def rollback(self, steps: int) -> None:
        """
        Removes the last 'n' messages from the branch.

        Args:
            steps: The number of messages to remove from the end.
        """

        self.messages = dataframe.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the branch.
        """
        self.messages = dataframe.ln_DataFrame(columns=self._columns)

    def replace_keyword(
        self,
        keyword: str,
        replacement: str,
        column: str = "content",
        case_sensitive: bool = False,
    ) -> None:
        """
        Replaces occurrences of a specified keyword within a designated column of the branch's messages with a replacement string.

        This method iterates over the branch's messages and replaces all instances of the specified keyword found in the selected column. It can perform either case-sensitive or case-insensitive replacement.

        Args:
            keyword (str): The keyword to search for within the messages' specified column.
            replacement (str): The string to replace the keyword with whenever it is found.
            column (str, optional): The column in the messages dataframe where the search and replace operation should be performed. Defaults to "content".
            case_sensitive (bool, optional): Determines if the search for the keyword should be case-sensitive. Defaults to False, performing a case-insensitive search and replace.

        Raises:
            ValueError: If the specified column does not exist in the branch's messages dataframe.
        """
        dataframe.replace_keyword(
            self.messages,
            keyword,
            replacement,
            column=column,
            case_sensitive=case_sensitive,
        )

    def search_keywords(
        self,
        keywords: str | list[str],
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False,
    ) -> dataframe.ln_DataFrame:
        """
        Searches for messages containing specified keywords.

        Args:
            keywords (str | List[str]): A single keyword or a list of keywords to search for in the messages.
            case_sensitive (bool, optional): If True, the search is case-sensitive. Defaults to False.
            reset_index (bool, optional): If True, the returned dataframe will have a reset index. Defaults to False.
            dropna (bool, optional): If True, drops rows with NA values. Defaults to False.

        Returns:
            dataframe.ln_DataFrame: A dataframe containing messages that match the search criteria.
        """
        return dataframe.search_keywords(
            self.messages,
            keywords,
            case_sensitive=case_sensitive,
            reset_index=reset_index,
            dropna=dropna,
        )

    def extend(self, messages: dataframe.ln_DataFrame, **kwargs) -> None:
        """
        Extends the branch's messages with additional messages provided in a dataframe.

        Args:
            messages (dataframe.ln_DataFrame): A dataframe containing messages to be added to the branch.
            **kwargs: Additional keyword arguments for handling message extension, such as specifying merge strategies.

        Raises:
            ValueError: If the provided messages cannot be integrated due to format or schema discrepancies.
        """
        self.messages = MessageUtil.extend(self.messages, messages, **kwargs)

    def filter_by(
        self,
        role: str | None = None,
        sender: str | None = None,
        start_time=None,
        end_time=None,
        content_keywords: str | list[str] | None = None,
        case_sensitive: bool = False,
    ) -> dataframe.ln_DataFrame:
        """
        Filters the branch's messages based on various criteria such as role, sender, time, and content keywords.

        Args:
            role (str | None, optional): Filter messages by role (e.g., 'system', 'user').
            sender (str | None, optional): Filter messages by sender identifier.
            start_time: Filter messages sent after this time. The format should be compatible with pandas datetime handling.
            end_time: Filter messages sent before this time. The format should be compatible with pandas datetime handling.
            content_keywords (str | List[str] | None, optional): Filter messages containing specified keyword(s) in their content.
            case_sensitive (bool, optional): If True, keyword search is case-sensitive. Defaults to False.

        Returns:
            dataframe.ln_DataFrame: A filtered dataframe containing messages that match the specified criteria.
        """
        return MessageUtil.filter_messages_by(
            self.messages,
            role=role,
            sender=sender,
            start_time=start_time,
            end_time=end_time,
            content_keywords=content_keywords,
            case_sensitive=case_sensitive,
        )

    # noinspection PyTestUnpassedFixture
    def _info(self, use_sender: bool = False) -> dict[str, int]:
        """
        Helper method to generate summaries of messages either by role or sender.

        Args:
            use_sender: If True, summary is categorized by sender. Otherwise, by role.

        Returns:
            A dictionary summarizing the count of messages either by role or sender.
        """

        messages = self.messages["sender"] if use_sender else self.messages["role"]
        result = messages.value_counts().to_dict()
        result["total"] = len(self.messages)
        return result
