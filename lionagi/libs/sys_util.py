import copy
import importlib
import logging
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List


_timestamp_syms = ['-', ':', '.']

class SysUtil:

    @staticmethod
    def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
        """Safely changes a key in a dictionary if the old key exists."""
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @staticmethod
    def get_timestamp(tz=timezone.utc, sep: str = "_") -> str:
        """
        Returns a timestamp string with optional custom separators and timezone.
        """
        str_ = datetime.now(tz=tz).isoformat()
        if sep is not None:
            for sym in _timestamp_syms:
                str_ = str_.replace(sym, sep)
        return str_

    @staticmethod
    def is_schema(dict_: Dict[Any, Any], schema: Dict[Any, type]) -> bool:
        """Validates if the given dictionary matches the expected schema types."""
        return all(
            isinstance(dict_.get(key), expected_type)
            for key, expected_type in schema.items()
        )

    @staticmethod
    def create_copy(input_: Any, num: int = 1) -> Any | List[Any]:
        """Creates deep copies of the input, either as a single copy or a list of copies."""
        if num < 1:
            raise ValueError(f"'num' must be a positive integer: {num}")
        return (
            copy.deepcopy(input_)
            if num == 1
            else [copy.deepcopy(input_) for _ in range(num)]
        )

    @staticmethod
    def create_id(n: int = 32) -> str:
        """Generates a unique identifier based on the current time and random bytes."""
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @staticmethod
    def get_bins(input_: List[str], upper: Any = 2000) -> List[List[int]]:
        """Organizes indices of strings into bins based on a cumulative upper limit."""
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
    def get_cpu_architecture() -> str:
        arch: str = platform.machine().lower()
        if "arm" in arch or "aarch64" in arch:
            return "apple_silicon"
        return "other_cpu"

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ) -> None:
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        package_spec = importlib.util.find_spec(package_name)
        return package_spec is not None

    @staticmethod
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ) -> None:
        try:
            if not SysUtil.is_package_installed(package_name):
                logging.info(
                    f"Package {package_name} not found. Attempting to install."
                )
                SysUtil.install_import(
                    package_name, module_name, import_name, pip_name
                )
        except ImportError as e:  # More specific exception handling
            logging.error(f"Failed to import {package_name}. Error: {e}")
            raise ValueError(f"Failed to import {package_name}. Error: {e}") from e

    @staticmethod
    def list_installed_packages() -> list:
        """List all installed packages using importlib.metadata."""
        return [dist.metadata["Name"] for dist in importlib.metadata.distributions()]

    @staticmethod
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
    def update_package(package_name: str) -> None:
        """Update a specified package."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
            )
            print(f"Successfully updated {package_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {package_name}. Error: {e}")

    @staticmethod
    def clear_dir(
        dir_path: Path | str, recursive: bool = False, exclude: list[str] = None
    ) -> None:
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
    def split_path(path: Path | str) -> tuple[Path, str]:
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def create_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        custom_timestamp_format: str | None = None,
    ) -> Path:
        directory = Path(directory)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError(
                "Invalid filename. Ensure it doesn't contain illegal characters and has a valid extension."
            )

        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        ext = f".{ext}" if ext else ""

        timestamp_str = ""
        if timestamp:
            from datetime import datetime

            timestamp_format = custom_timestamp_format or "%Y%m%d%H%M%S"
            timestamp_str = datetime.now().strftime(timestamp_format)
            filename = (
                f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
            )
        else:
            filename = name

        full_filename = f"{filename}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    def list_files(dir_path: Path | str, extension: str = None) -> list[Path]:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")
        if extension:
            return list(dir_path.glob(f"*.{extension}"))
        else:
            return list(dir_path.glob("*"))

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str) -> None:
        src, dest = Path(src), Path(dest)
        if not src.is_file():
            raise FileNotFoundError(f"{src} does not exist or is not a file.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(src, dest)

    @staticmethod
    def get_size(path: Path | str) -> int:
        path = Path(path)
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
        else:
            raise FileNotFoundError(f"{path} does not exist.")
