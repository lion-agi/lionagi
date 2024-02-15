import pandas as pd
import json
from datetime import datetime
from typing import Union, Optional

from .sys_util import strip_lower, to_df, as_dict
from .nested_util import nget


class CoreUtil:

    @staticmethod
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

    @staticmethod
    def sign_message(messages, sender: str):
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

    @staticmethod
    def search_keywords(
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
                outs = CoreUtil.search_keywords(content_keywords, case_sensitive)
            
            outs = outs[outs['role'] == role] if role else outs
            outs = outs[outs['sender'] == sender] if sender else outs
            outs = outs[outs['timestamp'] > start_time] if start_time else outs
            outs = outs[outs['timestamp'] < end_time] if end_time else outs
        
            return to_df(outs)
        
        except Exception as e:
            raise ValueError(f"Error in filtering messages: {e}")

    @staticmethod
    def replace_keyword(
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

    @staticmethod
    def remove_message(df, node_id: str) -> bool:
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

    @staticmethod
    def update_row(
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

    @staticmethod
    def remove_last_n_rows(df, steps: int) -> None:
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

    @staticmethod
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

        return CoreUtil.sign_message(outs, sender) if sign_ else outs

    @staticmethod
    def extend(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs) -> pd.DataFrame:
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
        CoreUtil.validate_messages(df2)
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
    def to_markdown_string(df):
        answers = []
        for _, i in df.iterrows():
            content = as_dict(i.content)
            
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
