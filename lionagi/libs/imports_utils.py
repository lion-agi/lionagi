# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
import importlib.metadata
import importlib.util
import logging
import subprocess
import sys
from collections.abc import Sequence
from typing import Any, Literal, TypeAlias

# Type aliases
ImportedModule: TypeAlias = Any
PackageManager: TypeAlias = Literal["uv", "pip"]
ImportName: TypeAlias = str | list[str]


__all__ = (
    "import_module",
    "install_import",
    "is_import_installed",
    "check_import",
)


def get_package_manager() -> PackageManager:
    """Check if uv is available, otherwise default to pip."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return "uv"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "pip"


def run_install_command(
    args: Sequence[str],
    package_manager: PackageManager | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Run package installation command with preferred manager.

    Args:
        args: Command arguments
        package_manager: Override default package manager
    """
    manager = package_manager or get_package_manager()

    if manager == "uv":
        return subprocess.run(
            ["uv", "pip"] + list(args),
            check=True,
            capture_output=True,
        )
    return subprocess.run(
        [sys.executable, "-m", "pip"] + list(args),
        check=True,
        capture_output=True,
    )


def import_module(
    package_name: str,
    module_name: str | None = None,
    import_name: ImportName | None = None,
) -> ImportedModule:
    """Import module or specific attributes.

    Args:
        package_name: Base package to import
        module_name: Optional submodule path
        import_name: Specific attribute(s) to import
    """
    try:
        full_path = (
            f"{package_name}.{module_name}" if module_name else package_name
        )

        if not import_name:
            return __import__(full_path)

        import_names = (
            [import_name] if isinstance(import_name, str) else import_name
        )
        imported = __import__(full_path, fromlist=import_names)

        if len(import_names) == 1:
            return getattr(imported, import_names[0])
        return [getattr(imported, name) for name in import_names]

    except ImportError as e:
        raise ImportError(f"Failed to import {full_path}: {e}") from e


def install_import(
    package_name: str,
    module_name: str | None = None,
    import_name: ImportName | None = None,
    pip_name: str | None = None,
) -> ImportedModule:
    """Install and import package if not found.

    Args:
        package_name: Package to install/import
        module_name: Optional submodule path
        import_name: Specific attribute(s) to import
        pip_name: Alternative name for installation
    """
    install_name = pip_name or package_name

    try:
        return import_module(package_name, module_name, import_name)
    except ImportError:
        logging.info(f"Installing {install_name}...")
        try:
            run_install_command(["install", install_name])
            return import_module(package_name, module_name, import_name)
        except subprocess.CalledProcessError as e:
            raise ImportError(f"Failed to install {install_name}: {e}") from e
        except ImportError as e:
            raise ImportError(
                f"Failed to import {install_name} after installation: {e}"
            ) from e


def is_import_installed(package_name: str) -> bool:
    """Check if package is installed."""
    return importlib.util.find_spec(package_name) is not None


def check_import(
    package_name: str,
    module_name: str | None = None,
    import_name: ImportName | None = None,
    pip_name: str | None = None,
    attempt_install: bool = True,
    error_message: str = "",
) -> ImportedModule:
    """Check, optionally install, and import package.

    Args:
        package_name: Package to check/install
        module_name: Optional submodule path
        import_name: Specific attribute(s) to import
        pip_name: Alternative name for installation
        attempt_install: Whether to try installing if missing
        error_message: Custom error message
    """
    if not is_import_installed(package_name):
        if attempt_install:
            logging.info(
                f"Package {package_name} not found. Attempting installation."
            )
            try:
                return install_import(
                    package_name, module_name, import_name, pip_name
                )
            except ImportError as e:
                raise ValueError(
                    f"Failed to install {package_name}: {e}"
                ) from e

        msg = f"Package {package_name} not found. {error_message}"
        logging.info(msg)
        raise ImportError(msg)

    return import_module(package_name, module_name, import_name)
