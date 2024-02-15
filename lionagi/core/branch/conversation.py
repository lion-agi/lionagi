import json
import pandas as pd
from datetime import datetime
from typing import Any, Optional, Dict, Union

from lionagi.utils.sys_util import as_dict, create_copy, strip_lower, to_df
from lionagi.utils.call_util import lcall
from ..messages.messages import Message, System, Instruction, Response

class Conversation:
    """
    A class to represent a conversation, encapsulating messages within a pandas DataFrame.
    
    Attributes:
        messages (pd.DataFrame): A DataFrame holding conversation messages with columns specified in _cols.
    """
    
    _cols = ["node_id", "role", "sender", "timestamp", "content"]

    def __init__(self) -> None:
        """
        Initializes a Conversation instance with an empty DataFrame structured to hold messages.
        """
        self.messages = pd.DataFrame(columns=Conversation._cols)

    @classmethod
    def from_csv(cls, filepath: str, **kwargs) -> 'Conversation':
        """
        Create a Conversation instance from a CSV file containing messages.

        Args:
            filepath (str): The path to the CSV file to be loaded.
            **kwargs: Additional keyword arguments passed to pandas.read_csv function.

        Returns:
            Conversation: An instance of Conversation with messages loaded from the specified CSV file.
        """
        messages = pd.read_csv(filepath)
        messages = to_df(messages)
        self = cls(messages=messages, **kwargs)
        return self
    
    @classmethod
    def from_json(cls, filepath: str, **kwargs) -> 'Conversation':
        """
        Create a Conversation instance from a JSON file containing messages.

        Args:
            filepath (str): The path to the JSON file to be loaded.
            **kwargs: Additional keyword arguments passed to pandas.read_json function.

        Returns:
            Conversation: An instance of Conversation with messages loaded from the specified JSON file.
        """
        messages = pd.read_json(filepath, orient="records", lines=True)
        messages = to_df(messages)
        self = cls(messages=messages, **kwargs)
        return self
        
    @property
    def last_row(self) -> pd.Series:
        """
        Retrieve the last row from the conversation messages as a pandas Series.

        Returns:
            pd.Series: The last message in the conversation.
        """
        return get_rows(self.messages, n=1, from_='last')
    
    @property
    def first_system(self) -> pd.Series:
        """
        Retrieve the first system message from the conversation.

        Returns:
            pd.Series: The first message in the conversation where the role is 'system'.
        """
        return get_rows(self.messages, role='system', n=1, from_='front')
        
    @property
    def last_response(self) -> pd.Series:
        """
        Retrieve the last response message from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'assistant'.
        """
        return get_rows(self.messages, role='assistant', n=1, from_='last')

    @property
    def last_response_content(self) -> Dict:
        """
        Retrieve the last response message content from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'assistant'.
        """
        return as_dict(self.last_response.content.iloc[-1])

    @property
    def last_instruction(self) -> pd.Series:
        """
        Retrieve the last instruction message from the conversation.

        Returns:
            pd.Series: The last message in the conversation where the role is 'user'.
        """
        return get_rows(self.messages, role='user', n=1, from_='last')

    @property
    def last_action_request(self):
        """
        Retrieve the last action request message from the conversation.

        Returns:
            pd.Series: The last message in the conversation with sender 'action_request'.
        """
        return get_rows(self.messages, sender='action_request', n=1, from_='last')
    
    @property
    def last_action_response(self):
        """
        Retrieve the last action response message from the conversation.

        Returns:
            pd.Series: The last message in the conversation with sender 'action_response'.
        """
        return get_rows(self.messages, sender='action_response', n=1, from_='last')

    @property
    def len_messages(self):
        """
        Get the total number of messages in the conversation.

        Returns:
            int: The total number of messages.
        """
        return len(self.messages)
    
    @property
    def len_instructions(self):
        """
        Get the total number of instruction messages (messages with role 'user') in the conversation.

        Returns:
            int: The total number of instruction messages.
        """
        return len(self.messages[self.messages.role == 'user'])
    
    @property
    def len_responses(self):
        """
        Get the total number of response messages (messages with role 'assistant') in the conversation.

        Returns:
            int: The total number of response messages.
        """

        return len(self.messages[self.messages.role == 'assistant'])
    
    @property
    def len_systems(self):
        """
        Get the total number of system messages (messages with role 'system') in the conversation.

        Returns:
            int: The total number of system messages.
        """
        return len(self.messages[self.messages.role == 'system'])

    @property
    def info(self):
        """
        Get a summary of the conversation messages categorized by role.

        Returns:
            Dict[str, int]: A dictionary with keys as message roles and values as counts.
        """

        return self._info()
    
    @property
    def sender_info(self):
        """
        Provides a descriptive summary of the conversation, including the total number of messages,
        a summary by role, and the first five messages.

        Returns:
            Dict[str, Any]: A dictionary containing the total number of messages, summary by role,
            and a list of the first five message dictionaries.
        """
        return self._info(use_sender=True)
    
    @property
    def describe(self) -> Dict[str, Any]:
        """
        Provides a descriptive summary of the conversation, including the total number of messages,
        a summary by role, and the first five messages.

        Returns:
            Dict[str, Any]: A dictionary containing the total number of messages, summary by role, and a list of the first maximum five message dictionaries.
        """
        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ][: self.len_messages -1 if self.len_messages < 5 else 5],
        }

    def clone(self, num: Optional[int] = None) -> 'Conversation':
        """
        Creates a copy or multiple copies of the current Conversation instance.

        Args:
            num (Optional[int], optional): The number of copies to create. If None, a single copy is created.
                                           Defaults to None.

        Returns:
            Conversation: A new Conversation instance or a list of Conversation instances if num is specified.
        """
        cloned = Conversation()
        cloned.logger.set_dir(self.logger.dir)
        cloned.messages = self.messages.copy()
        if num:
            return create_copy(cloned, num=num)
        return cloned

    def add_message(
        self,
        system: Optional[Union[dict, list, System]] = None,
        instruction: Optional[Union[dict, list, Instruction]] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        response: Optional[Union[dict, list, Response]] = None,
        sender: Optional[str] = None
    ) -> None:
        """
        Adds a message to the conversation.

        Args:
            system (Optional[Union[dict, list, System]], optional): System message content or object.
            instruction (Optional[Union[dict, list, Instruction]], optional): Instruction message content or object.
            context (Optional[Union[str, Dict[str, Any]]], optional): Context for the message.
            response (Optional[Union[dict, list, Response]], optional): Response message content or object.
            sender (Optional[str], optional): The sender of the message.

        Raises:
            ValueError: If the content cannot be converted to a JSON string.
        """
        msg = self._create_message(
            system=system, instruction=instruction, 
            context=context, response=response, sender=sender
        )
        message_dict = msg.to_dict()
        if isinstance(as_dict(message_dict['content']), dict):
            message_dict['content'] = json.dumps(message_dict['content'])
        message_dict['timestamp'] = datetime.now().isoformat()
        self.messages.loc[len(self.messages)] = message_dict
    
    def remove_message(self, node_id: str) -> None:
        """
        Removes a message from the conversation based on its node_id.

        Args:
            node_id (str): The node_id of the message to be removed.
        """
        _remove_message(self.messages, node_id)
    
    def update_message(
        self, value: Any, node_id: Optional[str] = None, col: str = 'node_id'
    ) -> None:
        """
        Updates a message in the conversation based on its node_id.

        Args:
            value (Any): The new value to update the message with.
            node_id (Optional[str], optional): The node_id of the message to be updated. Defaults to None.
            col (str, optional): The column to be updated. Defaults to 'node_id'.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        return _update_row(self.messages, node_id=node_id, col=col, value=value)
    
    def change_first_system_message(
        self, system: Union[str, Dict[str, Any], System], sender: Optional[str] = None
    ):
        """
        Updates the first system message in the conversation.

        Args:
            system (Union[str, Dict[str, Any], System]): The new system message content, which can be a string,
                                                         a dictionary of message content, or a System object.
            sender (Optional[str], optional): The sender of the system message. Defaults to None.

        Raises:
            ValueError: If there are no system messages in the conversation or if the input cannot be
                        converted into a system message.
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

        Args:
            steps (int): The number of messages to remove from the end of the conversation.

        Raises:
            ValueError: If 'steps' is not a positive integer or exceeds the number of messages.
        """
        return _remove_last_n_rows(self.messages, steps)

    def clear_messages(self) -> None:
        """
        Clears all messages from the conversation, resetting it to an empty state.
        """
        self.messages = pd.DataFrame(columns=Conversation._cols)

    def to_csv(self, filepath: str, **kwargs) -> None:
        """
        Exports the conversation messages to a CSV file.

        Args:
            filepath (str): The path to the file where the CSV will be saved.
            **kwargs: Additional keyword arguments passed to pandas.DataFrame.to_csv() method.
        """
        self.messages.to_csv(filepath, **kwargs)

    def to_json(self, filepath: str) -> None:
        """
        Exports the conversation messages to a JSON file.

        Args:
            filepath (str): The path to the file where the JSON will be saved.
            **kwargs: Additional keyword arguments passed to pandas.DataFrame.to_json() method, such as
                      'orient', 'lines', and 'date_format'.

        Note:
            The recommended kwargs for compatibility with the from_json class method are
            orient='records', lines=True, and date_format='iso'.
        """
        self.messages.to_json(
            filepath, orient="records", lines=True, date_format="iso")

    def replace_keyword(
        self,
        keyword: str, 
        replacement: str, 
        col: str = 'content',
        case_sensitive: bool = False
    ) -> None:
        """
        Replaces all occurrences of a keyword in a specified column of the conversation's messages with a given replacement.

        Args:
            keyword (str): The keyword to be replaced.
            replacement (str): The string to replace the keyword with.
            col (str, optional): The column where the replacement should occur. Defaults to 'content'.
            case_sensitive (bool, optional): If True, the replacement is case sensitive. Defaults to False.
        """
        _replace_keyword(
            self.messages, keyword, replacement, col=col, 
            case_sensitive=case_sensitive
        )
        
    def search_keywords(
        self, 
        keywords: Union[str, list],
        case_sensitive: bool = False, reset_index: bool = False, dropna: bool = False
    ) -> pd.DataFrame:
        """
        Searches for messages containing specified keywords within the conversation.

        Args:
            keywords (Union[str, list]): The keyword(s) to search for within the conversation's messages.
            case_sensitive (bool, optional): If True, the search is case sensitive. Defaults to False.
            reset_index (bool, optional): If True, resets the index of the resulting DataFrame. Defaults to False.
            dropna (bool, optional): If True, drops messages with NA values before searching. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages that match the search criteria.
        """
        return _search_keywords(
            self.messages, keywords, case_sensitive, reset_index, dropna
        )
        
    def extend(self, messages: pd.DataFrame, **kwargs) -> None:
        """
        Extends the conversation by appending new messages, optionally avoiding duplicates based on specified criteria.

        Args:
            messages (pd.DataFrame): A DataFrame containing new messages to append to the conversation.
            **kwargs: Additional keyword arguments for handling duplicates (passed to pandas' drop_duplicates method).
        """
        self.messages = _extend(self.messages, messages, **kwargs)
        
    def filter_by(
        self,
        role: Optional[str] = None, 
        sender: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        content_keywords: Optional[Union[str, list]] = None,
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        Filters the conversation's messages based on specified criteria such as role, sender, time range, and keywords.

        Args:
            role (Optional[str]): Filter messages by role (e.g., 'user', 'assistant', 'system').
            sender (Optional[str]): Filter messages by sender.
            start_time (Optional[datetime]): Filter messages sent after this time.
            end_time (Optional[datetime]): Filter messages sent before this time.
            content_keywords (Optional[Union[str, list]]): Filter messages containing these keywords.
            case_sensitive (bool, optional): If True, keyword search is case sensitive. Defaults to False.

        Returns:
            pd.DataFrame: A DataFrame containing messages that match the filter criteria.
        """
        return _filter_messages_by(
            self.messages, role=role, sender=sender, 
            start_time=start_time, end_time=end_time, 
            content_keywords=content_keywords, case_sensitive=case_sensitive
        )
        
    def _create_message(
        self,
        system: Optional[Union[dict, list, System]] = None,
        instruction: Optional[Union[dict, list, Instruction]] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        response: Optional[Union[dict, list, Response]] = None,
        sender: Optional[str] = None
    ) -> Message:
        """
        Creates a message object based on the given parameters, ensuring only one message type is specified.

        Args:
            system (Optional[Union[dict, list, System]]): System message to be added.
            instruction (Optional[Union[dict, list, Instruction]]): Instruction message to be added.
            context (Optional[Union[str, Dict[str, Any]]]): Context for the instruction message.
            response (Optional[Union[dict, list, Response]]): Response message to be added.
            sender (Optional[str]): The sender of the message.

        Returns:
            Message: A Message object created from the provided parameters.

        Raises:
            ValueError: If more than one message type is specified or if the parameters do not form a valid message.
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

    def _info(self, use_sender: bool = False) -> Dict[str, int]:
        """
        Generates a summary of the conversation's messages, either by role or sender.

        Args:
            use_sender (bool, optional): If True, generates the summary based on sender. If False, uses role. Defaults to False.

        Returns:
            Dict[str, int]: A dictionary with counts of messages, categorized either by role or sender.
        """
        messages = self.messages['sender'] if use_sender else self.messages['role']
        result = messages.value_counts().to_dict()
        result['total'] = len(self.len_messages)
        return result

def validate_messages(messages):
    """
    Validates the structure and content of a DataFrame containing conversation messages.

    Args:
        messages (pd.DataFrame): The DataFrame containing conversation messages to validate.

    Returns:
        bool: True if the DataFrame is valid, raises a ValueError otherwise.

    Raises:
        ValueError: If the DataFrame has unmatched columns, contains null values, has an unsupported role, or
                    if the content cannot be parsed as a JSON string.
    """
    if list(messages.columns) != ['node_id', 'role', 'sender', 'timestamp', 'content']:
        raise ValueError('Invalid messages dataframe. Unmatched columns.')
    if messages.isnull().values.any():
        raise ValueError('Invalid messages dataframe. Cannot have null.')
    if not all(role in ['system', 'user', 'assistant'] for role in messages['role'].unique()):
        raise ValueError('Invalid messages dataframe. Cannot have role other than ["system", "user", "assistant"].')
    for cont in messages['content']:
        if cont.startswith('Sender'):
            cont = cont.split(':', 1)[1]
        try:
            json.loads(cont)
        except:
            raise ValueError('Invalid messages dataframe. Content expect json string.')
    return True

def _sign_message(messages, sender: str):
    """
    Prefixes each message in the DataFrame with 'Sender <sender>:' to indicate the message's origin.

    Args:
        messages (pd.DataFrame): The DataFrame containing conversation messages to sign.
        sender (str): The name or identifier of the sender to prefix the messages with.

    Returns:
        pd.DataFrame: The DataFrame with updated messages signed by the specified sender.

    Raises:
        ValueError: If the sender is None or equivalent to the string 'none'.
    """
    if sender is None or strip_lower(sender) == 'none':
        raise ValueError("sender cannot be None")
    df = messages.copy()

    for i in df.index:
        if not df.loc[i, 'content'].startswith('Sender'):
            df.loc[i, 'content'] = f"Sender {sender}: {df.loc[i, 'content']}"
        else:
            content = df.loc[i, 'content'].split(':', 1)[1]
            df.loc[i, 'content'] = f"Sender {sender}: {content}"
            
    return to_df(df)

def _search_keywords(
    messages, 
    keywords: Union[str, list],
    case_sensitive: bool = False, reset_index=False, dropna=False
):
    """
    Searches for keywords in the 'content' column of a DataFrame and returns matching rows.

    Args:
        messages (pd.DataFrame): The DataFrame to search within.
        keywords (Union[str, List[str]]): Keyword(s) to search for. If a list, combines keywords with an OR condition.
        case_sensitive (bool, optional): Whether the search should be case-sensitive. Defaults to False.
        reset_index (bool, optional): Whether to reset the index of the resulting DataFrame. Defaults to False.
        dropna (bool, optional): Whether to drop rows with NA values in the 'content' column. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame containing rows where the 'content' column matches the search criteria.
    """
    out = ''
    if isinstance(keywords, list):
        keywords = '|'.join(keywords)
    if not case_sensitive:
        out = messages[
            messages["content"].str.contains(keywords, case=False)
        ]        
    out = messages[messages["content"].str.contains(keywords)]
    if reset_index or dropna:
        out = to_df(out, reset_index=reset_index)
    return out
        
def _filter_messages_by(
    messages,
    role: Optional[str] = None, 
    sender: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    content_keywords: Optional[Union[str, list]] = None,
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Filters messages in a DataFrame based on specified criteria such as role, sender, time range, and keywords.

    Args:
        messages (pd.DataFrame): The DataFrame of messages to filter.
        role (Optional[str]): The role to filter messages by (e.g., 'user', 'assistant').
        sender (Optional[str]): The sender to filter messages by.
        start_time (Optional[datetime]): The start time for filtering messages.
        end_time (Optional[datetime]): The end time for filtering messages.
        content_keywords (Optional[Union[str, list]]): Keywords to filter messages by content.
        case_sensitive (bool): Determines if the keyword search should be case-sensitive.

    Returns:
        pd.DataFrame: A DataFrame containing messages that match the filter criteria.

    Raises:
        ValueError: If an error occurs during the filtering process.
    """

    try:
        outs = messages.copy()
        
        if content_keywords:
            outs = _search_keywords(content_keywords, case_sensitive)
        
        outs = outs[outs['role'] == role] if role else outs
        outs = outs[outs['sender'] == sender] if sender else outs
        outs = outs[outs['timestamp'] > start_time] if start_time else outs
        outs = outs[outs['timestamp'] < end_time] if end_time else outs
    
        return to_df(outs)
    
    except Exception as e:
        raise ValueError(f"Error in filtering messages: {e}")

def _replace_keyword(
    df,
    keyword: str, 
    replacement: str, 
    col='content',
    case_sensitive: bool = False
) -> None:
    """
    Replaces occurrences of a keyword within a specified column of a DataFrame with a given replacement.

    Args:
        df (pd.DataFrame): The DataFrame to operate on.
        keyword (str): The keyword to search for and replace.
        replacement (str): The string to replace the keyword with.
        col (str): The column to search for the keyword in.
        case_sensitive (bool): If True, the search and replacement are case-sensitive.

    Returns:
        None: This function modifies the DataFrame in place.
    """
    if not case_sensitive:
        df[col] = df[col].str.replace(
            keyword, replacement, case=False
        )
    else:
        df[col] = df[col].str.replace(
            keyword, replacement
        )

def _remove_message(df, node_id: str) -> bool:
    """
    Removes a message from the DataFrame based on its node_id.

    Args:
        df (pd.DataFrame): The DataFrame from which the message should be removed.
        node_id (str): The node_id of the message to be removed.

    Returns:
        bool: True if the message was successfully removed, False otherwise.
    """
    initial_length = len(df)
    df = df[df["node_id"] != node_id]
    
    return len(df) < initial_length

def _update_row(
    df, node_id = None, col = "node_id", value = None
) -> bool:
    """
    Updates the value of a specified column for a row identified by node_id in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to update.
        node_id (Optional[str]): The node_id of the row to be updated.
        col (str): The column to update.
        value (Any): The new value to be assigned to the column.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    index = df.index[df[col] == node_id].tolist()
    if index:
        df.at[index[0], col] = value
        return True
    return False

def _remove_last_n_rows(df, steps: int) -> None:
    """
    Removes the last 'n' rows from a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which rows will be removed.
        steps (int): The number of rows to remove.

    Returns:
        pd.DataFrame: The DataFrame after the last 'n' rows have been removed.

    Raises:
        ValueError: If 'steps' is less than 0 or greater than the number of rows in the DataFrame.
    """
    if steps < 0 or steps > len(df):
        raise ValueError("Steps must be a non-negative integer less than or equal to the number of messages.")
    df = to_df(df[:-steps])

def get_rows(
    df, 
    sender: Optional[str] = None, 
    role: Optional[str] = None, 
    n: int = 1, 
    sign_ = False, 
    from_="front",
) -> pd.DataFrame:
    """
    Retrieves rows from a DataFrame based on specified sender, role, and quantity, optionally signing them.

    Args:
        df (pd.DataFrame): The DataFrame to retrieve rows from.
        sender (Optional[str]): The sender based on which to filter rows.
        role (Optional[str]): The role based on which to filter rows.
        n (int): The number of rows to retrieve.
        sign_ (bool): Whether to sign the retrieved rows.
        from_ (str): Direction to retrieve rows ('front' for the first rows, 'last' for the last rows).

    Returns:
        pd.DataFrame: A DataFrame containing the retrieved rows.
    """

    if from_ == "last":
        if sender is None and role is None:
            outs = df.iloc[-n:]
        elif sender and role:
            outs = df[(df['sender'] == sender) & (df['role'] == role)].iloc[-n:]
        elif sender:
            outs = df[df['sender'] == sender].iloc[-n:]
        else:
            outs = df[df['role'] == role].iloc[-n:]
            
    elif from_ == "front":
        if sender is None and role is None:
            outs = df.iloc[:n]
        elif sender and role:
            outs = df[(df['sender'] == sender) & (df['role'] == role)].iloc[:n]
        elif sender:
            outs = df[df['sender'] == sender].iloc[:n]
        else:
            outs = df[df['role'] == role].iloc[:n]

    return _sign_message(outs, sender) if sign_ else outs

def _extend(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Extends a DataFrame with another DataFrame, optionally removing duplicates based on specified criteria.

    Args:
        df1 (pd.DataFrame): The original DataFrame to be extended.
        df2 (pd.DataFrame): The DataFrame containing new rows to add to df1.
        **kwargs: Additional keyword arguments for pandas.DataFrame.drop_duplicates().

    Returns:
        pd.DataFrame: The extended DataFrame after adding rows from df2 and removing duplicates.

    Raises:
        ValueError: If an error occurs during the extension process.
    """
    validate_messages(df2)
    try:
        if len(df2.dropna(how='all')) > 0 and len(df1.dropna(how='all')) > 0:
            df = to_df([df1, df2])
            df.drop_duplicates(
                inplace=True, subset=['node_id'], keep='first', **kwargs
            )
            return to_df(df)
    except Exception as e:
        raise ValueError(f"Error in extending messages: {e}")
    