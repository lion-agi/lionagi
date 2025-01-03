# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChunkContentParams(BaseModel):
    """Parameters for chunking text content into smaller pieces.

    This model defines parameters used by the chunk_content function to split text
    content into chunks, with support for both character-based and token-based chunking.
    """

    content: str = Field(description="The text content to be chunked")
    chunk_by: Literal["chars", "tokens"] = Field(
        default="chars",
        description="Method to use for chunking: 'chars' for character-based or 'tokens' for token-based",
    )
    tokenizer: Callable[[str], list[str]] | None = Field(
        default=None,
        description="Function to use for tokenization. Defaults to str.split if None",
    )
    chunk_size: int = Field(
        default=1024, ge=1, description="Target size for each chunk"
    )
    overlap: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of overlap between chunks (0.0 to 1.0)",
    )
    threshold: int = Field(
        default=256,
        ge=0,
        description="Minimum size threshold for the last chunk",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata to include with each chunk",
    )
    return_tokens: bool = Field(
        default=False,
        description="If True, return chunks as token lists; if False, return as joined strings",
    )


class DirToFilesParams(BaseModel):
    """Parameters for processing directories and collecting file paths.

    This model defines parameters used by the dir_to_files function to recursively
    process directories and collect matching file paths.
    """

    directory: Path | str = Field(
        description="Directory to process recursively"
    )
    file_types: list[str] | None = Field(
        default=None,
        description="List of file extensions to include (e.g., ['.txt', '.pdf']). If None, includes all types",
    )
    max_workers: int | None = Field(
        default=None,
        description="Maximum number of worker threads for concurrent processing",
    )
    ignore_errors: bool = Field(
        default=False,
        description="If True, log warnings for errors instead of raising exceptions",
    )
    verbose: bool = Field(
        default=False,
        description="If True, print verbose output during processing",
    )


class FileToChunksParams(BaseModel):
    """Parameters for splitting file content into chunks.

    This model defines parameters used by the file_to_chunks function to read
    and split file content into chunks with metadata.
    """

    file_path: Path | str = Field(
        description="Path to the file to be processed"
    )
    chunk_func: Callable[[str, int, float, int], list[str]] = Field(
        description="Function to use for chunking the content"
    )
    chunk_size: int = Field(
        default=1500, ge=1, description="Target size for each chunk"
    )
    overlap: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Fraction of overlap between chunks (0.0 to 1.0)",
    )
    threshold: int = Field(
        default=200,
        ge=0,
        description="Minimum size threshold for the last chunk",
    )
    encoding: str = Field(
        default="utf-8",
        description="File encoding to use when reading the file",
    )
    custom_metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata to include with each chunk",
    )
    output_dir: Path | str | None = Field(
        default=None,
        description="Directory to save output chunks (if provided)",
    )
    verbose: bool = Field(
        default=False,
        description="If True, print verbose output during processing",
    )
    timestamp: bool = Field(
        default=True,
        description="If True, include timestamp in output filenames",
    )
    random_hash_digits: int = Field(
        default=4,
        ge=0,
        description="Number of random hash digits to include in output filenames",
    )


class SaveToFileParams(BaseModel):
    """Parameters for saving text content to a file.

    This model defines parameters used by the save_to_file function to save
    text content to a file with various options for naming and handling.
    """

    text: str = Field(description="The text content to save to file")
    directory: Path | str = Field(
        description="Directory where the file will be saved"
    )
    filename: str = Field(description="Name of the file to create")
    extension: str | None = Field(
        default=None,
        description="File extension (with or without leading dot)",
    )
    timestamp: bool = Field(
        default=False, description="If True, append timestamp to filename"
    )
    dir_exist_ok: bool = Field(
        default=True,
        description="If True, creates directory if it doesn't exist",
    )
    file_exist_ok: bool = Field(
        default=False, description="If True, allows overwriting existing files"
    )
    time_prefix: bool = Field(
        default=False,
        description="If True, prepend timestamp instead of append",
    )
    timestamp_format: str | None = Field(
        default=None,
        description="Custom format for timestamp (strftime format)",
    )
    random_hash_digits: int = Field(
        default=0,
        ge=0,
        description="Number of random hash digits to append to filename",
    )
    verbose: bool = Field(
        default=True, description="If True, logs the file path after saving"
    )
