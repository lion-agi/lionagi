"""
Module for converting various input types to pandas DataFrames.

Provides functions to convert a variety of data structures into pandas
DataFrames, with options for handling missing data, resetting the index,
and custom behavior for specific input types.

Functions:
    to_df: Converts various input types to a pandas DataFrame, with options for
           handling missing data and resetting the index.
    _ (list overload): Specialized behavior for converting a list of data to
                       a DataFrame.
"""

from functools import singledispatch
from pandas import DataFrame, Series, concat, read_csv
from pandas.core.generic import NDFrame
from typing import Any, Dict
from lionagi.os.libs.data_handlers._to_list import to_list
from io import StringIO


@singledispatch
def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Dict[str, Any] | None = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    """
    Converts various input types to a pandas DataFrame, with options for
    handling missing data and resetting the index. This function is
    overloaded to handle specific data structures such as lists of
    dictionaries, lists of pandas objects (DataFrames or Series), and more.

    The base implementation attempts to directly convert the input to a
    DataFrame, applying dropna and reset_index as specified.

    Args:
        input_ (Any): The input data to convert into a DataFrame. Accepts a
            wide range of types thanks to overloads.
        drop_how (str): Specifies how missing values are dropped. Passed
            directly to DataFrame.dropna().
        drop_kwargs (Dict[str, Any] | None): Additional keyword arguments for
            DataFrame.dropna().
        reset_index (bool): If True, the DataFrame index will be reset,
            removing the index labels.
        **kwargs: Additional keyword arguments passed to the pandas DataFrame
            constructor.

    Returns:
        pd.DataFrame: A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Note:
        - This function is overloaded to provide specialized behavior for
          different input types, enhancing its flexibility.
    """
    if drop_kwargs is None:
        drop_kwargs = {}

    try:
        df = DataFrame(input_, **kwargs)

        drop_kwargs["how"] = drop_how
        df = df.dropna(**drop_kwargs)
        return df.reset_index(drop=True) if reset_index else df
    except Exception as e:
        raise ValueError(f"Error converting input_ to DataFrame: {e}") from e


@to_df.register
def _(
    input_: list,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Dict | None = None,
    reset_index: bool = True,
    **kwargs,
) -> DataFrame:
    """
    Specialized behavior for converting a list of data to a DataFrame.

    Args:
        input_ (list): The input list to convert into a DataFrame.
        drop_how (str): Specifies how missing values are dropped. Passed
            directly to DataFrame.dropna().
        drop_kwargs (Dict | None): Additional keyword arguments for
            DataFrame.dropna().
        reset_index (bool): If True, the DataFrame index will be reset,
            removing the index labels.
        **kwargs: Additional keyword arguments passed to the pandas DataFrame
            constructor.

    Returns:
        pd.DataFrame: A pandas DataFrame constructed from the input list.

    Raises:
        ValueError: If there is an error during the conversion process.
    """
    if not input_:
        return DataFrame()

    if not isinstance(input_[0], (DataFrame, Series, NDFrame)):
        if drop_kwargs is None:
            drop_kwargs = {}
        try:
            df = DataFrame(input_, **kwargs)
            df = df.dropna(**{**drop_kwargs, "how": drop_how})
            return df.reset_index(drop=True) if reset_index else df
        except Exception as e:
            raise ValueError(f"Error converting input_ to DataFrame: {e}") from e

    if drop_kwargs is None:
        drop_kwargs = {}
    try:
        df = concat(
            input_,
            axis=1 if all(isinstance(i, Series) for i in input_) else 0,
            **kwargs,
        )
    except Exception as e1:
        try:
            input_ = to_list(input_)
            df = input_[0]
            if len(input_) > 1:
                for i in input_[1:]:
                    df = concat([df, i], **kwargs)
        except Exception as e2:
            raise ValueError(
                f"Error converting input_ to DataFrame: {e1}, {e2}"
            ) from e2

    drop_kwargs["how"] = drop_how
    df.dropna(**drop_kwargs, inplace=True)
    return df.reset_index(drop=True) if reset_index else df


# the following are borrowed from llama_index, MIT License
# https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/node_parser/relational/utils.py


def md_to_df(md_str: str) -> DataFrame:
    """Convert Markdown to dataframe."""
    # Replace " by "" in md_str
    md_str = md_str.replace('"', '""')

    # Replace markdown pipe tables with commas
    md_str = md_str.replace("|", '","')

    # Remove the second line (table header separator)
    lines = md_str.split("\n")
    md_str = "\n".join(lines[:1] + lines[2:])

    # Remove the first and last second char of the line (the pipes, transformed to ",")
    lines = md_str.split("\n")
    md_str = "\n".join([line[2:-2] for line in lines])

    # Check if the table is empty
    if len(md_str) == 0:
        return None

    # Use pandas to read the CSV string into a DataFrame
    return read_csv(StringIO(md_str))


def html_to_df(html_str: str) -> DataFrame:
    """Convert HTML to dataframe."""
    try:
        from lxml import html
    except ImportError:
        raise ImportError(
            "You must install the `lxml` package to use this node parser."
        )

    tree = html.fromstring(html_str)
    table_element = tree.xpath("//table")[0]
    rows = table_element.xpath(".//tr")

    data = []
    for row in rows:
        cols = row.xpath(".//td")
        cols = [c.text.strip() if c.text is not None else "" for c in cols]
        data.append(cols)

    # Check if the table is empty
    if len(data) == 0:
        return None

    # Check if the all rows have the same number of columns
    if not all(len(row) == len(data[0]) for row in data):
        return None

    return DataFrame(data[1:], columns=data[0])
