from __future__ import annotations

import importlib
import importlib.util
import importlib.metadata
import logging
import platform
import subprocess
import sys
from functools import lru_cache
from typing import Any, List, Sequence


class ImportUtil:
    
    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Get the CPU architecture.

        Returns:
            str: 'apple_silicon' if ARM-based, 'other_cpu' otherwise.
        """
        arch: str = platform.machine().lower()
        return "apple_silicon" if "arm" in arch or "aarch64" in arch else "other_cpu"

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
        pip_name = pip_name or package_name
        full_import_path = (
            f"{package_name}.{module_name}" if module_name else package_name
        )

        try:
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)
            logging.info(f"Successfully imported {import_name or full_import_path}.")
        except ImportError:
            logging.info(f"Installing {pip_name}...")
            try:
                ImportUtil._run_pip_command(["install", pip_name])
                if import_name:
                    module = __import__(full_import_path, fromlist=[import_name])
                    getattr(module, import_name)
                else:
                    __import__(full_import_path)
            except subprocess.CalledProcessError as e:
                raise ImportError(f"Failed to install {pip_name}: {e}") from e
            except ImportError as e:
                raise ImportError(f"Failed to import {pip_name} after installation: {e}") from e

    @staticmethod
    def import_module(module_path: str) -> Any:
        """
        Import a module by its path.

        Args:
            module_path: The path of the module to import.

        Returns:
            The imported module.

        Raises:
            ImportError: If the module cannot be imported.
        """
        try:
            return importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Failed to import module {module_path}: {e}") from e

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        return importlib.util.find_spec(package_name) is not None

    @staticmethod
    @lru_cache
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
            ImportError: If the package is not found and not installed.
            ValueError: If the import fails after installation attempt.
        """
        if not ImportUtil.is_package_installed(package_name):
            if attempt_install:
                logging.info(
                    f"Package {package_name} not found. Attempting to install."
                )
                try:
                    ImportUtil.install_import(
                        package_name, module_name, import_name, pip_name
                    )
                except ImportError as e:
                    raise ValueError(f"Failed to install {package_name}: {e}") from e
            else:
                logging.info(f"Package {package_name} not found. {error_message}")
                raise ImportError(
                    f"Package {package_name} not found. {error_message}"
                )

    @staticmethod
    def list_installed_packages() -> List[str]:
        """
        List all installed packages.

        Returns:
            List[str]: A list of names of installed packages.
        """
        try:
            return [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
        except Exception as e:
            logging.error(f"Failed to list installed packages: {e}")
            return []

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """
        Uninstall a specified package.

        Args:
            package_name: The name of the package to uninstall.

        Raises:
            subprocess.CalledProcessError: If the uninstallation fails.
        """
        try:
            ImportUtil._run_pip_command(["uninstall", package_name, "-y"])
            logging.info(f"Successfully uninstalled {package_name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to uninstall {package_name}. Error: {e}")
            raise

    @staticmethod
    def update_package(package_name: str) -> None:
        """
        Update a specified package.

        Args:
            package_name: The name of the package to update.

        Raises:
            subprocess.CalledProcessError: If the update fails.
        """
        try:
            ImportUtil._run_pip_command(["install", "--upgrade", package_name])
            logging.info(f"Successfully updated {package_name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to update {package_name}. Error: {e}")
            raise

    @staticmethod
    def _run_pip_command(args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
        """
        Run a pip command.

        Args:
            args: The arguments to pass to pip.

        Returns:
            A CompletedProcess instance.

        Raises:
            subprocess.CalledProcessError: If the pip command fails.
        """
        return subprocess.run(
            [sys.executable, "-m", "pip"] + list(args),
            check=True,
            capture_output=True
        )

# File: lion_core/utils/package_util.py