# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Literal

from lionagi.utils import lcall

from .chunk import chunk_content
from .save import save_chunks


def dir_to_files(
    directory: str | Path,
    file_types: list[str] | None = None,
    max_workers: int | None = None,
    ignore_errors: bool = False,
    verbose: bool = False,
    recursive: bool = False,
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
        recursive (bool): If True, process directories recursively (the default).
                          If False, only process files in the top-level directory.

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

    file_iterator = (
        directory_path.rglob("*") if recursive else directory_path.glob("*")
    )
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_file, f)
                for f in file_iterator
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
    chunk_by: Literal["chars", "tokens"] = "chars",
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
    encoding: str = "utf-8",
    custom_metadata: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    verbose: bool = False,
    timestamp: bool = True,
    random_hash_digits: int = 4,
    as_node: bool = False,
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
        if isinstance(file_path, str):
            file_path = Path(file_path)

        text = file_path.read_text(encoding=encoding)

        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            **(custom_metadata or {}),
        }

        chunks = chunk_content(
            text,
            chunk_by=chunk_by,
            chunk_size=chunk_size,
            overlap=overlap,
            threshold=threshold,
            metadata=metadata,
            as_node=as_node,
        )

        if output_dir:
            save_chunks(
                chunks=chunks,
                output_dir=output_dir,
                verbose=verbose,
                timestamp=timestamp,
                random_hash_digits=random_hash_digits,
            )

        return chunks
    except Exception as e:
        raise ValueError(f"Error processing file {file_path}: {e}") from e


def chunk(
    *,
    text: str | None = None,
    url_or_path: str | Path = None,
    file_types: list[str] | None = None,  # only local files
    recursive: bool = False,  # only local files
    tokenizer: Callable[[str], list[str]] = None,
    chunk_by: Literal["chars", "tokens"] = "chars",
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
    output_file: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
    reader_tool: Callable = None,
    as_node: bool = False,
) -> list:
    texts = []
    if not text:
        if isinstance(url_or_path, str):
            url_or_path = Path(url_or_path)

        chunks = None
        files = None
        if url_or_path.exists():
            if url_or_path.is_dir():
                files = dir_to_files(
                    directory=url_or_path,
                    file_types=file_types,
                    recursive=recursive,
                )
            elif url_or_path.is_file():
                files = [url_or_path]
        else:
            files = (
                [str(url_or_path)]
                if not isinstance(url_or_path, list)
                else url_or_path
            )

        if reader_tool is None:
            reader_tool = lambda x: x.read_text(encoding="utf-8")

        if reader_tool == "docling":
            from lionagi.libs.package.imports import check_import

            DocumentConverter = check_import(
                "docling",
                module_name="document_converter",
                import_name="DocumentConverter",
            )
            converter = DocumentConverter()
            reader_tool = lambda x: converter.convert(
                x
            ).document.export_to_markdown()

        texts = lcall(files, reader_tool)

    else:
        texts = [text]

    chunks = lcall(
        texts,
        chunk_content,
        chunk_by=chunk_by,
        chunk_size=chunk_size,
        overlap=overlap,
        threshold=threshold,
        metadata=metadata,
        as_node=True,
        flatten=True,
        tokenizer=tokenizer or str.split,
    )
    if threshold:
        chunks = [c for c in chunks if len(c.content) > threshold]

    if output_file:
        from lionagi.protocols.generic.pile import Pile

        output_file = Path(output_file)
        if output_file.suffix == ".csv":
            p = Pile(chunks)
            p.to_csv_file(output_file)

        elif output_file.suffix == ".json":
            p = Pile(chunks)
            p.to_json_file(output_file, use_pd=True)

        elif output_file.suffix in Pile.list_adapters():
            p = Pile(chunks)
            p.adapt_to(output_file.suffix, fp=output_file)

        else:
            raise ValueError(f"Unsupported output file format: {output_file}")

    if as_node:
        return chunks

    return [c.content for c in chunks]
