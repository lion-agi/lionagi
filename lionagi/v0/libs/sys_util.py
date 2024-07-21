import copy
import logging
import os
import re
import time
import warnings
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, TypeVar

from typing_extensions import deprecated

from lion_core import CoreUtil
from lionagi.setting.sys_config import LION_ID_CONFIG, TIME_CONFIG

T = TypeVar("T")
PATH_TYPE = str | Path

_timestamp_syms = ["-", ":", "."]


class SysUtil:

    # new
    @staticmethod
    def time(
        *,
        tz: timezone = TIME_CONFIG["tz"],
        type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
        iso: bool = False,
        sep: str | None = "T",
        timespec: str | None = "auto",
        custom_format: str | None = None,
        custom_sep: str | None = None,
    ) -> float | str | datetime:
        """
        Get current time in various formats.

        Args:
            tz: Timezone for the time (default: TIME_CONFIG["tz"]).
            type_: Type of time to return (default: "timestamp").
                Options: "timestamp", "datetime", "iso", "custom".
            iso: If True, returns ISO format string (deprecated, use type_="iso").
            sep: Separator for ISO format (default: "T").
            timespec: Timespec for ISO format (default: "auto").
            custom_format: Custom strftime format string for type_="custom".
            custom_sep: Custom separator for type_="custom", replaces "-", ":", ".".

        Returns:
            Current time in the specified format.

        Raises:
            `ValueError`: If an invalid type_ is provided or if custom_format
                is not provided when type_="custom".
        """
        return CoreUtil.time(
            tz=tz,
            type_=type_,
            iso=iso,
            sep=sep,
            timespec=timespec,
            custom_format=custom_format,
            custom_sep=custom_sep,
        )

    # new
    @staticmethod
    def copy(obj: T, /, *, deep: bool = True, num: int = 1) -> T | list[T]:
        """
        Create one or more copies of an object.

        Args:
            obj: The object to be copied.
            deep: If True, create a deep copy. Otherwise, create a shallow copy.
            num: The number of copies to create.

        Returns:
            A single copy if num is 1, otherwise a list of copies.

        Raises:
            `ValueError`: If num is less than 1.
        """
        return CoreUtil.copy(obj, deep=deep, num=num)

    # new
    @staticmethod
    def id(
        n: int = LION_ID_CONFIG["n"],
        prefix: str | None = LION_ID_CONFIG["prefix"],
        postfix: str | None = None,
        random_hyphen: bool = LION_ID_CONFIG["random_hyphen"],
        num_hyphens: int | None = LION_ID_CONFIG["num_hyphens"],
        hyphen_start_index: int | None = LION_ID_CONFIG["hyphen_start_index"],
        hyphen_end_index: int | None = LION_ID_CONFIG["hyphen_end_index"],
    ) -> str:
        """
        Generate a unique identifier.

        Args:
            n: Length of the ID (excluding prefix and postfix).
            prefix: String to prepend to the ID.
            postfix: String to append to the ID.
            random_hyphen: If True, insert random hyphens into the ID.
            num_hyphens: Number of hyphens to insert if random_hyphen is True.
            hyphen_start_index: Start index for hyphen insertion.
            hyphen_end_index: End index for hyphen insertion.

        Returns:
            A unique identifier string.
        """
        return CoreUtil.id(
            n=n,
            prefix=prefix,
            postfix=postfix,
            random_hyphen=random_hyphen,
            num_hyphens=num_hyphens,
            hyphen_start_index=hyphen_start_index,
            hyphen_end_index=hyphen_end_index,
        )

    @staticmethod
    def get_id(item: Any, /, *, config: dict = LION_ID_CONFIG) -> str:
        """
        Get the Lion ID of an item.

        Args:
            item: The item to get the ID from.
            config: Configuration dictionary for ID validation.

        Returns:
            The Lion ID of the item.

        Raises:
            `LionIDError`: If the item does not contain a valid Lion ID.
        """
        return CoreUtil.get_id(item, config=config)

    @staticmethod
    def is_id(item: Any, /, *, config: dict = LION_ID_CONFIG) -> bool:
        """
        Check if an item is a valid Lion ID.

        Args:
            item: The item to check.
            config: Configuration dictionary for ID validation.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        return CoreUtil.is_id(item, config=config)

    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Get the CPU architecture.

        Returns:
            str: 'apple_silicon' if ARM-based, 'other_cpu' otherwise.
        """
        from .ln_import import ImportUtil

        return ImportUtil.get_cpu_architecture()

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ) -> None:
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
        from .ln_import import ImportUtil

        ImportUtil.install_import(
            package_name=package_name,
            module_name=module_name,
            import_name=import_name,
            pip_name=pip_name,
        )

    @staticmethod
    def import_module(module_path: str) -> Any:
        """
        Import a module by its path.

        Args:
            module_path: The path of the module to import.

        Returns:
            The imported module.

        Raises:
            `ImportError`: If the module cannot be imported.
        """
        from .ln_import import ImportUtil

        return ImportUtil.import_module(module_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        from .ln_import import ImportUtil

        return ImportUtil.is_package_installed(package_name)

    @staticmethod
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
        attempt_install: bool = True,
        error_message: str = "",
    ) -> None:
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
            `ImportError`: If the package is not found and not installed.
            `ValueError`: If the import fails after installation attempt.
        """
        from .ln_import import ImportUtil

        ImportUtil.check_import(
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
        from .ln_import import ImportUtil

        return ImportUtil.list_installed_packages()

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """
        Uninstall a specified package.

        Args:
            package_name: The name of the package to uninstall.

        Raises:
            `subprocess.CalledProcessError`: If the uninstallation fails.
        """
        from .ln_import import ImportUtil

        ImportUtil.uninstall_package(package_name)

    @staticmethod
    def update_package(package_name: str) -> None:
        """
        Update a specified package.

        Args:
            package_name: The name of the package to update.

        Raises:
            subprocess.CalledProcessError: If the update fails.
        """
        from .ln_import import ImportUtil

        ImportUtil.update_package(package_name)

    @staticmethod
    def clear_path(
        path: Path | str, /, recursive: bool = False, exclude: list[str] | None = None
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
        from .ln_filepath import FilePathUtil

        FilePathUtil.clear_path(path, recursive=recursive, exclude=exclude)

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        """
        Split a path into its directory and filename components.

        Args:
            path: The path to split.

        Returns:
            A tuple containing the directory and filename.
        """
        from .ln_filepath import FilePathUtil

        return FilePathUtil.split_path(path)

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
        from .ln_filepath import FilePathUtil

        FilePathUtil.copy_file(src, dest)

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
        from .ln_filepath import FilePathUtil

        return FilePathUtil.get_file_size(path)

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
        from .ln_filepath import FilePathUtil

        return FilePathUtil.save_to_file(
            text,
            directory,
            filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
            timestamp_format=timestamp_format,
            random_hash_digits=random_hash_digits,
            verbose=verbose,
        )

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
        return CoreUtil.create_path(
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
        List all files in a specified directory with an optional extension filter.

        Args:
            dir_path: The directory path where files are listed.
            extension: Filter files by extension.

        Returns:
            A list of Path objects representing files in the directory.

        Raises:
            NotADirectoryError: If the provided dir_path is not a directory.
        """
        from .ln_filepath import FilePathUtil

        return FilePathUtil.list_files(dir_path, extension=extension)

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
        from .ln_filepath import FilePathUtil

        FilePathUtil.copy_file(src, dest)

    @staticmethod
    def get_bins(input_: list[str], upper: int | None = 2000) -> list[list[int]]:
        """
        Organizes indices of strings into bins based on a cumulative upper limit.

        Args:
            input_ (List[str]): The list of strings to be binned.
            upper (int): The cumulative length upper limit for each bin.

        Returns:
            List[List[int]]: A list of bins, each bin is a list of indices from the input list.
        """
        from .ln_tokenize import TokenizeUtil

        return TokenizeUtil.get_bins(input_, upper=upper)

    ## Deprecated methods

    @deprecated
    @staticmethod
    def get_size(path: Path | str) -> int:
        """
        Gets the size of a file or total size of files in a directory.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.get_file_size` instead. Will be removed in v1.0.0.

        Args:
            path (Path | str): The file or directory path.

        Returns:
            int: The size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        warnings.warn(
            "get_size is deprecated since v0.2.3 and will be removed in v1.0.0. Use SysUtil.get_file_size() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        path = Path(path)
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
        else:
            raise FileNotFoundError(f"{path} does not exist.")

    @deprecated
    @staticmethod
    def sleep(delay: float) -> None:
        """
        Pauses execution for a specified duration.

        .. deprecated:: 0.2.3
           Use `time.sleep()` from the standard library instead. Will be removed in v1.0.0.

        Args:
            delay (float): The amount of time, in seconds, to pause execution.
        """
        warnings.warn(
            "sleep is deprecated since v0.2.3 and will be removed in v1.0.0. Use time.sleep() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        time.sleep(delay)

    @deprecated
    @staticmethod
    def get_now(datetime_: bool = False, tz=None) -> float | datetime:
        """
        Returns the current time either as a Unix timestamp or a datetime object.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.time` instead. Will be removed in v1.0.0.

        Args:
            datetime_ (bool): If True, returns a datetime object; otherwise, returns a Unix timestamp.

        Returns:
            Union[float, datetime.datetime]: The current time as a Unix timestamp or a datetime object.
        """
        warnings.warn(
            "get_now is deprecated since v0.2.3 and will be removed in v1.0.0. Use SysUtil.time() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        if not datetime_:
            return time.time()
        config_ = {}
        if tz:
            config_["tz"] = tz if isinstance(tz, timezone) else timezone.utc
        return datetime.now(**config_)

    @deprecated
    @staticmethod
    def change_dict_key(dict_: dict[Any, Any], old_key: str, new_key: str) -> None:
        """
        Safely changes a key in a dictionary if the old key exists.

        .. deprecated:: 0.2.3
           Use `dict[new_key] = dict.pop(old_key)` instead. Will be removed in v1.0.0.

        Args:
            dict_ (Dict[Any, Any]): The dictionary in which to change the key.
            old_key (str): The old key to be changed.
            new_key (str): The new key to replace the old key.

        Returns:
            None
        """
        warnings.warn(
            "change_dict_key is deprecated since v0.2.3 and will be removed in v1.0.0. Use dict[new_key] = dict.pop(old_key) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @deprecated
    @staticmethod
    def get_timestamp(tz: timezone = timezone.utc, sep: str = "_") -> str:
        """
        Returns a timestamp string with optional custom separators and timezone.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.time` instead. Will be removed in v1.0.0.

        Args:
            tz (timezone): The timezone for the timestamp.
            sep (str): The separator to use in the timestamp string, replacing '-', ':', and '.'.

        Returns:
            str: A string representation of the current timestamp.
        """
        warnings.warn(
            "get_timestamp is deprecated since v0.2.3 and will be removed in v1.0.0. Use SysUtil.time() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        str_ = datetime.now(tz=tz).isoformat()
        if sep is not None:
            for sym in _timestamp_syms:
                str_ = str_.replace(sym, sep)
        return str_

    @deprecated
    @staticmethod
    def is_schema(dict_: dict[Any, Any], schema: dict[Any, type]) -> bool:
        """
        Validates if the given dictionary matches the expected schema types.

        .. deprecated:: 0.2.3
           This method will be removed without replacement in v1.0.0.

        Args:
            dict_ (Dict[Any, Any]): The dictionary to validate.
            schema (Dict[Any, type]): The expected schema types.

        Returns:
            bool: True if the dictionary matches the schema, False otherwise.
        """
        warnings.warn(
            "is_schema is deprecated since v0.2.3 and will be removed in v1.0.0 without replacement.",
            DeprecationWarning,
            stacklevel=2,
        )
        return all(
            isinstance(dict_.get(key), expected_type)
            for key, expected_type in schema.items()
        )

    @deprecated
    @staticmethod
    def create_copy(input_: Any, num: int = 1) -> Any | list[Any]:
        """
        Creates deep copies of the input, either as a single copy or a list of copies.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.copy` instead. Will be removed in v1.0.0.

        Args:
            input_ (Any): The input to be copied.
            num (int): The number of copies to create.

        Returns:
            Union[Any, List[Any]]: A single copy of the input or a list of deep copies.

        Raises:
            ValueError: If num is less than 1.
        """
        if num < 1:
            raise ValueError(f"'num' must be a positive integer: {num}")
        return (
            copy.deepcopy(input_)
            if num == 1
            else [copy.deepcopy(input_) for _ in range(num)]
        )

    @deprecated
    @staticmethod
    def create_id(n: int = 32) -> str:
        """
        Generates a unique identifier based on the current time and random bytes.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.id` instead. Will be removed in v1.0.0.

        Args:
            n (int): The length of the generated identifier.

        Returns:
            str: A unique identifier string.
        """
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @deprecated
    @staticmethod
    def clear_dir(
        dir_path: Path | str, recursive: bool = False, exclude: list[str] = None
    ) -> None:
        """
        Clears all files (and, if recursive, directories) in the specified directory,
        excluding files that match any pattern in the exclude list.

        .. deprecated:: 0.2.3
           Use :func:`SysUtil.clear_path` instead. Will be removed in v1.0.0.

        Args:
            dir_path (Union[Path, str]): The path to the directory to clear.
            recursive (bool): If True, clears directories recursively. Defaults to False.
            exclude (List[str]): A list of string patterns to exclude from deletion. Defaults to None.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        warnings.warn(
            "clear_dir is deprecated since v0.2.3 and will be removed in v1.0.0. Use SysUtil.clear_path() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
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


# File: lionagi/libs/sys_util.py
