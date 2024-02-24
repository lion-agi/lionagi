import pandas as pd
import json
from datetime import datetime
from typing import Union, Optional, Any, List

from pandas import DataFrame

from lionagi.util import strip_lower, to_dict, to_df, nget


class MessageUtil:

    @staticmethod
    def validate_messages(messages: DataFrame) -> bool:
        """
        Validates the structure and content of a DataFrame containing messages.

        Ensures that the DataFrame follows the expected schema with specific columns and checks
        for null values and the validity of message roles. Additionally, it validates that the
        'content' column contains valid JSON strings.

        Args:
            messages: The DataFrame containing messages to be validated.

        Returns:
            True if the DataFrame passes all validation checks, indicating it is properly formatted.

        Raises:
            ValueError: If the DataFrame does not match the expected schema, contains null values,
                        includes invalid roles, or has non-JSON strings in the 'content' column.

        Examples:
            >>> valid_messages = pd.DataFrame([...])
            >>> MessageUtil.validate_messages(valid_messages)
            True
        """

        if list(messages.columns) != ['node_id', 'role', 'sender', 'timestamp',
                                      'content']:
            raise ValueError('Invalid messages dataframe. Unmatched columns.')
        if messages.isnull().values.any():
            raise ValueError('Invalid messages dataframe. Cannot have null.')
        if not all(role in ['system', 'user', 'assistant'] for role in
                   messages['role'].unique()):
            raise ValueError(
                'Invalid messages dataframe. Cannot have role other than ["system", "user", "assistant"].')
        for cont in messages['content']:
            if cont.startswith('Sender'):
                cont = cont.split(':', 1)[1]
            try:
                json.loads(cont)
            except:
                raise ValueError(
                    'Invalid messages dataframe. Content expect json string.')
        return True

    @staticmethod
    def sign_message(messages: DataFrame, sender: str) -> DataFrame:
        """
        Prefixes each message in a DataFrame with the sender's identifier.

        This method modifies the 'content' column of each message to include "Sender [sender]:"
        at the beginning, effectively signing or marking each message with its origin.

        Args:
            messages: The DataFrame containing messages to be signed.
            sender: The identifier of the sender to be prefixed to each message.

        Returns:
            A new DataFrame with the messages signed by the specified sender.

        Raises:
            ValueError: If the sender is None or explicitly set to 'none'.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> signed_messages = MessageUtil.sign_message(messages, "assistant")
        """

        if sender is None or strip_lower(sender) == 'none':
            raise ValueError("sender cannot be None")
        df = to_df(messages)

        for i in df.index:
            if not df.loc[i, 'content'].startswith('Sender'):
                df.loc[i, 'content'] = f"Sender {sender}: {df.loc[i, 'content']}"
            else:
                content = df.loc[i, 'content'].split(':', 1)[1]
                df.loc[i, 'content'] = f"Sender {sender}: {content}"

        return to_df(df)

    @staticmethod
    def filter_messages_by(messages: DataFrame, role: Optional[str] = None,
                           sender: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           content_keywords: Optional[Union[str, List[str]]] = None,
                           case_sensitive: bool = False) -> DataFrame:
        """
        Filters messages in a DataFrame based on specified criteria such as role, sender, time range, and content keywords.

        This method allows for selective viewing of messages that match certain conditions,
        aiding in analysis or processing of conversation data.

        Args:
            messages: The DataFrame containing messages to be filtered.
            role: Optional; Filters messages to those matching the specified role.
            sender: Optional; Filters messages to those sent by the specified sender.
            start_time: Optional; Filters messages sent after this datetime.
            end_time: Optional; Filters messages sent before this datetime.
            content_keywords: Optional; Filters messages containing specified keywords in their content.
            case_sensitive: If True, makes the keyword search case-sensitive.

        Returns:
            A DataFrame containing messages that meet the specified criteria.

        Raises:
            ValueError: If an error occurs during the filtering process.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> filtered = MessageUtil.filter_messages_by(messages, role="user", content_keywords="help")
        """

        try:
            outs = messages.copy()

            if content_keywords:
                outs = search_keywords(content_keywords, case_sensitive)

            outs = outs[outs['role'] == role] if role else outs
            outs = outs[outs['sender'] == sender] if sender else outs
            outs = outs[outs['timestamp'] > start_time] if start_time else outs
            outs = outs[outs['timestamp'] < end_time] if end_time else outs

            return to_df(outs)

        except Exception as e:
            raise ValueError(f"Error in filtering messages: {e}")

    @staticmethod
    def remove_message(messages: DataFrame, node_id: str) -> bool:
        """
        Removes a message from a DataFrame based on its node ID.

        This method finds and deletes a message by its unique identifier, modifying the
        original DataFrame in place.

        Args:
            messages: The DataFrame containing messages.
            node_id: The unique identifier of the message to be removed.

        Returns:
            True if a message was found and removed, False if the message was not found.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> success = MessageUtil.remove_message(messages, "node_id_123")
            >>> print(success)
        """

        initial_length = len(messages)
        messages = messages[messages["node_id"] != node_id]

        return len(messages) < initial_length

    @staticmethod
    def get_message_rows(messages: DataFrame, sender: Optional[str] = None,
                         role: Optional[str] = None, n: int = 1, sign_: bool = False,
                         from_: str = "front") -> DataFrame:
        """
        Retrieves a specified number of message rows from a DataFrame based on sender, role, and order.

        This method allows for the selective retrieval of messages, optionally signing them with
        the sender's identifier. Messages can be fetched from the start ('front') or end ('last') of
        the DataFrame.

        Args:
            messages: The DataFrame containing messages.
            sender: Optional; Filters messages to those sent by the specified sender.
            role: Optional; Filters messages to those matching the specified role.
            n: The number of messages to retrieve. Defaults to 1.
            sign_: If True, prefixes the 'content' of each message with "Sender [sender]:".
            from_: Specifies whether to retrieve messages from the start ('front') or end ('last').

        Returns:
            A DataFrame containing the retrieved messages, optionally signed.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> last_message = MessageUtil.get_message_rows(messages, role="user", n=1, from_branch="last")
        """

        outs = ''

        if from_ == "last":
            if sender is None and role is None:
                outs = messages.iloc[-n:]
            elif sender and role:
                outs = messages[
                           (messages['sender'] == sender) & (messages['role'] == role)
                           ].iloc[-n:]

            elif sender:
                outs = messages[messages['sender'] == sender].iloc[-n:]
            else:
                outs = messages[messages['role'] == role].iloc[-n:]

        elif from_ == "front":
            if sender is None and role is None:
                outs = messages.iloc[:n]
            elif sender and role:
                outs = messages[(messages['sender'] == sender) & (
                        messages['role'] == role)].iloc[:n]
            elif sender:
                outs = messages[messages['sender'] == sender].iloc[:n]
            else:
                outs = messages[messages['role'] == role].iloc[:n]

        return MessageUtil.sign_message(outs, sender) if sign_ else outs

    @staticmethod
    def extend(df1: DataFrame, df2: DataFrame, **kwargs) -> DataFrame:
        """
        Combines two DataFrames of messages, ensuring no duplicate messages based on 'node_id'.

        This method extends the first DataFrame with messages from the second DataFrame,
        applying a filter to avoid duplicates. It's useful for aggregating messages from
        multiple sources or time frames into a single DataFrame.

        Args:
            df1: The primary DataFrame to which messages will be added.
            df2: The DataFrame containing messages to be merged with the first.
            **kwargs: Additional keyword arguments for `drop_duplicates` method, such as
                      `keep` which determines which duplicates (if any) to keep.

        Returns:
            A new DataFrame containing the combined set of messages from both input DataFrames,
            with duplicates removed based on 'node_id'.

        Raises:
            ValueError: If an error occurs during the message extension process.

        Examples:
            >>> df_main = pd.DataFrame([...])
            >>> df_new = pd.DataFrame([...])
            >>> combined_df = MessageUtil.extend(df_main, df_new, keep='first')
        """

        MessageUtil.validate_messages(df2)
        try:
            if len(df2.dropna(how='all')) > 0 and len(df1.dropna(how='all')) > 0:
                df = to_df([df1, df2])
                df.drop_duplicates(
                    inplace=True, subset=['node_id'], keep='first', **kwargs
                )
                return to_df(df)
        except Exception as e:
            raise ValueError(f"Error in extending messages: {e}")

    @staticmethod
    def to_markdown_string(messages: DataFrame) -> str:
        """
        Converts messages in a DataFrame to a Markdown-formatted string.

        This method is designed for rendering message content in a Markdown-friendly format,
        facilitating easy visualization or reporting of conversations. It processes different
        message roles (assistant, user, system) to format their content appropriately.

        Args:
            messages: The DataFrame containing messages to be converted.

        Returns:
            A string with the content of messages formatted in Markdown. Each message is
            rendered according to its role, with special handling for 'action_response'
            to extract function calls, arguments, and outputs.

        Examples:
            >>> messages = pd.DataFrame([...])
            >>> markdown_str = MessageUtil.to_markdown_string(messages)
            >>> print(markdown_str)
        """

        answers = []
        for _, i in messages.iterrows():
            content = to_dict(i.content)

            if i.role == "assistant":
                try:
                    a = nget(content, ['action_response', 'func'])
                    b = nget(content, ['action_response', 'arguments'])
                    c = nget(content, ['action_response', 'output'])
                    if a is not None:
                        answers.append(f"Function: {a}")
                        answers.append(f"Arguments: {b}")
                        answers.append(f"Output: {c}")
                    else:
                        answers.append(nget(content, ['response']))
                except:
                    pass
            elif i.role == "user":
                try:
                    answers.append(nget(content, ['instruction']))
                except:
                    pass
            else:
                try:
                    answers.append(nget(content, ['system_info']))
                except:
                    pass

        out_ = "\n".join(answers)
        return out_


    @staticmethod
    def search_keywords(df: DataFrame, keywords: Union[str, List[str]], col: str = "content",
                        case_sensitive: bool = False, reset_index: bool = False,
                        dropna: bool = False) -> DataFrame:
        """
        Searches for keywords in a specified column of a DataFrame and returns matching rows.

        This function filters the DataFrame based on the presence of specified keywords in
        a given column. It supports case-sensitive/insensitive searches and allows for
        additional post-search processing like index resetting and NA dropping.

        Args:
            df: The DataFrame to search through.
            keywords: A keyword or list of keywords to search for within the specified column.
            col: The column in which to perform the search. Defaults to "content".
            case_sensitive: If True, the search is case-sensitive. Defaults to False.
            reset_index: If True, resets the index of the resulting DataFrame. Defaults to False.
            dropna: If True, drops rows with NA values in the specified column before searching. Defaults to False.

        Returns:
            A DataFrame containing only the rows where the specified column contains any of the provided keywords.

        Examples:
            >>> df = pd.DataFrame([...])
            >>> filtered_df = MessageUtil.search_keywords(df, ['urgent', 'immediate'], case_sensitive=True)
        """
        if isinstance(keywords, list):
            keywords = '|'.join(keywords)

        def handle_cases():
            if not case_sensitive:
                return df[df[col].str.contains(keywords, case=False)]
            else:
                return df[df[col].str.contains(keywords)]

        out = handle_cases()
        if reset_index or dropna:
            out = to_df(out, reset_index=reset_index)

        return out

    @staticmethod
    def replace_keyword(
            df: DataFrame,
            keyword: str,
            replacement: str,
            col: str = 'content',
            case_sensitive: bool = False
    ) -> None:
        """
        Replaces occurrences of a specified keyword with a replacement string in a
        specified column of a DataFrame.

        This function performs an in-place modification of the DataFrame, replacing all
        instances of the specified keyword within the given column with a replacement
        string. The operation can be performed in a case-sensitive or case-insensitive
        manner, depending on the `case_sensitive` parameter.

        Args: df: The DataFrame to modify. keyword: The keyword to be replaced.
        replacement: The string to replace the keyword with. col: The column in which to
        replace the keyword. Defaults to 'content'. case_sensitive: Determines whether the
        replacement should be case-sensitive. Defaults to False.

        Examples:
            >>> df_ = pd.DataFrame({'content': ['apple', 'banana', 'Apple', 'BANANA']})
            >>> replace_keyword(df_, 'apple', 'fruit', case_sensitive=False)
            >>> print(df)
                 content
            0     fruit
            1    banana
            2     fruit
            3    BANANA

            Perform a case-sensitive replacement:
            >>> replace_keyword(df_, 'BANANA', 'berry', case_sensitive=True)
            >>> print(df_)
                 content
            0     fruit
            1    banana
            2     fruit
            3     berry

        """

        if not case_sensitive:
            df[col] = df[col].str.replace(keyword, replacement, case=False, regex=False)
        else:
            df[col] = df[col].str.replace(keyword, replacement, regex=False)

    @staticmethod
    def read_csv(filepath, **kwargs):
        df = pd.read_csv(filepath, **kwargs)
        return to_df(df)

    @staticmethod
    def read_json(filepath, **kwargs):
        df = pd.read_json(filepath, **kwargs)
        return to_df(df)


