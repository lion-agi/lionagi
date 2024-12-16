from typing import Any, Literal

import pandas as pd

from .to_df import to_df


def read_csv(
    filepath: str,
    chunk_size: int | None = None,
    low_memory: bool = False,
    return_as: Literal["dataframe", "json", "jsonl", "dict"] = "dataframe",
    **kwargs: Any,
) -> pd.DataFrame | str | list | dict:
    """
    Reads a CSV file into a DataFrame with optional chunking for large files.

    Args:
        filepath: The path to the CSV file to read.
        chunk_size: Number of rows to read at a time. If specified, returns an iterable.
        low_memory: Internally process the file in chunks to conserve memory (slower).
        **kwargs: Additional keyword arguments to pass to pandas.read_csv function.

    Returns:
        A DataFrame containing the data read from the CSV file, or a TextFileReader
        if chunk_size is specified.

    Example:
        >>> df = read_csv('large_file.csv', chunk_size=10000)
        >>> for chunk in df:
        ...     process_chunk(chunk)
    """
    try:
        if chunk_size:
            return pd.read_csv(
                filepath, chunksize=chunk_size, low_memory=low_memory, **kwargs
            )
        df = pd.read_csv(filepath, low_memory=low_memory, **kwargs)
        df = to_df(df)
        if return_as == "dataframe":
            return df
        if return_as == "json":
            return df.to_json(orient="records")
        if return_as == "jsonl":
            return df.to_json(orient="records", lines=True)
        if return_as == "dict":
            return df.to_dict(orient="records")

    except Exception as e:
        raise OSError(f"Error reading CSV file: {e}") from e


def read_json(
    filepath: str,
    orient: str | None = None,
    lines: bool = False,
    chunk_size: int | None = None,
    return_as: Literal["dataframe", "json", "jsonl", "dict"] = "dataframe",
    **kwargs: Any,
) -> pd.DataFrame | pd.io.json._json.JsonReader:
    """
    Reads a JSON file into a DataFrame with options for different JSON formats.

    Args:
        filepath: The path to the JSON file to read.
        orient: Indication of expected JSON string format.
                Allowed values are: 'split', 'records', 'index', 'columns', 'values', 'table'.
        lines: Read the file as a json object per line.
        chunk_size: Number of lines to read at a time. If specified, returns an iterable.
        **kwargs: Additional keyword arguments to pass to pandas.read_json function.

    Returns:
        A DataFrame containing the data read from the JSON file, or a JsonReader
        if chunk_size is specified.

    Example:
        >>> df = read_json('data.json', orient='records', lines=True)
    """
    try:
        if chunk_size:
            return pd.read_json(
                filepath,
                orient=orient,
                lines=lines,
                chunksize=chunk_size,
                **kwargs,
            )
        df = pd.read_json(filepath, orient=orient, lines=lines, **kwargs)
        df = to_df(df)
        if return_as == "dataframe":
            return df
        if return_as == "json":
            return df.to_json(orient="records")
        if return_as == "jsonl":
            return df.to_json(orient="records", lines=True)
        if return_as == "dict":
            return df.to_dict(orient="records")

    except Exception as e:
        raise OSError(f"Error reading JSON file: {e}") from e
