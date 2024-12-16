import pandas as pd

from .to_df import to_df


def remove_rows(
    df: pd.DataFrame,
    rows: int | slice | list[int],
    from_end: bool = False,
    reset_index: bool = False,
) -> pd.DataFrame:
    """
    Removes specified rows from a DataFrame.

    Args:
        df: The DataFrame from which to remove rows.
        rows: The row(s) to remove. Can be an integer, slice, or list of integers.
        from_end: If True, count rows from the end of the DataFrame.
        reset_index: If True, reset the index after removing rows.

    Returns:
        A DataFrame with the specified rows removed.

    Raises:
        ValueError: If the specified rows are invalid.

    Example:
        >>> df = pd.DataFrame({'A': range(10)})
        >>> remove_rows(df, [0, 2, 4], reset_index=True)
           A
        0  1
        1  3
        2  5
        3  6
        4  7
        5  8
        6  9
    """
    if df.empty:
        return df.copy()

    if isinstance(rows, int):
        rows = [rows]
    elif isinstance(rows, slice):
        rows = list(range(*rows.indices(len(df))))

    if from_end:
        rows = [len(df) - 1 - r for r in rows]

    try:
        result = df.drop(df.index[rows])
    except IndexError as e:
        raise ValueError(f"Invalid row selection: {e}") from e

    if reset_index:
        result = result.reset_index(drop=True)

    return to_df(result)
