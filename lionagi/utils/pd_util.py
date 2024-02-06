from typing import List, Dict
import pandas as pd
from ..schema.data_node import DataNode
from .sys_util import timestamp_to_datetime

def to_pd_df(items: List[Dict], how: str = 'all') -> pd.DataFrame:
    """
    Converts a list of dictionaries to a pandas DataFrame, dropping NA values.

    Args:
        items (List[Dict]): A list of dictionaries to be converted to a DataFrame.
        how (str): How to handle NA values. Options are 'all' to drop rows with all NA values,
                   'any' to drop rows with any NA values, or 'none' to keep all rows.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the input list of dictionaries.
    """
    df = pd.DataFrame(items).dropna(how=how)
    df.reset_index(drop=True, inplace=True)
    return df

def pd_row_to_node(row: pd.Series):
    """
    Converts a pandas Series row to a DataNode object with structured data.

    Args:
        row (pd.Series): A pandas Series containing row data to be converted.

    Returns:
        DataNode: A DataNode object containing structured data from the input pandas Series.
    """
    dict_ = row.to_dict()
    dict_['datetime'] = str(timestamp_to_datetime(dict_['datetime']))
    dict_['content'] = {'headline': dict_.pop('headline'), 'summary': dict_.pop('summary')}
    dict_['metadata'] = {'datetime': dict_.pop('datetime'), 'url': dict_.pop('url'), 'id': dict_.pop('id')}
    return DataNode.from_dict(dict_)

def expand_df_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expands a pandas DataFrame with a datetime column into separate year, month, and day columns.

    Args:
        df (pd.DataFrame): The pandas DataFrame containing a 'datetime' column to be expanded.

    Returns:
        pd.DataFrame: A pandas DataFrame with 'year', 'month', and 'day' columns.
    """
    df_expanded = df.copy()
    if df_expanded['datetime'].dtype == int:
        df_expanded['datetime'] = df_expanded['datetime'].apply(lambda x: timestamp_to_datetime(x))

    df_expanded.insert(0, 'year', df_expanded['datetime'].dt.year)
    df_expanded.insert(1, 'month', df_expanded['datetime'].dt.month)
    df_expanded.insert(2, 'day', df_expanded['datetime'].dt.day)
    df_expanded.drop('datetime', axis=1, inplace=True)

    return df_expanded
