import pandas as pd

from .to_df import to_df


def replace_keywords(
    df: pd.DataFrame,
    keyword: str | dict[str, str],
    replacement: str | None = None,
    *,
    column: str | list[str] = "content",
    case_sensitive: bool = False,
    regex: bool = False,
    inplace: bool = False,
) -> pd.DataFrame | None:
    """
    Replaces occurrences of specified keyword(s) with replacement string(s) in DataFrame column(s).

    Args:
        df: The DataFrame to modify.
        keyword: The keyword to be replaced. Can be a string or a dictionary of {old: new} pairs.
        replacement: The string to replace the keyword with. Ignored if keyword is a dict.
        column: The column(s) in which to perform the replacement. Can be a string or list of strings.
        case_sensitive: If True, performs a case-sensitive replacement.
        regex: If True, treat keyword(s) as regular expressions.
        inplace: If True, modifies the DataFrame in place and returns None.

    Returns:
        Modified DataFrame if inplace is False, None otherwise.

    Example:
        >>> df = pd.DataFrame({'content': ['apple pie', 'banana split', 'cherry pie']})
        >>> replace_keyword(df, {'pie': 'tart', 'split': 'smoothie'}, column='content')
           content
        0  apple tart
        1  banana smoothie
        2  cherry tart
    """
    df_ = df if inplace else df.copy()

    if isinstance(column, str):
        column = [column]

    if isinstance(keyword, dict):
        for col in column:
            df_[col] = df_[col].replace(
                to_replace=keyword,
                regex=regex,
                case=case_sensitive,
            )
    else:
        for col in column:
            df_[col] = df_[col].replace(
                to_replace=keyword,
                value=replacement,
                regex=regex,
                case=case_sensitive,
            )

    if inplace:
        return None
    return to_df(df_)