def remove_last_n_rows(df: DataFrame, steps: int) -> DataFrame:
    """
    Removes the last 'num' rows from a DataFrame and returns the modified DataFrame.

    This function takes a DataFrame and an integer 'steps', removing the last 'steps'
    rows from the DataFrame. It validates that 'steps' is a non-negative integer that does
    not exceed the total number of rows in the DataFrame. The operation does not modify
    the original DataFrame but returns a new DataFrame with the specified rows removed.

    Args: df: The DataFrame from which to remove rows. steps: The number of rows to
    remove from the end of the DataFrame. It Must be a non-negative integer and not
    greater than the number of rows in the DataFrame.

    Returns:
        DataFrame: A new DataFrame with the last 'steps' rows removed.

    Raises: ValueError: If 'steps' is negative or greater than the number of rows in
    the DataFrame.

    Examples:
        >>> df_ = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        >>> modified_df = remove_last_n_rows(df_, 2)
        >>> print(modified_df)
           A
        0  1
        1  2
        2  3

        Attempting to remove more rows than the DataFrame contains: >>>
        remove_last_n_rows(df, 6) ValueError: 'steps' must be a non-negative integer
        less than or equal to the length of DataFrame.
    """
    if steps < 0 or steps > len(df):
        raise ValueError(
            "'steps' must be a non-negative integer less than or equal to "
            "the length of DataFrame.")
    return to_df(df[:-steps])


