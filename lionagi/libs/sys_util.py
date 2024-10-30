import copy
import importlib
import logging
import os
import platform
import re
import subprocess
import sys
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from lion_core.setting import DEFAULT_LION_ID_CONFIG, LionIDConfig
from lion_core.sys_utils import SysUtil as _u
from lionabc import Observable
from typing_extensions import deprecated

_timestamp_syms = ["-", ":", "."]

PATH_TYPE = str | Path


class SysUtil:

    @staticmethod
    def id(
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        n: int = None,
        prefix: str = None,
        postfix: str = None,
        random_hyphen: bool = None,
        num_hyphens: int = None,
        hyphen_start_index: int = None,
        hyphen_end_index: int = None,
    ) -> str:
        return _u.id(
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
        return _u.get_id(item, config)

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> bool:
        return _u.is_id(item, config)

    # legacy methods, kept for backward compatibility

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use time.sleep instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def sleep(delay: float) -> None:
        """
        Pauses execution for a specified duration.

        Args:
            delay (float): The amount of time, in seconds, to pause execution.
        """
        time.sleep(delay)

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.time instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use d_[k2] = d_.pop(k1) instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def change_dict_key(
        dict_: dict[Any, Any], old_key: str, new_key: str
    ) -> None:
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.time instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
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
            for sym in _timestamp_syms:
                str_ = str_.replace(sym, sep)
        return str_

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Deprecated without replacement",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def is_schema(dict_: dict[Any, Any], schema: dict[Any, type]) -> bool:
        """Validates if the given dictionary matches the expected schema types."""
        return all(
            isinstance(dict_.get(key), expected_type)
            for key, expected_type in schema.items()
        )

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.copy instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use SysUtil.id instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.get_bins instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def get_bins(
        input_: list[str], upper: int | None = 2000
    ) -> list[list[int]]:
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.get_cpu_architecture instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def get_cpu_architecture() -> str:
        """Returns a string identifying the CPU architecture.

        This method categorizes some architectures as 'apple_silicon'.

        Returns:
            str: A string identifying the CPU architecture ('apple_silicon' or 'other_cpu').
        """
        arch: str = platform.machine().lower()
        return (
            "apple_silicon"
            if "arm" in arch or "aarch64" in arch
            else "other_cpu"
        )

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.install_import instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def install_import(
        package_name: str,
        module_name: str = None,
        import_name: str = None,
        pip_name: str = None,
    ) -> None:
        """Attempts to import a package, installing it with pip if not found.

        This method tries to import a specified module or attribute. If the import fails, it attempts
        to install the package using pip and then retries the import.

        Args:
            package_name: The base name of the package to import.
            module_name: The submodule name to import from the package, if applicable. Defaults to None.
            import_name: The specific name to import from the module or package. Defaults to None.
            pip_name: The pip package name if different from `package_name`. Defaults to None.

        Prints a message indicating success or attempts installation if the import fails.
        """
        pip_name: str = pip_name or package_name
        full_import_path: str = (
            f"{package_name}.{module_name}" if module_name else package_name
        )

        try:
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)
            print(f"Successfully imported {import_name or full_import_path}.")
        except ImportError:
            print(
                f"Module {full_import_path} or attribute {import_name} not found. Installing {pip_name}..."
            )
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name]
            )

            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.import_module instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def import_module(module_path: str):
        return importlib.import_module(module_path)

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.is_package_installed instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def is_package_installed(package_name: str) -> bool:
        """Checks if a package is currently installed.

        Args:
            package_name: The name of the package to check.

        Returns:
            A boolean indicating whether the package is installed.
        """
        package_spec = importlib.util.find_spec(package_name)
        return package_spec is not None

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.check_import instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
        attempt_install: bool = True,
        error_message: str = "",
    ) -> None:
        """Checks if a package is installed; if not, attempts to install and import it.

        This method first checks if a package is installed using `is_package_installed`. If not found,
        it attempts to install the package using `install_import` and then retries the import.

        Args:
            package_name: The name of the package to check and potentially install.
            module_name: The submodule name to import from the package, if applicable. Defaults to None.
            import_name: The specific name to import from the module or package. Defaults to None.
            pip_name: The pip package name if different from `package_name`. Defaults to None.
            attempt_install: If attempt to install the package if uninstalled. Defaults to True.
            error_message: Error message when the package is not installed and not attempt to install.
        """
        try:
            if not SysUtil.is_package_installed(package_name):
                # print("check")
                if attempt_install:
                    logging.info(
                        f"Package {package_name} not found. Attempting to install."
                    )
                    SysUtil.install_import(
                        package_name, module_name, import_name, pip_name
                    )
                else:
                    logging.info(
                        f"Package {package_name} not found. {error_message}"
                    )
                    raise ImportError(
                        f"Package {package_name} not found. {error_message}"
                    )
        except ImportError as e:  # More specific exception handling
            logging.error(f"Failed to import {package_name}. Error: {e}")
            raise ValueError(
                f"Failed to import {package_name}. Error: {e}"
            ) from e

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.list_installed_packages instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def list_installed_packages() -> list:
        """list all installed packages using importlib.metadata."""
        return [
            dist.metadata["Name"]
            for dist in importlib.metadata.distributions()
        ]

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.uninstall_package instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def uninstall_package(package_name: str) -> None:
        """Uninstall a specified package."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "uninstall", package_name, "-y"]
            )
            print(f"Successfully uninstalled {package_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to uninstall {package_name}. Error: {e}")

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.update_package instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def update_package(package_name: str) -> None:
        """Update a specified package."""
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    package_name,
                ]
            )
            print(f"Successfully updated {package_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {package_name}. Error: {e}")

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.clear_path instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def clear_dir(
        dir_path: Path | str,
        recursive: bool = False,
        exclude: list[str] = None,
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

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.split_path instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def split_path(path: Path | str) -> tuple[Path, str]:
        """
        Splits a path into its directory and filename components.

        Args:
                path (Union[Path, str]): The path to split.

        Returns:
                Tuple[Path, str]: A tuple containing the directory and filename.
        """
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.create_path instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def create_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        custom_timestamp_format: str | None = None,
        random_hash_digits=0,
    ) -> Path:
        """
        Creates a path with an optional timestamp in the specified directory.

        Args:
            directory (Union[Path, str]): The directory where the file will be located.
            filename (str): The filename. Must include a valid extension.
            timestamp (bool): If True, adds a timestamp to the filename. Defaults to True.
            dir_exist_ok (bool): If True, does not raise an error if the directory exists. Defaults to True.
            time_prefix (bool): If True, adds the timestamp as a prefix; otherwise, as a suffix. Defaults to False.
            custom_timestamp_format (str): A custom format for the timestamp. Defaults to "%Y%m%d%H%M%S".

        Returns:
                Path: The full path to the file.

        Raises:
                ValueError: If the filename is invalid.
        """
        directory = Path(directory)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError(
                "Invalid filename. Ensure it doesn't contain illegal characters and has a valid extension."
            )

        name, ext = (
            filename.rsplit(".", 1) if "." in filename else (filename, "")
        )
        ext = f".{ext}" if ext else ""

        timestamp_str = ""
        if timestamp:
            timestamp_format = custom_timestamp_format or "%Y%m%d%H%M%S"
            timestamp_str = datetime.now().strftime(timestamp_format)
            filename = (
                f"{timestamp_str}_{name}"
                if time_prefix
                else f"{name}_{timestamp_str}"
            )
        else:
            filename = name

        random_hash = (
            "-" + SysUtil.create_id(random_hash_digits)
            if random_hash_digits > 0
            else ""
        )

        full_filename = f"{filename}{random_hash}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.list_files instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def list_files(dir_path: Path | str, extension: str = None) -> list[Path]:
        """
        Lists all files in a specified directory with an optional filter for file extensions.

        Args:
            dir_path (Path | str): The directory path where files are listed.
            extension (str, optional): Filter files by extension. Default is None, which lists all files.

        Returns:
            list[Path]: A list of Path objects representing files in the directory.

        Raises:
            NotADirectoryError: If the provided dir_path is not a directory.
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")
        if extension:
            return list(dir_path.glob(f"*.{extension}"))
        else:
            return list(dir_path.glob("*"))

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.copy_file instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def copy_file(src: Path | str, dest: Path | str) -> None:
        """
        Copies a file from a source path to a destination path.

        Args:
            src (Path | str): The source file path.
            dest (Path | str): The destination file path.

        Raises:
            FileNotFoundError: If the source file does not exist or is not a file.
        """
        from shutil import copy2

        src, dest = Path(src), Path(dest)
        if not src.is_file():
            raise FileNotFoundError(f"{src} does not exist or is not a file.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(src, dest)

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.get_file_size instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
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
            return sum(
                f.stat().st_size for f in path.glob("**/*") if f.is_file()
            )
        else:
            raise FileNotFoundError(f"{path} does not exist.")

    @staticmethod
    @deprecated(
        "Deprecated since v0.3, will be removed in v1.0. Use lionfuncs.save_to_file instead",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def save_to_file(
        text,
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        custom_timestamp_format: str | None = None,
        random_hash_digits=0,
        verbose=True,
    ):
        """
        Saves text to a file within a specified directory, optionally adding a timestamp, hash, and verbose logging.

        Args:
            text (str): The text to save.
            directory (Path | str): The directory path to save the file.
            filename (str): The filename for the saved text.
            timestamp (bool): If True, append a timestamp to the filename. Default is True.
            dir_exist_ok (bool): If True, creates the directory if it does not exist. Default is True.
            time_prefix (bool): If True, prepend the timestamp instead of appending. Default is False.
            custom_timestamp_format (str | None): A custom format for the timestamp, if None uses default format. Default is None.
            random_hash_digits (int): Number of random hash digits to append to filename. Default is 0.
            verbose (bool): If True, prints the file path after saving. Default is True.

        Returns:
            bool: True if the text was successfully saved.
        """
        file_path = SysUtil.create_path(
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            dir_exist_ok=dir_exist_ok,
            time_prefix=time_prefix,
            custom_timestamp_format=custom_timestamp_format,
            random_hash_digits=random_hash_digits,
        )

        with open(file_path, "w") as file:
            file.write(text)

        if verbose:
            print(f"Text saved to: {file_path}")

        return True


__all__ = ["SysUtil"]
