import copy
import logging
import os
import re
from collections.abc import Sequence
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, TypeVar, Literal
from typing_extensions import deprecated

from lion_core.abc import Observable
from lion_core.setting import (
    DEFAULT_LION_ID_CONFIG,
    DEFAULT_TIMEZONE,
    LionIDConfig,
)
from lion_core.sys_utils import SysUtil as _sys

T = TypeVar("T")

import time


def format_deprecated_msg(
    deprecated_name: str,
    deprecated_version: str,
    removal_version: str | None = None,
    replacement: str | Literal["python"] | None = None,
    python_msg: str | None = None,
) -> str:

    msg = f"<{deprecated_name}> is deprecated since <{deprecated_version}> and will be removed in {removal_version}."
    if replacement is None:
        msg += " No `LionAGI` replacement is available."
    if replacement == "python":
        msg += f" Use the Python directly: <{python_msg}> instead."
    elif isinstance(replacement, str):
        msg += f" Please use <{replacement}> instead."
    return msg


class SysUtil:
    """Utility class providing various system-related functionalities."""

    @staticmethod
    def time(
        *,
        tz: timezone = DEFAULT_TIMEZONE,
        type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
        sep: str | None = "T",
        timespec: str | None = "auto",
        custom_format: str | None = None,
        custom_sep: str | None = None,
    ) -> float | str | datetime:
        """
        Get current time in various formats.

        Args:
            tz: Timezone for the time (default: utc).
            type_: Type of time to return (default: "timestamp").
                Options: "timestamp", "datetime", "iso", "custom".
            sep: Separator for ISO format (default: "T").
            timespec: Timespec for ISO format (default: "auto").
            custom_format: Custom strftime format string for
                type_="custom".
            custom_sep: Custom separator for type_="custom",
                replaces "-", ":", ".".

        Returns:
            Current time in the specified format.

        Raises:
            ValueError: If an invalid type_ is provided or if custom_format
                is not provided when type_="custom".
        """
        return _sys.time(
            tz=tz,
            type_=type_,
            sep=sep,
            timespec=timespec,
            custom_format=custom_format,
            custom_sep=custom_sep,
        )

    @staticmethod
    def copy(obj: T, /, *, deep: bool = True, num: int = 1) -> T | list[T]:
        """
        Create one or more copies of an object.

        Args:
            obj: The object to be copied.
            deep: If True, create a deep copy. Otherwise, create a shallow
                copy.
            num: The number of copies to create.

        Returns:
            A single copy if num is 1, otherwise a list of copies.

        Raises:
            ValueError: If num is less than 1.
        """
        return _sys.copy(obj, deep=deep, num=num)

    def id(
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
        n: int = None,
        prefix: str = None,
        postfix: str = None,
        random_hyphen: bool = None,
        num_hyphens: int = None,
        hyphen_start_index: int = None,
        hyphen_end_index: int = None,
    ) -> str:
        return _sys.id(
            config=config,
            n=n,
            prefix=prefix,
            postfix=postfix,
            random_hyphen=random_hyphen,
            num_hyphens=num_hyphens,
            hyphen_start_index=hyphen_start_index,
            hyphen_end_index=hyphen_end_index,
        )

    @staticmethod
    def get_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> str:
        """
        Get the Lion ID of an item.

        Args:
            item: The item to get the ID from.
            config: Configuration dictionary for ID validation.

        Returns:
            The Lion ID of the item.

        Raises:
            LionIDError: If the item does not contain a valid Lion ID.
        """
        return _sys.get_id(item, config)

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> bool:
        """
        Check if an item is a valid Lion ID.

        Args:
            item: The item to check.
            config: Configuration dictionary for ID validation.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        return _sys.is_id(item, config)

    @staticmethod
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
        _sys.clear_path(path, recursive=recursive, exclude=exclude)

    @staticmethod
    def create_path(
        directory: Path | str,
        filename: str,
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
        return _sys.create_path(
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            file_exist_ok=file_exist_ok,
            time_prefix=time_prefix,
            timestamp_format=timestamp_format,
            random_hash_digits=random_hash_digits,
        )

    @staticmethod
    def list_files(dir_path: Path | str, extension: str | None = None) -> list[Path]:
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
        return _sys.list_files(dir_path, extension)

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        """
        Split a path into its directory and filename components.

        Args:
            path: The path to split.

        Returns:
            A tuple containing the directory and filename.
        """
        return _sys.split_path(path)

    @staticmethod
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
        _sys.copy_file(src, dest)

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
            PermissionError: If there are insufficient permissions
                to access the path.
        """
        return _sys.get_file_size(path)

    @staticmethod
    def save_to_file(
        text: str,
        directory: Path | str,
        filename: str,
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
        _sys.save_to_file(
            text=text,
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            file_exist_ok=file_exist_ok,
            time_prefix=time_prefix,
            timestamp_format=timestamp_format,
            random_hash_digits=random_hash_digits,
            verbose=verbose,
        )

    @staticmethod
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
        return _sys.read_file(path)

    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Get the CPU architecture.

        Returns:
            str: 'arm64' if ARM-based, 'x86_64' for Intel/AMD 64-bit, or the
                actual architecture string for other cases.
        """
        return _sys.get_cpu_architecture()

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ):
        """
        Attempt to import a package, installing it if not found.

        Args:
            package_name: The name of the package to import.
            module_name: The specific module to import (if any).
            import_name: The specific name to import from the module (if any).
            pip_name: The name to use for pip installation (if different).

        Raises:
            ImportError: If the package cannot be imported or installed.
            subprocess.CalledProcessError: If pip installation fails.
        """
        return _sys.install_import(
            package_name=package_name,
            module_name=module_name,
            import_name=import_name,
            pip_name=pip_name,
        )

    @staticmethod
    def import_module(
        package_name: str,
        module_name: str = None,
        import_name: str | list = None,
    ) -> Any:
        """
        Import a module by its path.

        Args:
            module_path: The path of the module to import.

        Returns:
            The imported module.

        Raises:
            ImportError: If the module cannot be imported.
        """
        return _sys.import_module(
            package_name=package_name,
            module_name=module_name,
            import_name=import_name,
        )

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        return _sys.is_package_installed(package_name)

    @staticmethod
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
        attempt_install: bool = True,
        error_message: str = "",
    ):
        """
        Check if a package is installed, attempt to install if not.

        Args:
            package_name: The name of the package to check.
            module_name: The specific module to import (if any).
            import_name: The specific name to import from the module (if any).
            pip_name: The name to use for pip installation (if different).
            attempt_install: Whether to attempt installation if not found.
            error_message: Custom error message to use if package not found.

        Raises:
            ImportError: If the package is not found and not installed.
            ValueError: If the import fails after installation attempt.
        """
        return _sys.check_import(
            package_name=package_name,
            module_name=module_name,
            import_name=import_name,
            pip_name=pip_name,
            attempt_install=attempt_install,
            error_message=error_message,
        )

    @staticmethod
    def list_installed_packages() -> list[str]:
        """
        List all installed packages.

        Returns:
            List[str]: A list of names of installed packages.
        """
        return _sys.list_installed_packages()

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """
        Uninstall a specified package.

        Args:
            package_name: The name of the package to uninstall.

        Raises:
            subprocess.CalledProcessError: If the uninstallation fails.
        """
        _sys.uninstall_package(package_name)

    @staticmethod
    def update_package(package_name: str) -> None:
        """
        Update a specified package.

        Args:
            package_name: The name of the package to update.

        Raises:
            subprocess.CalledProcessError: If the update fails.
        """
        _sys.update_package(package_name)

    @staticmethod
    def unique_hash(n: int = 32) -> str:
        """unique random hash"""
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @staticmethod
    def get_bins(input_: list[str], upper: int | None = 2000) -> list[list[int]]:
        """Organizes indices of strings into bins based on a cumulative upper limit.

        Args:
            input_ (List[str]): The list of strings to be binned.
            upper (int): The cumulative length upper limit for each bin.

        Returns:
            List[List[int]]: A list of bins, each bin is a list of indices from the input list.
        """
        current = 0
        bins = []
        current_bin = []
        for idx, item in enumerate(input_):
            if current + len(item) < upper:
                current_bin.append(idx)
                current += len(item)
            else:
                bins.append(current_bin)
                current_bin = [idx]
                current = len(item)
        if current_bin:
            bins.append(current_bin)
        return bins

    ## Deprecated

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.sleep()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="python",
            python_msg="time.sleep()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def sleep(delay: float) -> None:
        """
        Pauses execution for a specified duration.

        Args:
            delay (float): The amount of time, in seconds, to pause execution.
        """
        time.sleep(delay)

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.get_now()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.time()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def get_now(datetime_: bool = False, tz=None) -> float | datetime:
        """Returns the current time either as a Unix timestamp or a datetime object.

        Args:
            datetime_ (bool): If True, returns a datetime object; otherwise, returns a Unix timestamp.

        Returns:
            Union[float, datetime.datetime]: The current time as a Unix timestamp or a datetime object.
        """

        if not datetime_:
            return time.time()
        config_ = {}
        if tz:
            config_["tz"] = tz if isinstance(tz, timezone) else timezone.utc
        return datetime.now(**config_)

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.change_dict_key()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="python",
            python_msg='d["new_key"] = d.pop("old_key")',
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def change_dict_key(dict_: dict[Any, Any], old_key: str, new_key: str) -> None:
        """Safely changes a key in a dictionary if the old key exists.

        Args:
            dict_ (Dict[Any, Any]): The dictionary in which to change the key.
            old_key (str): The old key to be changed.
            new_key (str): The new key to replace the old key.

        Returns:
                None
        """
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.get_timestamp()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.time(type_='timestamp')",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def get_timestamp(tz: timezone = timezone.utc, sep: str = "_") -> str:
        """Returns a timestamp string with optional custom separators and timezone.

        Args:
            tz (timezone): The timezone for the timestamp.
            sep (str): The separator to use in the timestamp string, replacing '-', ':', and '.'.

        Returns:
            str: A string representation of the current timestamp.
        """
        str_ = datetime.now(tz=tz).isoformat()
        if sep is not None:
            for sym in ["-", ":", "."]:
                str_ = str_.replace(sym, sep)
        return str_

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.is_schema()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement=None,
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def is_schema(dict_: dict[Any, Any], schema: dict[Any, type]) -> bool:
        """Validates if the given dictionary matches the expected schema types."""
        return all(
            isinstance(dict_.get(key), expected_type)
            for key, expected_type in schema.items()
        )

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.create_copy()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.copy()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def create_copy(input_: Any, num: int = 1) -> Any | list[Any]:
        """Creates deep copies of the input, either as a single copy or a list of copies.

        Args:
            input_ (Any): The input to be copied.
            num (int): The number of copies to create.

        Returns:
            Union[Any, List[Any]]: A single copy of the input or a list of deep copies.
        """
        if num < 1:
            raise ValueError(f"'num' must be a positive integer: {num}")
        return (
            copy.deepcopy(input_)
            if num == 1
            else [copy.deepcopy(input_) for _ in range(num)]
        )

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.create_id()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.id()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def create_id(n: int = 32) -> str:
        """
        Generates a unique identifier based on the current time and random bytes.

        Args:
            n (int): The length of the generated identifier.

        Returns:
            str: A unique identifier string.
        """
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.clear_dir()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.clear_path()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def clear_dir(
        dir_path: Path | str, recursive: bool = False, exclude: list[str] = None
    ) -> None:
        """
        Clears all files (and, if recursive, directories) in the specified directory,
        excluding files that match any pattern in the exclude list.

        Args:
            dir_path (Union[Path, str]): The path to the directory to clear.
            recursive (bool): If True, clears directories recursively. Defaults to False.
            exclude (List[str]): A list of string patterns to exclude from deletion. Defaults to None.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(
                f"The specified directory {dir_path} does not exist."
            )

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in dir_path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            if recursive and file_path.is_dir():
                SysUtil.clear_dir(file_path, recursive=True, exclude=exclude)
            elif file_path.is_file() or file_path.is_symlink():
                try:
                    file_path.unlink()
                    logging.info(f"Successfully deleted {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {file_path}. Reason: {e}")
                    raise

    @deprecated(
        format_deprecated_msg(
            deprecated_name="SysUtil.get_size()",
            deprecated_version="0.3.0",
            removal_version="1.0.0",
            replacement="SysUtil.get_file_size()",
        ),
        category=DeprecationWarning,
    )
    @staticmethod
    def get_size(path: Path | str) -> int:
        """
        Gets the size of a file or total size of files in a directory.

        Args:
            path (Path | str): The file or directory path.

        Returns:
            int: The size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        path = Path(path)
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
        else:
            raise FileNotFoundError(f"{path} does not exist.")


# File: lionagi/os/sys_utils.py
