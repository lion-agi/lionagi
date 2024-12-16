# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Any

from lionagi.integrations.pandas_.to_df import to_df
from lionagi.libs.file.types import create_path


def to_csv(
    input_: Any,
    /,
    *,
    directory: str | Path,
    filename: str,
    timestamp: bool = False,
    random_hash_digits: int = 0,
    drop_how: str = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    concat_kwargs: dict[str, Any] | None = None,
    df_kwargs: dict[str, Any] | None = None,
    path_kwargs: dict[str, Any] | None = None,
    verbose: bool = False,
) -> None:
    """
    Convert input to a DataFrame and save it as a CSV file.

    Args:
        input_: The input data to convert to a DataFrame.
        directory: The directory to save the CSV file.
        filename: The name of the CSV file (without extension).
        timestamp: If True, add a timestamp to the filename.
        random_hash_digits: Number of random hash digits to add to the filename.
        drop_how: How to drop NA values in the DataFrame.
        drop_kwargs: Additional keyword arguments for dropna().
        reset_index: If True, reset the index of the DataFrame.
        concat_kwargs: Keyword arguments for pandas.concat().
        df_kwargs: Additional keyword arguments for to_df().
        path_kwargs: Additional keyword arguments for create_path().
        verbose: If True, print the file path after saving.

    Returns:
        None
    """
    df = to_df(
        input_,
        drop_how=drop_how,
        drop_kwargs=drop_kwargs,
        reset_index=reset_index,
        concat_kwargs=concat_kwargs,
        **(df_kwargs or {}),
    )

    fp = create_path(
        directory=directory,
        filename=filename,
        timestamp=timestamp,
        random_hash_digits=random_hash_digits,
        extension="csv",
        **(path_kwargs or {}),
    )

    df.to_csv(fp, index=False)

    if verbose:
        print(f"Data saved to {fp}")


def to_excel(
    input_: Any,
    /,
    *,
    directory: str | Path,
    filename: str,
    timestamp: bool = False,
    random_hash_digits: int = 0,
    drop_how: str = "all",
    drop_kwargs: dict[str, Any] | None = None,
    reset_index: bool = True,
    concat_kwargs: dict[str, Any] | None = None,
    df_kwargs: dict[str, Any] | None = None,
    path_kwargs: dict[str, Any] | None = None,
    verbose: bool = False,
) -> None:
    """
    Convert input to a DataFrame and save it as an Excel file.

    Args:
        input_: The input data to convert to a DataFrame.
        directory: The directory to save the Excel file.
        filename: The name of the Excel file (without extension).
        timestamp: If True, add a timestamp to the filename.
        random_hash_digits: Number of random hash digits to add to the filename.
        drop_how: How to drop NA values in the DataFrame.
        drop_kwargs: Additional keyword arguments for dropna().
        reset_index: If True, reset the index of the DataFrame.
        concat_kwargs: Keyword arguments for pandas.concat().
        df_kwargs: Additional keyword arguments for to_df().
        path_kwargs: Additional keyword arguments for create_path().
        verbose: If True, print the file path after saving.

    Returns:
        None
    """
    df = to_df(
        input_,
        drop_how=drop_how,
        drop_kwargs=drop_kwargs,
        reset_index=reset_index,
        concat_kwargs=concat_kwargs,
        **(df_kwargs or {}),
    )

    fp = create_path(
        directory=directory,
        filename=filename,
        timestamp=timestamp,
        random_hash_digits=random_hash_digits,
        extension="xlsx",
        **(path_kwargs or {}),
    )

    df.to_excel(fp, index=False)

    if verbose:
        print(f"Data saved to {fp}")


__all__ = ["to_csv", "to_excel"]
