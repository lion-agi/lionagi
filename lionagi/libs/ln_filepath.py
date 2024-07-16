from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import List

from lion_core.libs import unique_hash


class FilePathUtil:
    
    @staticmethod
    def clear_path(
        path: Path | str,
        /,
        recursive: bool = False,
        exclude: list[str] | None = None
    ) -> None:
        """
        Clear all files (and, if recursive, directories) in the specified directory,
        excluding files that match any pattern in the exclude list.

        Args:
            path: The path to the directory to clear.
            recursive: If True, clears directories recursively.
            exclude: A list of string patterns to exclude from deletion.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If there are insufficient permissions to delete files.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"The specified directory {path} does not exist.")

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            try:
                if recursive and file_path.is_dir():
                    FilePathUtil.clear_path(file_path, recursive=True, exclude=exclude)
                elif file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
                    logging.info(f"Successfully deleted {file_path}")
            except PermissionError as e:
                logging.error(f"Permission denied when deleting {file_path}: {e}")
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {e}")

    @staticmethod
    def create_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        file_exist_ok: bool = False,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
    ) -> Path:
        """
        Generate a new file path with optional timestamp and random hash.

        Args:
            directory: The directory where the file will be created.
            filename: The base name of the file to create.
            timestamp: If True, adds a timestamp to the filename.
            dir_exist_ok: If True, doesn't raise an error if the directory exists.
            file_exist_ok: If True, allows overwriting of existing files.
            time_prefix: If True, adds the timestamp as a prefix instead of a suffix.
            timestamp_format: Custom format for the timestamp.
            random_hash_digits: Number of digits for the random hash.

        Returns:
            The full path to the new or existing file.

        Raises:
            ValueError: If the filename contains illegal characters.
            FileExistsError: If the file exists and file_exist_ok is False.
        """
        directory = Path(directory)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError("Invalid filename. Ensure it has a valid extension.")

        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        ext = f".{ext}" if ext else ""

        if timestamp:
            timestamp_str = datetime.now().strftime(timestamp_format or "%Y%m%d%H%M%S")
            filename = (
                f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
            )
        else:
            filename = name

        if file_exist_ok and random_hash_digits < 5:
            random_hash_digits = 5

        random_hash = (
            "-" + unique_hash(random_hash_digits) if random_hash_digits > 0 else ""
        )

        full_filename = f"{filename}{random_hash}{ext}"
        full_path = directory / full_filename

        if not file_exist_ok:
            counter = 1
            while full_path.exists():
                new_filename = f"{filename}_{counter}{random_hash}{ext}"
                full_path = directory / new_filename
                counter += 1
        elif full_path.exists():
            logging.warning(f"File {full_path} already exists. Using existing file.")

        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    def list_files(dir_path: Path | str, extension: str | None = None) -> List[Path]:
        """
        List all files in a specified directory with an optional extension filter.

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
        return list(dir_path.glob(f"*.{extension}" if extension else "*"))

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        """
        Split a path into its directory and filename components.

        Args:
            path: The path to split.

        Returns:
            A tuple containing the directory and filename.
        """
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str) -> None:
        """
        Copy a file from a source path to a destination path.

        Args:
            src: The source file path.
            dest: The destination file path.

        Raises:
            FileNotFoundError: If the source file does not exist or is not a file.
            PermissionError: If there are insufficient permissions to copy the file.
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

    @staticmethod
    def get_file_size(path: Path | str) -> int:
        """
        Get the size of a file or total size of files in a directory.

        Args:
            path: The file or directory path.

        Returns:
            The size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If there are insufficient permissions to access the path.
        """
        path = Path(path)
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
            else:
                raise FileNotFoundError(f"{path} does not exist.")
        except PermissionError as e:
            raise PermissionError(f"Permission denied when accessing {path}") from e

    @staticmethod
    def save_to_file(
        text: str,
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
        verbose: bool = True,
    ) -> bool:
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
            random_hash_digits: Number of random hash digits to append to filename.
            verbose: If True, logs the file path after saving.

        Returns:
            True if the text was successfully saved.

        Raises:
            OSError: If there's an error creating the directory or writing the file.
        """
        try:
            file_path = FilePathUtil.create_path(
                directory=directory,
                filename=filename,
                timestamp=timestamp,
                dir_exist_ok=dir_exist_ok,
                time_prefix=time_prefix,
                timestamp_format=timestamp_format,
                random_hash_digits=random_hash_digits,
            )

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)

            if verbose:
                logging.info(f"Text saved to: {file_path}")

            return True
        except OSError as e:
            logging.error(f"Failed to save file {filename}: {e}")
            raise

# File: lionagi/libs/ln_filepath.py