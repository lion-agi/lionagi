import pandas as pd
import json
from datetime import datetime
from typing import Union, Optional, Any

from pandas import DataFrame

from ..utils import strip_lower, to_dict, NestedStructUtil, to_df


class MessageUtil:

    @staticmethod
    def validate_messages(messages):
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
    def sign_message(messages, sender: str):
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
    def filter_messages_by(
            messages,
            role: Optional[str] = None,
            sender: Optional[str] = None,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            content_keywords: Optional[Union[str, list]] = None,
            case_sensitive: bool = False
    ) -> pd.DataFrame:

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
    def remove_message(messages, node_id: str) -> bool:
        initial_length = len(messages)
        messages = messages[messages["node_id"] != node_id]

        return len(messages) < initial_length

    @staticmethod
    def get_message_rows(
            messages,
            sender: Optional[str] = None,
            role: Optional[str] = None,
            n: int = 1,
            sign_=False,
            from_="front",
    ) -> pd.DataFrame:

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
    def extend(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
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
    def to_markdown_string(messages):
        answers = []
        for _, i in messages.iterrows():
            content = to_dict(i.content)

            if i.role == "assistant":
                try:
                    a = NestedStructUtil.nget(content, ['action_response', 'func'])
                    b = NestedStructUtil.nget(content, ['action_response', 'arguments'])
                    c = NestedStructUtil.nget(content, ['action_response', 'output'])
                    if a is not None:
                        answers.append(f"Function: {a}")
                        answers.append(f"Arguments: {b}")
                        answers.append(f"Output: {c}")
                    else:
                        answers.append(NestedStructUtil.nget(content, ['response']))
                except:
                    pass
            elif i.role == "user":
                try:
                    answers.append(NestedStructUtil.nget(content, ['instruction']))
                except:
                    pass
            else:
                try:
                    answers.append(NestedStructUtil.nget(content, ['system_info']))
                except:
                    pass

        out_ = "\n".join(answers)
        return out_


def search_keywords(
        df: DataFrame,
        keywords: str | list[str],
        col: str = "content",
        case_sensitive: bool = False,
        reset_index: bool = False,
        dropna: bool = False
) -> DataFrame:
    """
    Filters a DataFrame for rows where the specified column contains any of the
    provided keywords.

    This function performs a search within a specified column of a DataFrame, looking
    for rows that contain any of the keywords provided. The search can be
    case-sensitive or case-insensitive. Additionally, it offers the option to reset the
    index of the filtered DataFrame and/or drop rows with NA values post-filtering.

    Args: df: The DataFrame to search. keywords: A single keyword or a list of keywords
    to search for. If providing a list, the function searches for any of the keywords
    within the specified column. col: The name of the column to search. Defaults to
    "content". case_sensitive: If True, performs a case-sensitive search; otherwise,
    the search is case-insensitive. Defaults to False. reset_index: If True, reset the
    index of the filtered DataFrame. Defaults to False. dropna: If True, drop rows
    with NA values in the filtered DataFrame. Defaults to False.

    Returns: A filtered DataFrame containing only the rows where the specified column
    contains any of the provided keywords.

    Examples:
        >>> df_ = pd.DataFrame({'content': ['apple', 'banana', 'Apple', 'BANANA']})
        >>> filtered_df = search_keywords(df_, ['apple', 'banana'], case_sensitive=False)
        >>> print(filtered_df)
           content
        0    apple
        1   banana
        2    Apple
        3   BANANA
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