def _update_row(
        df: DataFrame,
        col: str,
        old_value: Any,
        new_value: Any
) -> bool:
    """
    Updates the value of a specified column for the row matching an old value with a
    new value.

    This function searches the DataFrame for a row where the specified column matches
    'old_value'. If such a row is found, the function updates that row's column to
    'new_value'. The operation is performed in-place, modifying the original DataFrame.
    It returns True if the update was successful, or False if no matching row was found.

    Args:
        df: The DataFrame to update.
        col: The column to search for 'old_value' and in which to update 'new_value'.
        old_value: The value to be replaced in the 'col' column.
        new_value: The new value to replace 'old_value' in the 'col' column.

    Returns:
        bool: True if the update was successful, False otherwise.

    Examples:
        >>> df_ = pd.DataFrame({'node_id': [1, 2, 3], 'value': ['a', 'b', 'c']})
        >>> success = _update_row(df_, 'node_id', 2, 4)
        >>> print(success)
        True
        >>> print(df_)
           node_id value
        0        1     a
        1        4     b
        2        3     c

        Attempting to update a non-existing value:
        >>> success = _update_row(df, 'node_id', 5, 6)
        >>> print(success)
        False
    """
    index = df.index[df[col] == old_value].tolist()
    if index:
        df.at[index[0], col] = new_value
        return True
    return False
