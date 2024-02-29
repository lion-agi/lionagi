import json
from abc import ABC
from typing import Any, Dict, List
import pandas as pd
from pathlib import Path
from datetime import datetime

from lionagi.util import PathUtil, to_dict, to_df

from lionagi.core.schema import BaseRelatableNode, DataLogger, DLog


from lionagi.core.session.base.schema import (
    BranchColumns,
    System,
    Instruction,
    BaseMessage,
)
from lionagi.core.session.base.util import MessageUtil


class BaseBranch(BaseRelatableNode, ABC):
    """
    Base class for managing branches of conversation, incorporating messages
    and logging functionality.

    Attributes:
        messages (pd.DataFrame): Holds the messages in the branch.
        datalogger (DataLogger): Logs data related to the branch's operation.
        persist_path (Path | str): Filesystem path for data persistence.
    """

    _columns: List[str] = BranchColumns.COLUMNS.value

    def __init__(
        self,
        messages: pd.DataFrame | None = None,
        datalogger: DataLogger | None = None,
        persist_path: Path | str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if isinstance(messages, pd.DataFrame):
            if MessageUtil.validate_messages(messages):
                self.messages = messages
            else:
                raise ValueError("Invalid messages format")
        else:
            self.messages = pd.DataFrame(columns=self._columns)

        self.datalogger = datalogger if datalogger else DataLogger(persist_path=persist_path)

    def add_message(
        self,
        system: Dict | List | System | None = None,
        instruction: Dict | List | Instruction | None = None,
        context: str | Dict[str, Any] | None = None,
        response: Dict | List | BaseMessage | None = None,
        **kwargs,
    ) -> None:
        """
        Adds a message to the branch.

        Args:
            system: Information for creating a System message.
            instruction: Information for creating an Instruction message.
            context: Context information for the message.
            response: Response data for creating a message.
            **kwargs: Additional keyword arguments for message creation.
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
    ) -> List[Dict[str, Any]]:
        """
        Converts messages to a list of dictionaries formatted for chat completion,
        optionally including sender information.

        Args:
            with_sender: Flag to include sender information in the output.

        Returns:
            A list of message dictionaries, each with 'role' and 'content' keys,
            and optionally prefixed by 'Sender' if with_sender is True.
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
    def chat_messages(self) -> List[Dict[str, Any]]:
        """
        Retrieves all chat messages without sender information.

        Returns:
            A list of dictionaries representing chat messages.
        """

        return self._to_chatcompletion_message()

    @property
    def chat_messages_with_sender(self) -> List[Dict[str, Any]]:
        """
        Retrieves all chat messages, including sender information.

        Returns:
            A list of dictionaries representing chat messages, each prefixed with its sender.
        """

        return self._to_chatcompletion_message(with_sender=True)

    @property
    def last_message(self) -> pd.DataFrame:
        """
        Retrieves the last message from the branch as a pandas Series.

        Returns:
            A pandas Series representing the last message in the branch.
        """

        return MessageUtil.get_message_rows(self.messages, n=1, from_="last")

    @property
    def last_message_content(self) -> Dict[str, Any]:
        """
        Extracts the content of the last message in the branch.

        Returns:
            A dictionary representing the content of the last message.
        """

        return to_dict(self.messages.content.iloc[-1])

    @property
    def first_system(self) -> pd.DataFrame:
        """
        Retrieves the first message marked with the 'system' role.

        Returns:
            A pandas Series representing the first 'system' message in the branch.
        """

        return MessageUtil.get_message_rows(
            self.messages, role="system", n=1, from_="front"
        )

    @property
    def last_response(self) -> pd.DataFrame:
        """
        Retrieves the last message marked with the 'assistant' role.

        Returns:
            A pandas Series representing the last 'assistant' (response) message in the branch.
        """

        return MessageUtil.get_message_rows(
            self.messages, role="assistant", n=1, from_="last"
        )

    @property
    def last_response_content(self) -> Dict[str, Any]:
        """
        Extracts the content of the last 'assistant' (response) message.

        Returns:
            A dictionary representing the content of the last 'assistant' message.
        """

        return to_dict(self.last_response.content.iloc[-1])

    @property
    def action_request(self) -> pd.DataFrame:
        """
        Filters and retrieves all messages sent by 'action_request'.

        Returns:
            A pandas DataFrame containing all 'action_request' messages.
        """

        return to_df(self.messages[self.messages.sender == "action_request"])

    @property
    def action_response(self) -> pd.DataFrame:
        """
        Filters and retrieves all messages sent by 'action_response'.

        Returns:
            A pandas DataFrame containing all 'action_response' messages.
        """

        return to_df(self.messages[self.messages.sender == "action_response"])

    @property
    def responses(self) -> pd.DataFrame:
        """
        Retrieves all messages marked with the 'assistant' role.

        Returns:
            A pandas DataFrame containing all messages with an 'assistant' role.
        """

        return to_df(self.messages[self.messages.role == "assistant"])

    @property
    def assistant_responses(self) -> pd.DataFrame:
        """
        Filters 'assistant' role messages excluding 'action_request' and 'action_response'.

        Returns:
            A pandas DataFrame of 'assistant' messages excluding action requests/responses.
        """

        a_responses = self.responses[self.responses.sender != "action_response"]
        a_responses = a_responses[a_responses.sender != "action_request"]
        return to_df(a_responses)

    @property
    def info(self) -> Dict[str, Any]:
        """
        Summarizes branch information, including message counts by role.

        Returns:
            A dictionary containing counts of messages categorized by their role.
        """

        return self._info()

    @property
    def sender_info(self) -> Dict[str, int]:
        """
        Provides a summary of message counts categorized by sender.

        Returns:
            A dictionary with senders as keys and counts of their messages as values.
        """

        return self._info(use_sender=True)

    @property
    def describe(self) -> Dict[str, Any]:
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
        messages = MessageUtil.read_csv(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    @classmethod
    def from_csv(cls, **kwargs) -> "BaseBranch":

        return cls._from_csv(**kwargs)

    @classmethod
    def from_json(cls, **kwargs) -> "BaseBranch":

        return cls._from_json(**kwargs)

    @classmethod
    def _from_json(cls, filename: str, read_kwargs=None, **kwargs) -> "BaseBranch":
        read_kwargs = {} if read_kwargs is None else read_kwargs
        messages = MessageUtil.read_json(filename, **read_kwargs)
        return cls(messages=messages, **kwargs)

    def to_csv_file(
        self,
        filename: str | Path = "messages.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        **kwargs,
    ) -> None:
        """
        Exports the branch messages to a CSV file.

        Args:
            filepath: Destination path for the CSV file. Defaults to 'messages.csv'.
            dir_exist_ok: If False, an error is raised if the directory exists. Defaults to True.
            timestamp: If True, appends a timestamp to the filename. Defaults to True.
            time_prefix: If True, prefixes the filename with a timestamp. Defaults to False.
            verbose: If True, prints a message upon successful export. Defaults to True.
            clear: If True, clears the messages after exporting. Defaults to True.
            **kwargs: Additional keyword arguments for pandas.DataFrame.to_csv().
        """

        if not filename.endswith(".csv"):
            filename += ".csv"

        filename = PathUtil.create_path(
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
        filename: str | Path = "messages.json",
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

        filename = PathUtil.create_path(
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
        filename: str | Path = "log.csv",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True, 
        sep='[^_^]',
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
        filename: str | Path = "log.json",
        dir_exist_ok: bool = True,
        timestamp: bool = True,
        time_prefix: bool = False,
        verbose: bool = True,
        clear: bool = True,
        flatten_=True, 
        sep='[^_^]',
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
    
    def load_log(
        self, 
        filename,
        flattened=True, 
        sep='[^_^]',
        verbose=True,
        **kwargs
    ):
        df = ''
        try:        
            if filename.endswith('.csv'):
                df = MessageUtil.read_csv(filename, **kwargs)
                
            elif filename.endswith('.json'):
                df = MessageUtil.read_json(filename, **kwargs)

            for _, row in df.iterrows():
                self.datalogger.log.append(DLog.deserialize(
                    input_str=row.input_data, 
                    output_str = row.output_data,
                    unflatten_=flattened, 
                    sep=sep,
                ))
        
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

    def update_message(self, node_id: str, col: str, value: Any) -> bool:
        """
        Updates a specific column of a message identified by node_id with a new value.

        Args:
            value: The new value to update the message with.
            node_id: The unique identifier of the message to update.
            col: The column of the message to update.
        """

        index = self.messages[self.messages['node_id'] == node_id].index[0]

        return MessageUtil.update_row(
            self.messages, row=index, col=col, value=value
        )

    def change_first_system_message(
        self, system: str | Dict[str, Any] | System, sender: str | None = None
    ) -> None:
        """
        Updates the first system message with new content and/or sender.

        Args:
            system: The new system message content or a System object.
            sender: The identifier of the sender for the system message.
        """

        if len(self.messages[self.messages["role"] == "system"]) == 0:
            raise ValueError("There is no system message in the messages.")

        if not isinstance(system, (str, Dict, System)):
            raise ValueError("Input cannot be converted into a system message.")

        if isinstance(system, (str, Dict)):
            system = System(system, sender=sender)

        if isinstance(system, System):
            system.timestamp = datetime.now().isoformat()
            sys_index = self.messages[self.messages.role == "system"].index
            self.messages.loc[sys_index[0]] = system.to_pd_series()

    def rollback(self, steps: int) -> None:
        """
        Removes the last 'n' messages from the branch.

        Args:
            steps: The number of messages to remove from the end.
        """

        self.messages = MessageUtil.remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the branch.
        """
        self.messages = pd.DataFrame(columns=self._columns)

    def replace_keyword(
        self,
        keyword: str,
        replacement: str,
        col: str = "content",
        case_sensitive: bool = False,
    ) -> None:

        MessageUtil.replace_keyword(
            self.messages, keyword, replacement, col=col, case_sensitive=case_sensitive
        )

    def search_keywords(
        self,
        keywords: str | list[str],
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False,
    ) -> pd.DataFrame:
        return MessageUtil.search_keywords(
            self.messages, keywords, case_sensitive=case_sensitive, reset_index=reset_index, dropna=dropna
        )

    def extend(self, messages: pd.DataFrame, **kwargs) -> None:

        self.messages = MessageUtil.extend(self.messages, messages, **kwargs)

    def filter_by(
        self,
        role: str | None = None,
        sender: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        content_keywords: str | list[str] | None = None,
        case_sensitive: bool = False,
    ) -> pd.DataFrame:

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
    def _info(self, use_sender: bool = False) -> Dict[str, int]:
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
