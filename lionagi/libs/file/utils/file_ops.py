# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from shutil import copy2


def copy_file(src: Path | str, dest: Path | str) -> None:
    """
    Copy a file from a source path to a destination path.

    Args:
        src: The source file path.
        dest: The destination file path.

    Raises:
        FileNotFoundError: If the source file does not exist or is not
            a file.
        PermissionError: If there are insufficient permissions to copy
            the file.
        OSError: If there's an OS-level error during the copy operation.
    """
    src_path, dest_path = Path(src), Path(dest)
    if not src_path.is_file():
        raise FileNotFoundError(f"{src_path} does not exist or is not a file.")

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(src_path, dest_path)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied when copying {src_path} to {dest_path}"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to copy {src_path} to {dest_path}: {e}") from e


def get_file_size(path: Path | str) -> int:
    """
    Get the size of a file or total size of files in a directory.

    Args:
        path: The file or directory path.

    Returns:
        The size in bytes.

    Raises:
        FileNotFoundError: If the path does not exist.
        PermissionError: If there are insufficient permissions
            to access the path.
    """
    path = Path(path)
    try:
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(
                f.stat().st_size for f in path.rglob("*") if f.is_file()
            )
        else:
            raise FileNotFoundError(f"{path} does not exist.")
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied when accessing {path}"
        ) from e


def list_files(
    dir_path: Path | str, extension: str | None = None
) -> list[Path]:
    """
    List all files in a specified directory with an optional extension
    filter, including files in subdirectories.

    Args:
        dir_path: The directory path where files are listed.
        extension: Filter files by extension.

    Returns:
        A list of Path objects representing files in the directory.

    Raises:
        NotADirectoryError: If the provided dir_path is not a directory.
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"{dir_path} is not a directory.")

    pattern = f"*.{extension}" if extension else "*"
    return [f for f in dir_path.rglob(pattern) if f.is_file()]


def read_file(path: Path | str, /) -> str:
    """
    Read the contents of a file.

    Args:
        path: The path to the file to read.

    Returns:
        str: The contents of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to read
            the file.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logging.error(f"File not found: {path}: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied when reading file: {path}: {e}")
        raise
