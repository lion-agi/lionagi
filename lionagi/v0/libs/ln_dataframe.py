from typing import Any


def extend_dataframe(
    df1,
    df2,
    /,
    unique_col: str = "node_id",
    keep="first",
    **kwargs,
):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.extend_dataframe(
        df1,
        df2,
        unique_col=unique_col,
        keep=keep,
        **kwargs,
    )


def search_keywords(
    df,
    /,
    keywords: str | list[str],
    *,
    column: str = "content",
    case_sensitive: bool = False,
    reset_index: bool = False,
    dropna: bool = False,
):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.search_keywords(
        df,
        keywords=keywords,
        column=column,
        case_sensitive=case_sensitive,
        reset_index=reset_index,
        dropna=dropna,
    )


def replace_keyword(
    df,
    /,
    keyword: str,
    replacement: str,
    *,
    inplace=True,
    column: str = "content",
    case_sensitive: bool = False,
):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.replace_keyword(
        df,
        keyword=keyword,
        replacement=replacement,
        inplace=inplace,
        column=column,
        case_sensitive=case_sensitive,
    )


def read_csv(filepath: str, **kwargs):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.read_csv(filepath, **kwargs)


def read_json(filepath, **kwargs):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.read_json(filepath, **kwargs)


def remove_last_n_rows(df, steps: int):
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.remove_last_n_rows(df, steps)


def update_row(df, row: str | int, column: str | int, value: Any) -> bool:
    from lionagi.app.Pandas.utils import PandasUtil

    return PandasUtil.update_row(df, row, column, value)
