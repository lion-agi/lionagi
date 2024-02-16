from typing import Any, List, Dict, Union
import pandas as pd
from .sys_util import _SysUtil

def to_df(
    item: Any, how: str = 'all', drop_kwargs: Dict = {}, reset_index: bool = True, 
    **kwargs
) -> pd.DataFrame:
    """
    Converts a given item into a pandas DataFrame.

    This function is capable of handling a variety of inputs including lists of
    data items or pandas DataFrames. It offers options to drop rows with missing
    values based on specified criteria, and to reset the index of the resulting
    DataFrame.

    Args:
        item: The item to be converted into a DataFrame. Can be a list of items,
              a list of DataFrames, or a single DataFrame.
        how: A string indicating how to drop rows with missing values. Accepts
             the same values as pandas.DataFrame.dropna method ('any' or 'all').
        drop_kwargs: Additional keyword arguments to be passed to dropna method.
        reset_index: Whether to reset the index of the resulting DataFrame. If
                     True, the index is reset.
        **kwargs: Additional keyword arguments passed to reset_index method.

    Returns:
        A pandas DataFrame created from the input item.

    Raises:
        ValueError: If an error occurs during the conversion process.

    Examples:
        >>> df1 = pd.DataFrame({'A': [1, 2, None]})
        >>> df2 = to_df(df1, drop_kwargs={'subset': ['A']}, how='any')
        >>> print(df2)
           A
        0  1.0
        1  2.0
    """
    try:
        dfs = ''
        
        if isinstance(item, List):
            if _SysUtil.is_same_dtype(item, pd.DataFrame):
                dfs = pd.concat(item)
            dfs = pd.DataFrame(item)

        elif isinstance(item, pd.DataFrame):
            dfs = item

        drop_kwargs['how'] = how
        dfs = dfs.dropna(**drop_kwargs)
        
        if reset_index:
            drop = kwargs.pop('drop', True)
            inplace = kwargs.pop('inplace', True)
            dfs.reset_index(drop=drop, inplace=inplace, **kwargs)
            
        return dfs
    
    except Exception as e:
        raise ValueError(f'Error converting items to DataFrame: {e}')

def search_keywords(
    df,
    keywords: Union[str, list],
    col = "content",
    case_sensitive: bool = False, reset_index=False, dropna=False
):
    """
    Filters a DataFrame for rows where the specified column contains any of the
    provided keywords.

    Args:
        df: The DataFrame to search.
        keywords: A keyword or list of keywords to search for. If a list, the
                  function searches for any of the keywords.
        col: The name of the column to search for the keywords.
        case_sensitive: If False, performs a case-insensitive search. Default is
                        False.
        reset_index: If True, resets the index of the filtered DataFrame.
        dropna: If True, drops rows with NA values after filtering. This is
                handled by passing the DataFrame through `to_df`.

    Returns:
        A filtered DataFrame containing only the rows where the specified column
        contains any of the provided keywords.

    Examples:
        >>> df = pd.DataFrame({'content': ['apple', 'banana', 'Apple', 'BANANA']})
        >>> filtered_df = search_keywords(df, ['apple', 'banana'], case_sensitive=False)
        >>> print(filtered_df)
           content
        0    apple
        1   banana
        2    Apple
        3   BANANA
    """
    out = ''
    if isinstance(keywords, list):
        keywords = '|'.join(keywords)
    if not case_sensitive:
        out = df[
            df[col].str.contains(keywords, case=False)
        ]        
    out = df[df[col].str.contains(keywords)]
    if reset_index or dropna:
        out = to_df(out, reset_index=reset_index)
    return out

def replace_keyword(
    df,
    keyword: str, 
    replacement: str, 
    col='content',
    case_sensitive: bool = False
) -> None:
    """
    Replaces occurrences of a specified keyword with a replacement string in a
    specified column of a DataFrame.

    This operation is performed in place, modifying the original DataFrame.

    Args:
        df: The DataFrame to modify.
        keyword: The keyword to be replaced.
        replacement: The string to replace the keyword with.
        col: The column in which to replace the keyword.
        case_sensitive: If False, performs a case-insensitive replacement.
                        Default is False.

    Examples:
        >>> df = pd.DataFrame({'content': ['apple', 'banana', 'Apple', 'BANANA']})
        >>> replace_keyword(df, 'apple', 'fruit')
        >>> print(df)
            content
        0     fruit
        1    banana
        2     fruit
        3    BANANA
    """
    if not case_sensitive:
        df[col] = df[col].str.replace(
            keyword, replacement, case=False
        )
    else:
        df[col] = df[col].str.replace(
            keyword, replacement
        )
        
def remove_last_n_rows(df, steps: int) -> None:
    """
    Removes the last 'n' rows from a DataFrame.

    This function validates that the number of rows to be removed does not exceed
    the total number of rows in the DataFrame. The operation is performed in place.

    Args:
        df: The DataFrame from which to remove rows.
        steps: The number of rows to remove from the end of the DataFrame.

    Raises:
        ValueError: If 'steps' is negative or greater than the number of rows in
                    the DataFrame.

    Examples:
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        >>> remove_last_n_rows(df, 2)
        >>> print(df)
           A
        0  1
        1  2
        2  3
    """
    if steps < 0 or steps > len(df):
        raise ValueError("Steps must be a non-negative integer less than or equal to the length of DataFrame.")
    df = to_df(df[:-steps])

def _update_row(
    df, col = "node_id", old_value = None,  new_value = None
) -> bool:
    """
    Updates the value of a specified column for the row matching an old value with
    a new value.

    Args:
        df: The DataFrame to update.
        col: The column in which to search for the old value.
        old_value: The value to be replaced.
        new_value: The new value to replace the old value with.

    Returns:
        bool: True if the update was successful, False otherwise.

    Examples:
        >>> df = pd.DataFrame({'node_id': [1, 2, 3], 'value': ['a', 'b', 'c']})
        >>> success = _update_row(df, 'node_id', 2, 4)
        >>> print(df)
           node_id value
        0        1     a
        1        4     b
        2        3     c
        >>> print(success)
        True
    """
    index = df.index[df[col] == old_value].tolist()
    if index:
        df.at[index[0], col] = new_value
        return True
    return False
