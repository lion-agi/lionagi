# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .chunk import chunk_content
from .save import save_chunks


def dir_to_files(
    directory: str | Path,
    file_types: list[str] | None = None,
    max_workers: int | None = None,
    ignore_errors: bool = False,
    verbose: bool = False,
) -> list[Path]:
    """
    Recursively process a directory and return a list of file paths.

    This function walks through the given directory and its subdirectories,
    collecting file paths that match the specified file types (if any).

    Args:
        directory (Union[str, Path]): The directory to process.
        file_types (Optional[List[str]]): List of file extensions to include (e.g., ['.txt', '.pdf']).
                                          If None, include all file types.
        max_workers (Optional[int]): Maximum number of worker threads for concurrent processing.
                                     If None, uses the default ThreadPoolExecutor behavior.
        ignore_errors (bool): If True, log warnings for errors instead of raising exceptions.
        verbose (bool): If True, print verbose output.

    Returns:
        List[Path]: A list of Path objects representing the files found.

    Raises:
        ValueError: If the provided directory doesn't exist or isn't a directory.
    """
    directory_path = Path(directory)
    if not directory_path.is_dir():
        raise ValueError(
            f"The provided path is not a valid directory: {directory}"
        )

    def process_file(file_path: Path) -> Path | None:
        try:
            if file_types is None or file_path.suffix in file_types:
                return file_path
        except Exception as e:
            if ignore_errors:
                if verbose:
                    logging.warning(f"Error processing {file_path}: {e}")
            else:
                raise ValueError(f"Error processing {file_path}: {e}") from e
        return None

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_file, f)
                for f in directory_path.rglob("*")
                if f.is_file()
            ]
            files = [
                future.result()
                for future in as_completed(futures)
                if future.result() is not None
            ]

        if verbose:
            logging.info(f"Processed {len(files)} files from {directory}")

        return files
    except Exception as e:
        raise ValueError(f"Error processing directory {directory}: {e}") from e


def file_to_chunks(
    file_path: str | Path,
    chunk_func: Callable[[str, int, float, int], list[str]],
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
    encoding: str = "utf-8",
    custom_metadata: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    verbose: bool = False,
    timestamp: bool = True,
    random_hash_digits: int = 4,
) -> list[dict[str, Any]]:
    """
    Process a file and split its content into chunks.

    This function reads a file, splits its content into chunks using the provided
    chunking function, and optionally saves the chunks to separate files.

    Args:
        file_path (Union[str, Path]): Path to the file to be processed.
        chunk_func (Callable): Function to use for chunking the content.
        chunk_size (int): The target size for each chunk.
        overlap (float): The fraction of overlap between chunks.
        threshold (int): The minimum size for the last chunk.
        encoding (str): File encoding to use when reading the file.
        custom_metadata (Optional[Dict[str, Any]]): Additional metadata to include with each chunk.
        output_dir (Optional[Union[str, Path]]): Directory to save output chunks (if provided).
        verbose (bool): If True, print verbose output.
        timestamp (bool): If True, include timestamp in output filenames.
        random_hash_digits (int): Number of random hash digits to include in output filenames.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a chunk with metadata.

    Raises:
        ValueError: If there's an error processing the file.
    """
    try:
        file_path = Path(file_path)
        with open(file_path, encoding=encoding) as f:
            content = f.read()

        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            **(custom_metadata or {}),
        }

        chunks = chunk_content(
            content, chunk_func, chunk_size, overlap, threshold, metadata
        )

        if output_dir:
            save_chunks(
                chunks, output_dir, verbose, timestamp, random_hash_digits
            )

        return chunks
    except Exception as e:
        raise ValueError(f"Error processing file {file_path}: {e}") from e
