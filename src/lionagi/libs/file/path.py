import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from ..utils import unique_hash


def create_path(
    directory: Path | str,
    filename: str,
    extension: str = None,
    timestamp: bool = False,
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
        dir_exist_ok: If True, doesn't raise an error if the directory
            exists.
        file_exist_ok: If True, allows overwriting of existing files.
        time_prefix: If True, adds the timestamp as a prefix instead of
            a suffix.
        timestamp_format: Custom format for the timestamp.
        random_hash_digits: Number of digits for the random hash.

    Returns:
        The full path to the new or existing file.

    Raises:
        ValueError: If the filename contains illegal characters.
        FileExistsError: If the file exists and file_exist_ok is False.
    """
    if "/" in filename or "\\" in filename:
        raise ValueError("Filename cannot contain directory separators.")
    directory = Path(directory)

    name, ext = None, None
    if "." in filename:
        name, ext = filename.rsplit(".", 1)
    else:
        name = filename
        ext = extension.strip(".").strip() if extension else None

    if not ext:
        raise ValueError("No extension provided for filename.")

    ext = f".{ext}" if ext else ""

    if timestamp:
        timestamp_str = datetime.now().strftime(
            timestamp_format or "%Y%m%d%H%M%S"
        )
        name = (
            f"{timestamp_str}_{name}"
            if time_prefix
            else f"{name}_{timestamp_str}"
        )

    if random_hash_digits > 0:
        random_hash = "-" + unique_hash(random_hash_digits)
        name = f"{name}{random_hash}"

    full_filename = f"{name}{ext}"
    full_path = directory / full_filename

    if full_path.exists():
        if file_exist_ok:
            return full_path
        raise FileExistsError(
            f"File {full_path} already exists and file_exist_ok is False."
        )
    full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)
    return full_path


def is_valid_path(
    path: str | Path,
    *,
    max_length: int | None = None,
    allow_relative: bool = True,
    allow_symlinks: bool = True,
    custom_reserved_names: list[str] | None = None,
    strict_mode: bool = False,
) -> bool:
    """
    Validates whether the given path is syntactically valid for the current operating system.

    Args:
        path (Union[str, Path]): The filesystem path to validate.
        max_length (Optional[int]): Maximum allowed path length. If None, uses OS default.
        allow_relative (bool): Whether to allow relative paths. Default is True.
        allow_symlinks (bool): Whether to allow symlinks. Default is True.
        custom_reserved_names (Optional[List[str]]): Additional reserved names to check.
        strict_mode (bool): If True, applies stricter validation rules. Default is False.

    Returns:
        bool: True if the path is valid, False otherwise.

    Raises:
        ValueError: If the path is invalid, with a detailed explanation.
    """
    if isinstance(path, Path):
        path_str = str(path)
    elif isinstance(path, str):
        path_str = path
    else:
        raise TypeError("Path must be a string or Path object.")

    if not path_str:
        raise ValueError("Path cannot be an empty string.")

    issues = []
    is_windows = sys.platform.startswith("win")

    # Common checks for both Windows and Unix-like systems
    if "\0" in path_str:
        issues.append("Path contains null character.")

    if not max_length:
        max_length = 260 if is_windows else 4096
    if len(path_str) > max_length:
        issues.append(
            f"Path exceeds the maximum length of {max_length} characters."
        )

    if is_windows:
        # Windows-specific validation
        invalid_chars = r'<>:"/\\|?*'
        if re.search(f"[{re.escape(invalid_chars)}]", path_str):
            issues.append(f"Path contains invalid characters: {invalid_chars}")

        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if custom_reserved_names:
            reserved_names.update(custom_reserved_names)

        path = Path(path_str)
        for part in path.parts:
            name = part.upper().rstrip(". ")
            if name in reserved_names:
                issues.append(f"Path contains a reserved name: '{part}'")

        if path_str.endswith(" ") or path_str.endswith("."):
            issues.append(
                "Path cannot end with a space or a period on Windows."
            )

        if strict_mode:
            if not path_str.startswith("\\\\?\\") and len(path_str) > 260:
                issues.append(
                    "Path exceeds 260 characters without long path prefix."
                )

    else:
        # Unix-like systems validation
        if strict_mode:
            if re.search(r"//+", path_str):
                issues.append("Path contains consecutive slashes.")

        if not allow_relative and not path_str.startswith("/"):
            issues.append("Relative paths are not allowed.")

    # Common additional checks
    if not allow_symlinks and Path(path_str).is_symlink():
        issues.append("Symlinks are not allowed.")

    if strict_mode:
        if re.search(r"\s", path_str):
            issues.append("Path contains whitespace characters.")

    if issues:
        raise ValueError("Invalid path: " + "; ".join(issues))

    return True


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


def _get_path_kwargs(
    persist_path: str | Path, postfix: str, **path_kwargs: Any
) -> dict[str, Any]:
    """
    Generate keyword arguments for path creation.

    Args:
        persist_path: The base path to use.
        postfix: The file extension to use.
        **path_kwargs: Additional keyword arguments to override defaults.

    Returns:
        A dictionary of keyword arguments for path creation.
    """
    persist_path = Path(persist_path)
    postfix = f".{postfix.strip('.')}"

    if persist_path.suffix != postfix:
        dirname = persist_path
        filename = f"new_file{postfix}"
    else:
        dirname, filename = persist_path.parent, persist_path.name

    return {
        "timestamp": path_kwargs.get("timestamp", False),
        "file_exist_ok": path_kwargs.get("file_exist_ok", True),
        "directory": path_kwargs.get("directory", dirname),
        "filename": path_kwargs.get("filename", filename),
    }


def clear_path(
    path: Path | str,
    /,
    recursive: bool = False,
    exclude: list[str] | None = None,
) -> None:
    """
    Clear all files and directories in the specified path.

    Args:
        path: The path to the directory to clear.
        recursive: If True, clears directories recursively.
        exclude: A list of string patterns to exclude from deletion.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If there are insufficient permissions to delete
            files.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"The specified directory {path} does not exist."
        )

    exclude = exclude or []
    exclude_pattern = re.compile("|".join(exclude)) if exclude else None

    for file_path in path.iterdir():
        if exclude_pattern and exclude_pattern.search(file_path.name):
            logging.info(f"Excluded from deletion: {file_path}")
            continue

        try:
            if file_path.is_dir():
                if recursive:
                    clear_path(file_path, recursive=True, exclude=exclude)
                    file_path.rmdir()
                else:
                    continue
            else:
                file_path.unlink()
            logging.info(f"Successfully deleted {file_path}")
        except PermissionError as e:
            logging.error(f"Permission denied when deleting {file_path}: {e}")
        except Exception as e:
            logging.error(f"Failed to delete {file_path}: {e}")
