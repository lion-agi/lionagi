from typing import Any

import pandas as pd

from .to_df import to_df


def update_cells(
    df: pd.DataFrame,
    updates: dict[tuple[int | str, int | str], Any],
    create_missing: bool = False,
) -> pd.DataFrame:
    """
    Updates multiple cells in a DataFrame based on a dictionary of updates.

    Args:
        df: The DataFrame to update.
        updates: A dictionary where keys are (row, column) tuples and values are the new values.
                 Rows and columns can be specified by integer position or label.
        create_missing: If True, create new columns if they don't exist.

    Returns:
        The updated DataFrame.

    Raises:
        KeyError: If a specified row or column doesn't exist and create_missing is False.

    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> updates = {(0, 'A'): 10, (1, 'B'): 40, (0, 'C'): 100}
        >>> update_cells(df, updates, create_missing=True)
            A   B    C
        0  10   3  100
        1   2  40  NaN
    """
    df_copy = df.copy()

    for (row, col), value in updates.items():
        try:
            if isinstance(col, str) and col not in df_copy.columns:
                if create_missing:
                    df_copy[col] = None
                else:
                    raise KeyError(f"Column '{col}' does not exist.")

            df_copy.loc[row, col] = value
        except KeyError as e:
            if not create_missing:
                raise KeyError(f"Invalid row or column: {e}") from e

    return to_df(df_copy)
