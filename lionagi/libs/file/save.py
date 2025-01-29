# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from pathlib import Path
from typing import Any

from lionagi.utils import create_path


def save_to_file(
    text: str,
    directory: Path | str,
    filename: str,
    extension: str = None,
    timestamp: bool = False,
    dir_exist_ok: bool = True,
    file_exist_ok: bool = False,
    time_prefix: bool = False,
    timestamp_format: str | None = None,
    random_hash_digits: int = 0,
    verbose: bool = True,
) -> Path:
    """
    Save text to a file within a specified directory, optionally adding a
    timestamp, hash, and verbose logging.

    Args:
        text: The text to save.
        directory: The directory path to save the file.
        filename: The filename for the saved text.
        timestamp: If True, append a timestamp to the filename.
        dir_exist_ok: If True, creates the directory if it does not exist.
        time_prefix: If True, prepend the timestamp instead of appending.
        timestamp_format: A custom format for the timestamp.
        random_hash_digits: Number of random hash digits to append
            to filename.
        verbose: If True, logs the file path after saving.

    Returns:
        Path: The path to the saved file.

    Raises:
        OSError: If there's an error creating the directory or
            writing the file.
    """
    try:
        file_path = create_path(
            directory=directory,
            filename=filename,
            extension=extension,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            file_exist_ok=file_exist_ok,
            time_prefix=time_prefix,
            timestamp_format=timestamp_format,
            random_hash_digits=random_hash_digits,
        )
        with file_path.open("w", encoding="utf-8") as file:
            file.write(text)
        file.close()
        if verbose:
            logging.info(f"Text saved to: {file_path}")
        return file_path

    except OSError as e:
        logging.error(f"Failed to save file {filename}: {e}")
        raise


def save_chunks(
    chunks: list[dict[str, Any]],
    output_dir: str | Path,
    verbose: bool,
    timestamp: bool,
    random_hash_digits: int,
) -> None:
    """Helper function to save chunks to files."""
    output_path = Path(output_dir)
    for i, chunk in enumerate(chunks):
        file_path = create_path(
            directory=output_path,
            filename=f"chunk_{i+1}",
            extension="json",
            timestamp=timestamp,
            random_hash_digits=random_hash_digits,
        )
        save_to_file(
            json.dumps(chunk, ensure_ascii=False, indent=2),
            directory=file_path.parent,
            filename=file_path.name,
            verbose=verbose,
        )
