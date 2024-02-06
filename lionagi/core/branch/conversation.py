import json
import pandas as pd
from datetime import datetime
from typing import Any, Optional, Dict, Union
from lionagi.schema import DataLogger
from lionagi.utils import lcall, as_dict
from ..messages.messages import Message, System, Instruction, Response
from ..core_util import sign_message, validate_messages


class Conversation:
    """
    Represents a conversation with messages, tools, and instructions.

    A `Conversation` is a container for messages exchanged in a conversation, as well as tools and instructions
    for interacting with external services or tools.

    Attributes:
        messages (pd.DataFrame): A DataFrame containing conversation messages.
        _logger (DataLogger): An instance of DataLogger for logging.
    """

    def __init__(self, dir: Optional[str] = None) -> None:
        """
        Initializes a Conversation object with an empty DataFrame for messages and a DataLogger.

        Args:
            dir (Optional[str]): The directory path for storing logs. Defaults to None.

        Examples:
            >>> conversation = Conversation(dir='logs/')
        """
        self.messages = pd.DataFrame(columns=["node_id", "role", "sender", "timestamp", "content"])
        self.logger = DataLogger(dir=dir)

    def _create_message(
        self,
        system: Optional[Union[dict, list, System]] = None,
        instruction: Optional[Union[dict, list, Instruction]] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        response: Optional[Union[dict, list, Response]] = None,
        sender: Optional[str] = None
    ) -> Message:
        """
        Creates a Message object based on the given parameters.

        Only one of `system`, `instruction`, or `response` can be provided to create a message.

        Args:
            system (Optional[Union[dict, list, System]]): The system message content.
            instruction (Optional[Union[dict, list, Instruction]]): The instruction content.
            context (Optional[Union[str, Dict[str, Any]]]): The context associated with the instruction.
            response (Optional[Union[dict, list, Response]]): The response content.
            sender (Optional[str]): The sender of the message.

        Returns:
            Message: A message object created from the provided parameters.

        Raises:
            ValueError: If more than one or none of the parameters (system, instruction, response) are provided.

        Examples:
            >>> conversation = Conversation()
            >>> msg = conversation._create_message(system="System message", sender="system")
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
        self,
        system: Optional[Union[dict, list, System]] = None,
        instruction: Optional[Union[dict, list, Instruction]] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        response: Optional[Union[dict, list, Response]] = None,
        sender: Optional[str] = None
    ) -> None:
        """
        Creates and adds a new message to the conversation's messages DataFrame.
        Args:
            system (Optional[System]): Content for a system message.
            instruction (Optional[Instruction]): Content for an instruction message.
            context (Optional[Union[str, Dict[str, Any]]]): Context for the instruction message.
            response (Optional[Response]): Content for a response message.
            sender (Optional[str]): The sender of the message.

        Examples:
            >>> conversation = Conversation()
            >>> conversation.add_message(instruction="What's the weather?", sender="user")
        """
        msg = self._create_message(
            system=system, instruction=instruction, 
            context=context, response=response, sender=sender
        )
        message_dict = msg.to_dict()
        if isinstance(as_dict(message_dict['content']), dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now()
        self.messages.loc[len(self.messages)] = message_dict
    
    @property
    def last_row(self) -> pd.Series:
        """
        Retrieves the last row from the messages DataFrame.

        Returns:
            pd.Series: A Series object representing the last message.
        """
        return self.messages.iloc[-1]
    
    @property
    def first_system(self) -> pd.Series:
        """
        Retrieves the first system message from the messages DataFrame.

        Returns:
            pd.Series: A Series object representing the first system message.
        """
        return self.messages[self.messages.role == 'system'].iloc[0]
        
    @property
    def last_response(self) -> pd.Series:
        """
        Retrieves the last response message from the messages DataFrame.

        Returns:
            pd.Series: A Series object representing the last response message.
        """
        return self.get_last_rows(role='assistant')
    
    @property
    def last_instruction(self) -> pd.Series:
        """
        Retrieves the last instruction message from the messages DataFrame.

        Returns:
            pd.Series: A Series object representing the last instruction message.
        """
        return self.get_last_rows(role='user')
    
    def get_last_rows(
        self, 
        sender: Optional[str] = None, 
        role: Optional[str] = None, 
        n: int = 1, 
        sign_ = False
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Retrieves the last n rows from the messages DataFrame filtered by sender or role.

        Args:
            sender (Optional[str]): The sender filter for the messages.
            role (Optional[str]): The role filter for the messages.
            n (int): The number of rows to retrieve.
            sign_: If sign messages with a sender identifier.

        Returns:
            Union[pd.DataFrame, pd.Series]: The last n messages as a DataFrame or a single message as a Series.

        Raises:
            ValueError: If both sender and role are provided or if none is provided.
        """

        if sender is None and role is None:
            outs = self.messages.iloc[-n:]
        elif sender and role:
            outs = self.messages[(self.messages['sender'] == sender) & (self.messages['role'] == role)].iloc[-n:]
        elif sender:
            outs = self.messages[self.messages['sender'] == sender].iloc[-n:]
        else:
            outs = self.messages[self.messages['role'] == role].iloc[-n:]

        return sign_message(outs, sender) if sign_ else outs

    def filter_messages_by(
        self,
        role: Optional[str] = None, 
        sender: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        content_keywords: Optional[Union[str, list]] = None,
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        Retrieves messages filtered by a specific criterion.

        Args:
            role (Optional[str]): The role to filter the messages.
            sender (Optional[str]): The sender to filter the messages.
            start_time (Optional[datetime]): The start time to filter the messages.
            end_time (Optional[datetime]): The end time to filter the messages.
            content_keywords (Optional[Union[str, list]]): The content to filter the messages.
            case_sensitive (bool): Flag to indicate if the search should be case sensitive. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing filtered messages.

        Raises:
            ValueError: If more than one or none of the filtering criteria are provided.
        """
        outs = self.messages.copy()
        
        if content_keywords:
            outs = self.search_keywords(content_keywords, case_sensitive)
        
        outs = outs[outs['role'] == role] if role else outs
        outs = outs[outs['sender'] == sender] if sender else outs
        outs = outs[outs['timestamp'] > start_time] if start_time else outs
        outs = outs[outs['timestamp'] < end_time] if end_time else outs
        return outs

    def replace_keyword(
        self, 
        keyword: str, 
        replacement: str, 
        case_sensitive: bool = False
    ) -> None:
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

    def search_keywords(
        self, 
        keywords: Union[str, list],
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        Searches for a keyword in the content of all messages and returns the messages containing it.

        Args:
            keywords (str): The keywords to search for.
            case_sensitive (bool, optional): Flag to indicate if the search should be case sensitive. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages with the specified keyword.
        """
        if isinstance(keywords, list):
            keywords = '|'.join(keywords)
        if not case_sensitive:
            return self.messages[
                self.messages["content"].str.contains(keywords, case=False)
            ]
        return self.messages[self.messages["content"].str.contains(keywords)]

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

    def update_messages_content(
        self, 
        message_id: str, 
        col: str, 
        value: Any
    ) -> bool:
        """
        Updates the content of a specific message in the conversation.

        Args:
            message_id (str): The ID of the message to be updated.
            col (str): The column of the message that needs to be updated.
            value (Any): The new value to be set for the specified column.

        Returns:
            bool: True if the update was successful, False otherwise.

        Examples:
            >>> conversation = Conversation()
            >>> conversation.add_message(system="Initial message", sender="system")
            >>> success = conversation.update_messages_content(
            ...     message_id="1", col="content", value="Updated message")
        """
        index = self.messages.index[self.messages["id_"] == message_id].tolist()
        if index:
            self.messages.at[index[0], col] = value
            return True
        return False

    def info(self, use_sender: bool = False) -> Dict[str, int]:
        """
        Provides a summary of the conversation messages.

        Args:
            use_sender (bool, optional): Determines whether to summarize by sender or by role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary containing counts of messages either by role or sender.
        """
        messages = self.messages['sender'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.messages)
        return result

    @property
    def describe(self) -> Dict[str, Any]:
        """
        Describes the conversation with various statistics and information.

        Returns:
            Dict[str, Any]: A dictionary containing information such as total number of messages, summary by role,
                            and individual messages.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self.info(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    def history(
        self, begin_: Optional[datetime] = None, end_: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieves a history of messages within a specified date range.

        Args:
            begin_ (Optional[datetime], optional): The start date of the message history. Defaults to None.
            end_ (Optional[datetime], optional): The end date of the message history. Defaults to None.

        Returns:
            pd.DataFrame: A DataFrame containing messages within the specified date range.
        """
        
        if isinstance(begin_, str):
            begin_ = datetime.strptime(begin_, '%Y-%m-%d')
        if isinstance(end_, str):
            end_ = datetime.strptime(end_, '%Y-%m-%d')
        if begin_ and end_:
            return self.messages[
                (self.messages["timestamp"].dt.date >= begin_.date())
                & (self.messages["timestamp"].dt.date <= end_.date())
            ]
        elif begin_:
            return self.messages[(self.messages["timestamp"].dt.date >= begin_.date())]
        elif end_:
            return self.messages[(self.messages["timestamp"].dt.date <= end_.date())]
        return self.messages

    def clone(self) -> 'Conversation':
        """
        Creates a clone of the current conversation.

        Returns:
            Conversation: A new Conversation object that is a clone of the current conversation.
        """
        cloned = Conversation()
        cloned.logger.set_dir(self.logger.dir)
        cloned.messages = self.messages.copy()
        return cloned

    # def merge_conversation(self, other: 'Conversation', update: bool = False,) -> None:
    #     """
    #     Merges another conversation into the current one.
    #
    #     Args:
    #         other (Conversation): The other conversation to merge with the current one.
    #         update (bool, optional): If True, updates the first system message before merging. Defaults to False.
    #     """
    #     if update:
    #         self.first_system = other.first_system.copy()
    #     df = pd.concat([self.messages.copy(), other.messages.copy()], ignore_index=True)
    #     self.messages = df.drop_duplicates().reset_index(drop=True, inplace=True)

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

    def extend(self, messages: pd.DataFrame, **kwargs) -> None:
        """
        Extends the current conversation messages with additional messages from a DataFrame.

        Args:
            messages (pd.DataFrame): The DataFrame containing messages to be added to the conversation.
            kwargs: for pd.df.drop_duplicates
        """
        
        validate_messages(messages)
        try:
            if len(messages.dropna(how='all')) > 0 and len(self.messages.dropna(how='all')) > 0:
                self.messages = pd.concat([self.messages, messages], ignore_index=True)
                self.messages.drop_duplicates(
                    inplace=True, subset=['node_id'], keep='first', **kwargs
                )
                self.messages.reset_index(drop=True, inplace=True)
                return
        except Exception as e:
            raise ValueError(f"Error in extending messages: {e}")
