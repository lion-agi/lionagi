"""Utility functions for system operations in the Lion framework."""

import os
import importlib
import importlib.util
import importlib.metadata
import logging
import platform
import re
import subprocess
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2
from typing import Any, Literal, Sequence, TypeVar

from lion_core.abc import Observable
from lion_core.sys_utils import SysUtil as _sys
import pkg_resources
import requests
from lionagi.os import lionfuncs as ln
from lionagi.os.sys_config import TIME_CONFIG


T = TypeVar("T")
PATH_TYPE = str | Path
TIME_TYPES = Literal["timestamp", "datetime", "iso", "custom"]


class SysUtil:
    """Utility class for system operations in the Lion framework."""

    @staticmethod
    def time(
        *,
        tz: timezone = TIME_CONFIG["tz"],
        type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
        sep: str | None = "T",
        timespec: str | None = "auto",
        custom_format: str | None = None,
        custom_sep: str | None = None,
    ) -> float | str | datetime:
        """Get current time in various formats.

        Args:
            tz: Timezone for the time.
            type_:
            Type of time to return.
            sep: Separator for ISO format.
            timespec: Timespec for ISO format.
            custom_format: Custom strftime format string.
            custom_sep: Custom separator for type_="custom".

        Returns:
            Current time in the specified format.

        Raises:
            ValueError: If invalid type_ or missing custom_format.
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
        """Create one or more copies of an object.

        Args:
            obj: The object to be copied.
            deep: If True, create a deep copy.
            num: The number of copies to create.

        Returns:
            A single copy if num is 1, otherwise a list of copies.

        Raises:
            ValueError: If num is less than 1.
        """
        return _sys.copy(obj, deep=deep, num=num)

    @staticmethod
    def id() -> str:
        """Generate a unique identifier."""
        return _sys.id()

    @staticmethod
    def get_id(item: Observable | str, /) -> str:
        """Get the Lion ID of an item.

        Args:
            item: The item to get the ID from.

        Returns:
            The Lion ID of the item.

        Raises:
            LionIDError: If the item does not contain a valid Lion ID.
        """
        return _sys.get_id(item)

    @staticmethod
    def is_id(item: Observable | str, /) -> bool:
        """Check if an item is a valid Lion ID.

        Args:
            item: The item to check.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        return _sys.is_id(item)

    @staticmethod
    def clear_path(
        path: Path | str, /, recursive: bool = False, exclude: list[str] | None = None
    ) -> None:
        """Clear files in the specified directory.

        Args:
            path: The path to the directory to clear.
            recursive: If True, clears directories recursively.
            exclude: A list of string patterns to exclude from deletion.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If there are insufficient permissions.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Directory {path} does not exist.")

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            try:
                if recursive and file_path.is_dir():
                    SysUtil.clear_path(file_path, recursive=True, exclude=exclude)
                elif file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
                    logging.info(f"Successfully deleted {file_path}")
            except PermissionError as e:
                logging.error(f"Permission denied: {file_path}: {e}")
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {e}")

    @staticmethod
    def create_path(
        path: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        file_exist_ok: bool = False,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
    ) -> Path:
        """Generate a new file path with optional timestamp and random hash.

        Args:
            directory: The directory where the file will be created.
            filename: The base name of the file to create.
            timestamp: If True, adds a timestamp to the filename.
            dir_exist_ok: If True, doesn't raise an error if dir exists.
            file_exist_ok: If True, allows overwriting of existing files.
            time_prefix: If True, adds timestamp as prefix instead of suffix.
            timestamp_format: Custom format for the timestamp.
            random_hash_digits: Number of digits for the random hash.

        Returns:
            The full path to the new or existing file.

        Raises:
            ValueError: If the filename contains illegal characters.
            FileExistsError: If file exists and file_exist_ok is False.
        """
        path = Path(path)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError("Invalid filename. Ensure valid extension.")

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
            "-" + ln.unique_hash(random_hash_digits) if random_hash_digits > 0 else ""
        )

        full_filename = f"{filename}{random_hash}{ext}"
        full_path = path / full_filename

        if not file_exist_ok:
            counter = 1
            while full_path.exists():
                new_filename = f"{filename}_{counter}{random_hash}{ext}"
                full_path = path / new_filename
                counter += 1
        elif full_path.exists():
            logging.warning(f"File {full_path} exists. Using existing file.")

        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    def _get_path_kwargs(
        persist_path: Path | str, postfix: str, **path_kwargs: Any
    ) -> dict[str, Any]:
        """Get path kwargs for file operations.

        Args:
            persist_path: The path to persist the file.
            postfix: The postfix to add to the filename.
            **path_kwargs: Additional keyword arguments for create_path.

        Returns:
            A dictionary of path kwargs.
        """
        dirname, filename = None, None

        postfix = f".{postfix.strip().strip('.')}"

        if postfix not in (_path := str(persist_path)):
            dirname = _path
            filename = f"new_file.{postfix}"
        else:
            dirname, filename = SysUtil.split_path(persist_path)

        path_kwargs["timestamp"] = path_kwargs.get("timestamp", False)
        path_kwargs["file_exist_ok"] = path_kwargs.get("file_exist_ok", True)
        path_kwargs["directory"] = path_kwargs.get("directory", dirname)
        path_kwargs["filename"] = path_kwargs.get("filename", filename)

        return path_kwargs

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        """Split a path into its directory and filename components.

        Args:
            path: The path to split.

        Returns:
            A tuple containing the directory and filename.
        """
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def list_files(
        dir_path: Path | str, extension: str | None = None, recursive: bool = False
    ) -> list[Path]:
        """List files in a specified directory, optionally recursively.

        Args:
            dir_path: The directory path where files are listed.
            extension: Filter files by extension.
            recursive: If True, search for files recursively in subdirectories

        Returns:
            A list of Path objects representing files in the directory.

        Raises:
            NotADirectoryError: If the provided dir_path is not a directory.
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")

        glob_pattern = "**/*" if recursive else "*"
        if extension:
            glob_pattern += f".{extension}"

        return [f for f in dir_path.glob(glob_pattern) if f.is_file() or f.is_symlink()]

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str, overwrite: bool = False) -> None:
        """Copy a file from a source path to a destination path.

        Args:
            src: The source file path.
            dest: The destination file path.
            overwrite: If True, overwrite the destination file if it exists.

        Raises:
            FileNotFoundError: If the source file does not exist.
            FileExistsError: If destination exists and overwrite is False.
            PermissionError: If there are insufficient permissions.
            OSError: If there's an OS-level error during the copy operation.
        """
        src_path, dest_path = Path(src), Path(dest)
        if not src_path.is_file():
            raise FileNotFoundError(f"{src_path} does not exist or is not a file.")
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"{dest_path} already exists.")

        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            copy2(src_path, dest_path)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied: {src_path} to {dest_path}"
            ) from e
        except OSError as e:
            raise OSError(f"Failed to copy {src_path} to {dest_path}: {e}") from e

    @staticmethod
    def move_file(src: Path | str, dest: Path | str, overwrite: bool = False) -> None:
        """Move a file from a source path to a destination path.

        Args:
            src: The source file path.
            dest: The destination file path.
            overwrite: If True, overwrite the destination file if it exists.

        Raises:
            FileNotFoundError: If the source file does not exist.
            FileExistsError: If destination exists and overwrite is False.
            PermissionError: If there are insufficient permissions.
            OSError: If there's an OS-level error during the move operation.
        """
        src_path, dest_path = Path(src), Path(dest)
        if not src_path.is_file():
            raise FileNotFoundError(f"{src_path} does not exist or is not a file.")
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"{dest_path} already exists.")

        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            src_path.rename(dest_path)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied: {src_path} to {dest_path}"
            ) from e
        except OSError as e:
            # If moving across filesystems fails, try copy and delete
            try:
                copy2(src_path, dest_path)
                src_path.unlink()
            except OSError as copy_error:
                raise OSError(
                    f"Failed to move {src_path} to {dest_path}: {copy_error}"
                ) from e

    @staticmethod
    def get_file_info(path: Path | str) -> dict[str, int | str]:
        """Get detailed information about a file or directory.

        Args:
            path: The file or directory path.

        Returns:
            A dictionary containing size, type, and other relevant information.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If there are insufficient permissions.
        """
        path = Path(path)
        try:
            if not path.exists():
                raise FileNotFoundError(f"{path} does not exist.")

            info = {
                "type": "file" if path.is_file() else "directory",
                "size": (
                    path.stat().st_size
                    if path.is_file()
                    else sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                ),
                "last_modified": path.stat().st_mtime,
                "permissions": oct(path.stat().st_mode)[-3:],
            }

            if path.is_file():
                info["md5"] = SysUtil.calculate_md5(path)

            return info
        except PermissionError as e:
            raise PermissionError(f"Permission denied when accessing {path}") from e

    @staticmethod
    def calculate_md5(file_path: Path | str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def get_file_size(path: Path | str) -> int:
        """Get the size of a file or total size of files in a directory.

        Args:
            path: The file or directory path.

        Returns:
            The size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If there are insufficient permissions.
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
        content: str | bytes,
        directory: Path | str,
        filename: str,
        mode: str = "w",
        encoding: str | None = "utf-8",
        **kwargs,
    ) -> Path:
        """Save content to a file within a specified directory.

        Args:
            content: The content to save (string or bytes).
            directory: The directory path to save the file.
            filename: The filename for the saved content.
            mode: The mode to open the file ('w' for text, 'wb' for binary).
            encoding: The encoding to use (None for binary mode).
            **kwargs: Additional arguments for create_path method.

        Returns:
            Path object of the saved file.

        Raises:
            OSError: If there's an error creating the directory or writing.
        """
        try:
            file_path = SysUtil.create_path(path=directory, filename=filename, **kwargs)

            write_args = (
                {"mode": mode, "encoding": encoding} if encoding else {"mode": mode}
            )
            with open(file_path, **write_args) as file:
                file.write(content)

            logging.info(f"Content saved to: {file_path}")
            return file_path
        except OSError as e:
            logging.error(f"Failed to save file {filename}: {e}")
            raise

    @staticmethod
    def read_file(
        path: Path | str, mode: str = "r", encoding: str | None = "utf-8"
    ) -> str | bytes:
        """Read the contents of a file.

        Args:
            path: The path to the file to read.
            mode: The mode to open the file ('r' for text, 'rb' for binary).
            encoding: The encoding to use (None for binary mode).

        Returns:
            The contents of the file as a string or bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If there are insufficient permissions.
        """
        try:
            read_args = (
                {"mode": mode, "encoding": encoding} if encoding else {"mode": mode}
            )
            with open(path, **read_args) as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except PermissionError:
            raise PermissionError(f"Permission denied when accessing {path}")

    @staticmethod
    def get_cpu_architecture() -> dict[str, Any]:
        """Get detailed CPU architecture information.

        Returns:
            A dictionary containing various CPU architecture details.
        """
        arch_info = {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "system": platform.system(),
            "python_bits": platform.architecture()[0],
        }

        if platform.system() == "Darwin":  # macOS
            arch_info.update(SysUtil._get_macos_cpu_info())
        elif platform.system() == "Linux":
            arch_info.update(SysUtil._get_linux_cpu_info())
        elif platform.system() == "Windows":
            arch_info.update(SysUtil._get_windows_cpu_info())

        # Determine if it's ARM-based
        arch_info["is_arm"] = (
            "arm" in arch_info["machine"].lower()
            or "aarch64" in arch_info["machine"].lower()
        )

        return arch_info

    @staticmethod
    def _get_macos_cpu_info() -> dict[str, str]:
        """Get macOS-specific CPU information."""
        try:
            output = (
                subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"])
                .decode()
                .strip()
            )
            vendor = (
                subprocess.check_output(["sysctl", "-n", "machdep.cpu.vendor"])
                .decode()
                .strip()
            )
            cores = (
                subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"])
                .decode()
                .strip()
            )
            model = (
                subprocess.check_output(["sysctl", "-n", "machdep.cpu.model"])
                .decode()
                .strip()
            )
            return {
                "brand": output,
                "vendor": vendor,
                "physical_cores": cores,
                "model": model,
            }
        except subprocess.CalledProcessError:
            return {"error": "Failed to retrieve macOS CPU info"}

    @staticmethod
    def _get_linux_cpu_info() -> dict[str, str]:
        """Get Linux-specific CPU information."""
        info = {}
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        info["brand"] = line.split(":")[1].strip()
                        break
            info["physical_cores"] = os.cpu_count()
            return info
        except FileNotFoundError:
            return {"error": "Failed to retrieve Linux CPU info"}

    @staticmethod
    def _get_windows_cpu_info() -> dict[str, str]:
        """Get Windows-specific CPU information."""
        try:
            output = subprocess.check_output(
                ["wmic", "cpu", "get", "name", "/format:list"]
            ).decode()
            brand = output.strip().split("=")[1]
            cores = os.cpu_count()
            return {"brand": brand, "physical_cores": str(cores)}
        except subprocess.CalledProcessError:
            return {"error": "Failed to retrieve Windows CPU info"}

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Check if a package is installed.

        Args:
            package_name: Name of the package to check.

        Returns:
            True if the package is installed, False otherwise.
        """
        return importlib.util.find_spec(package_name) is not None

    @staticmethod
    def import_module(
        package_name: str,
        module_name: str | None = None,
        import_name: str | list[str] | None = None,
    ) -> Any:
        """Import a module by its path.

        Args:
            package_name: Name of the package containing the module.
            module_name: Name of the specific module to import.
            import_name: Name or list of names to import from the module.

        Returns:
            The imported module, function, or a list of imported objects.

        Raises:
            ImportError: If the module or specified names cannot be imported.
        """
        try:
            full_import_path = (
                f"{package_name}.{module_name}" if module_name else package_name
            )

            if import_name:
                import_names = (
                    [import_name] if isinstance(import_name, str) else import_name
                )
                module = __import__(full_import_path, fromlist=import_names)
                if len(import_names) == 1:
                    return getattr(module, import_names[0])
                return [getattr(module, name) for name in import_names]
            else:
                return __import__(full_import_path)

        except ImportError as e:
            raise ImportError(f"Failed to import module {full_import_path}: {e}") from e

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | list[str] | None = None,
        pip_name: str | None = None,
        version: str | None = None,
        upgrade: bool = False,
        extras: list[str] | None = None,
        constraint_file: str | None = None,
        editable: bool = False,
    ) -> Any:
        """Attempt to import a package, installing it if not found.

        Args:
            package_name: Name of the package to import.
            module_name: Specific module to import from the package.
            import_name: Specific name or list of names to import from the module.
            pip_name: Alternative name for pip installation.
            version: Specific version to install (e.g., '==1.2.3', '>=1.0,<2.0').
            upgrade: Whether to upgrade an existing installation.
            extras: List of extras to include in the installation.
            constraint_file: Path to a pip constraints file.
            editable: Whether to install in editable mode.

        Returns:
            The imported module or object.

        Raises:
            ImportError: If the package cannot be imported or installed.
            subprocess.CalledProcessError: If pip installation fails.
        """
        pip_name = pip_name or package_name
        install_name = f"{pip_name}[{','.join(extras)}]" if extras else pip_name
        if version:
            install_name += f"{version}"

        try:
            if upgrade and SysUtil.is_package_installed(package_name):
                SysUtil.update_package(install_name)
            elif not SysUtil.is_package_installed(package_name):
                install_args = ["install"]
                if editable:
                    install_args.append("-e")
                if constraint_file:
                    install_args.extend(["-c", constraint_file])
                install_args.append(install_name)
                _run_pip_command(install_args)

            return SysUtil.import_module(
                package_name=package_name,
                module_name=module_name,
                import_name=import_name,
            )
        except ImportError:
            logging.error(f"Failed to import {package_name} after installation.")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install {install_name}: {e}")
            raise ImportError(f"Failed to install {install_name}: {e}") from e

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """Uninstall a specified package.

        Args:
            package_name: Name of the package to uninstall.

        Raises:
            subprocess.CalledProcessError: If the uninstallation fails.
        """
        try:
            _run_pip_command(["uninstall", package_name, "-y"])
            logging.info(f"Successfully uninstalled {package_name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to uninstall {package_name}. Error: {e}")
            raise

    @staticmethod
    def check_package_version(
        package_name: str,
        version_spec: str,
    ) -> tuple[bool, str | None]:
        """Check if the installed package version meets the specification.

        Args:
            package_name: Name of the package to check.
            version_spec: Version specification (e.g., '>=1.2,<2.0').

        Returns:
            A tuple containing:
            - A boolean indicating if the installed version meets the specification.
            - The installed version as a string, or None if not installed.

        Raises:
            pkg_resources.DistributionNotFound: If the package is not installed.
        """
        try:
            installed_version = pkg_resources.get_distribution(package_name).version
            spec = pkg_resources.Requirement.parse(f"{package_name}{version_spec}")
            return installed_version in spec, installed_version
        except pkg_resources.DistributionNotFound:
            return False, None

    @staticmethod
    def list_installed_packages(include_version: bool = False) -> list[str]:
        """List all installed packages.

        Args:
            include_version: Whether to include version information.

        Returns:
            A list of installed package names, optionally with versions.

        Raises:
            RuntimeError: If there's an error accessing package information.
        """
        try:
            if include_version:
                return [
                    f"{dist.metadata['Name']}=={dist.version}"
                    for dist in importlib.metadata.distributions()
                ]
            else:
                return [
                    dist.metadata["Name"] for dist in importlib.metadata.distributions()
                ]
        except Exception as e:
            logging.error(f"Failed to list installed packages: {e}")
            raise RuntimeError(f"Error listing installed packages: {e}") from e

    @staticmethod
    def install_from_github(
        repo_url: str,
        branch: str | None = None,
        editable: bool = False,
        extras: list[str] | None = None,
        subdirectory: str | None = None,
    ) -> None:
        """Install a package from a GitHub repository.

        Args:
            repo_url: URL of the GitHub repository.
            branch: Specific branch to install from. If None, uses the default branch.
            editable: Whether to install in editable mode.
            extras: List of extras to install.
            subdirectory: Subdirectory containing the package, if any.

        Raises:
            ValueError: If the repository or branch doesn't exist.
            subprocess.CalledProcessError: If pip installation fails.
        """
        # Normalize the repo URL
        if not repo_url.startswith(("http://", "https://")):
            repo_url = f"https://github.com/{repo_url}"

        # Check if the repository exists
        response = requests.get(repo_url)
        if response.status_code != 200:
            raise ValueError(f"Repository not found: {repo_url}")

        # Construct the installation URL
        install_url = repo_url
        if branch:
            # Check if the branch exists
            branch_url = f"{repo_url}/tree/{branch}"
            response = requests.get(branch_url)
            if response.status_code != 200:
                raise ValueError(f"Branch not found: {branch}")
            install_url += f"@{branch}"

        if subdirectory:
            install_url += f"/{subdirectory}"

        if extras:
            install_url += f"[{','.join(extras)}]"

        # Prepare pip command
        pip_args = ["install"]
        if editable:
            pip_args.append("-e")
        pip_args.append(f"git+{install_url}")

        try:
            _run_pip_command(pip_args)
            logging.info(f"Successfully installed package from {install_url}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install package from GitHub: {e}")
            raise

    @staticmethod
    def check_github_branch(repo_url: str, branch: str) -> bool:
        """Check if a specific branch exists in a GitHub repository.

        Args:
            repo_url: URL of the GitHub repository.
            branch: Name of the branch to check.

        Returns:
            True if the branch exists, False otherwise.

        Raises:
            ValueError: If the repository doesn't exist.
        """
        if not repo_url.startswith(("http://", "https://")):
            repo_url = f"https://github.com/{repo_url}"

        # Check if the repository exists
        response = requests.get(repo_url)
        if response.status_code != 200:
            raise ValueError(f"Repository not found: {repo_url}")

        # Check if the branch exists
        branch_url = f"{repo_url}/tree/{branch}"
        response = requests.get(branch_url)
        return response.status_code == 200

    @staticmethod
    def list_github_branches(repo_url: str) -> list[str]:
        """List all branches of a GitHub repository.

        Args:
            repo_url: URL of the GitHub repository.

        Returns:
            A list of branch names.

        Raises:
            ValueError: If the repository doesn't exist or API request fails.
        """
        if not repo_url.startswith(("http://", "https://")):
            repo_url = f"https://github.com/{repo_url}"

        # Extract owner and repo name from URL
        parts = repo_url.split("/")
        owner, repo = parts[-2], parts[-1]

        # Use GitHub API to get branches
        api_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
        response = requests.get(api_url)

        if response.status_code != 200:
            raise ValueError(f"Failed to fetch branches: {response.status_code}")

        branches = response.json()
        return [branch["name"] for branch in branches]


def _run_pip_command(args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """Run a pip command.

    Args:
        args: The arguments to pass to pip.

    Returns:
        The completed process object.

    Raises:
        subprocess.CalledProcessError: If the pip command fails.
    """
    return subprocess.run(
        [sys.executable, "-m", "pip"] + list(args),
        check=True,
        capture_output=True,
    )


__all__ = ["SysUtil"]
