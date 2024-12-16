# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Literal

import pandas as pd

from lionagi.integrations.pandas_.to_df import to_df


def extend_dataframe(
    dataframes: list[pd.DataFrame],
    unique_col: str = "node_id",
    keep: Literal["first", "last", False] = "first",
    ignore_index: bool = False,
    sort: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Merges multiple DataFrames while ensuring no duplicate entries based on a specified unique column.

    Args:
        dataframes: List of DataFrames to merge, with the first being the primary DataFrame.
        unique_col: The column name to check for duplicate entries. Defaults to 'node_id'.
        keep: Determines which duplicates to keep. 'first' keeps the first occurrence,
              'last' keeps the last occurrence, and False drops all duplicates.
        ignore_index: If True, the resulting axis will be labeled 0, 1, …, n - 1.
        sort: If True, sort the join keys lexicographically in the result DataFrame.
        **kwargs: Additional keyword arguments for `drop_duplicates`.

    Returns:
        A DataFrame combined from all input DataFrames with duplicates removed based on the unique column.

    Raises:
        ValueError: If all DataFrames are empty or if there's an error in extending.

    Example:
        >>> df1 = pd.DataFrame({'node_id': [1, 2], 'value': ['a', 'b']})
        >>> df2 = pd.DataFrame({'node_id': [2, 3], 'value': ['c', 'd']})
        >>> extend_dataframe([df1, df2], keep='last', ignore_index=True)
           node_id value
        0       1     a
        1       2     c
        2       3     d
    """
    try:
        if all(df.empty for df in dataframes):
            raise ValueError("All input DataFrames are empty.")

        combined = pd.concat(dataframes, ignore_index=ignore_index, sort=sort)
        result = combined.drop_duplicates(
            subset=[unique_col], keep=keep, **kwargs
        )

        if result.empty:
            raise ValueError("No data left after removing duplicates.")

        return to_df(result)

    except Exception as e:
        raise ValueError(f"Error in extending DataFrames: {e}") from e
