import pandas as pd

from .to_df import to_df


def search_dataframe_keywords(
    df: pd.DataFrame,
    keywords: str | list[str],
    *,
    column: str | list[str] = "content",
    case_sensitive: bool = False,
    reset_index: bool = False,
    dropna: bool = False,
    regex: bool = False,
    match_all: bool = False,
) -> pd.DataFrame:
    """
    Filters a DataFrame for rows where specified column(s) contain given keywords.

    Args:
        df: The DataFrame to search through.
        keywords: A keyword or list of keywords to search for.
        column: The column(s) to perform the search in. Can be a string or list of strings.
        case_sensitive: Whether the search should be case-sensitive.
        reset_index: Whether to reset the DataFrame's index after filtering.
        dropna: Whether to drop rows with NA values before searching.
        regex: If True, treat keywords as regular expressions.
        match_all: If True, all keywords must be present for a match.

    Returns:
        A filtered DataFrame containing only rows where the specified column(s) contain
        any (or all) of the provided keywords.

    Example:
        >>> df = pd.DataFrame({'content': ['apple pie', 'banana split', 'cherry pie']})
        >>> search_keywords(df, ['pie', 'cherry'], match_all=True)
           content
        2  cherry pie
    """
    if dropna:
        df = df.dropna(subset=[column] if isinstance(column, str) else column)

    if isinstance(keywords, str):
        keywords = [keywords]

    if isinstance(column, str):
        column = [column]

    mask = pd.DataFrame(index=df.index)
    for col in column:
        col_mask = pd.Series(False, index=df.index)
        for keyword in keywords:
            keyword_mask = df[col].str.contains(
                keyword, case=case_sensitive, regex=regex, na=False
            )
            col_mask = col_mask | keyword_mask
        mask[col] = col_mask

    final_mask = mask.all(axis=1) if match_all else mask.any(axis=1)

    result = df[final_mask]

    if reset_index:
        result = result.reset_index(drop=True)

    return to_df(result)
