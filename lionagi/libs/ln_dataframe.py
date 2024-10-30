from typing import Any

import pandas as pd

from lionagi.libs import ln_convert as convert

ln_DataFrame = pd.DataFrame
ln_Series = pd.Series


def extend_dataframe(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    /,
    unique_col: str = "node_id",
    keep="first",
    **kwargs,
) -> pd.DataFrame:
    """
    Merges two DataFrames while ensuring no duplicate entries based on a specified unique column.

    Args:
            df1: The primary DataFrame.
            df2: The DataFrame to merge with the primary DataFrame.
            unique_col: The column name to check for duplicate entries. Defaults to 'node_id'.
            **kwargs: Additional keyword arguments for `drop_duplicates`.

    Returns:
            A DataFrame combined from df1 and df2 with duplicates removed based on the unique column.
    """
    try:
        if len(df2.dropna(how="all")) > 0 and len(df1.dropna(how="all")) > 0:
            df = convert.to_df([df1, df2])
            df.drop_duplicates(
                inplace=True, subset=[unique_col], keep=keep, **kwargs
            )
            df_ = convert.to_df(df)
            if len(df_) > 1:
                return df_
            else:
                raise ValueError("No data to extend")

    except Exception as e:
        raise ValueError(f"Error in extending messages: {e}") from e


def search_keywords(
    df: pd.DataFrame,
    /,
    keywords: str | list[str],
    *,
    column: str = "content",
    case_sensitive: bool = False,
    reset_index: bool = False,
    dropna: bool = False,
) -> pd.DataFrame:
    """
    Filters a DataFrame for rows where a specified column contains given keywords.

    Args:
            df: The DataFrame to search through.
            keywords: A keyword or list of keywords to search for.
            col: The column to perform the search in. Defaults to "content".
            case_sensitive: Whether the search should be case-sensitive. Defaults to False.
            reset_index: Whether to reset the DataFrame's index after filtering. Defaults to False.
            dropna: Whether to drop rows with NA values before searching. Defaults to False.

    Returns:
            A filtered DataFrame containing only rows where the specified column contains
            any of the provided keywords.
    """

    if isinstance(keywords, list):
        keywords = "|".join(keywords)

    def handle_cases():
        if not case_sensitive:
            return df[df[column].str.contains(keywords, case=False)]
        else:
            return df[df[column].str.contains(keywords)]

    out = handle_cases()
    if reset_index or dropna:
        out = convert.to_df(out, reset_index=reset_index)

    return out


def replace_keyword(
    df: pd.DataFrame,
    /,
    keyword: str,
    replacement: str,
    *,
    inplace=True,
    column: str = "content",
    case_sensitive: bool = False,
) -> pd.DataFrame | bool:
    """
    Replaces occurrences of a specified keyword with a replacement string in a DataFrame column.

    Args:
            df: The DataFrame to modify.
            keyword: The keyword to be replaced.
            replacement: The string to replace the keyword with.
            col: The column in which to perform the replacement.
            case_sensitive: If True, performs a case-sensitive replacement. Defaults to False.
    """

    df_ = df.copy(deep=False) if inplace else df.copy()

    if not case_sensitive:
        df_.loc[:, column] = df_[column].str.replace(
            keyword, replacement, case=False, regex=False
        )
    else:
        df_.loc[:, column] = df_[column].str.replace(
            keyword, replacement, regex=False
        )

    return df_ if inplace else True


def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame with optional additional pandas read_csv parameters.

    Args:
            filepath: The path to the CSV file to read.
            **kwargs: Additional keyword arguments to pass to pandas.read_csv function.

    Returns:
            A DataFrame containing the data read from the CSV file.
    """
    df = pd.read_csv(filepath, **kwargs)
    return convert.to_df(df)


def read_json(filepath, **kwargs):
    df = pd.read_json(filepath, **kwargs)
    return convert.to_df(df)


def remove_last_n_rows(df: pd.DataFrame, steps: int) -> pd.DataFrame:
    """
    Removes the last 'n' rows from a DataFrame.

    Args:
            df: The DataFrame from which to remove rows.
            steps: The number of rows to remove from the end of the DataFrame.

    Returns:
            A DataFrame with the last 'n' rows removed.

    Raises:
            ValueError: If 'steps' is negative or greater than the number of rows in the DataFrame.
    """

    if steps < 0 or steps > len(df):
        raise ValueError(
            "'steps' must be a non-negative integer less than or equal to "
            "the length of DataFrame."
        )
    return convert.to_df(df[:-steps])


def update_row(
    df: pd.DataFrame, row: str | int, column: str | int, value: Any
) -> bool:
    """
    Updates a row's value for a specified column in a DataFrame.

    Args:
            df: The DataFrame to update.
            col: The column whose value is to be updated.
            old_value: The current value to search for in the specified column.
            new_value: The new value to replace the old value with.

    Returns:
            True if the update was successful, False otherwise.
    """

    try:
        df.loc[row, column] = value
        return True
    except Exception:
        return False
