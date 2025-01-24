# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
import logging
import subprocess

from lionagi.utils import run_package_manager_command


def list_installed_packages() -> list[str]:
    """
    List all installed packages.

    Returns:
        List[str]: A list of names of installed packages.
    """
    try:
        return [
            dist.metadata["Name"]
            for dist in importlib.metadata.distributions()
        ]
    except Exception as e:
        logging.error(f"Failed to list installed packages: {e}")
        return []


def uninstall_package(package_name: str) -> None:
    """
    Uninstall a specified package.

    Args:
        package_name: The name of the package to uninstall.

    Raises:
        subprocess.CalledProcessError: If the uninstallation fails.
    """
    try:
        run_package_manager_command(["uninstall", package_name, "-y"])
        logging.info(f"Successfully uninstalled {package_name}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to uninstall {package_name}. Error: {e}")
        raise


def update_package(package_name: str) -> None:
    """
    Update a specified package.

    Args:
        package_name: The name of the package to update.

    Raises:
        subprocess.CalledProcessError: If the update fails.
    """
    try:
        run_package_manager_command(["install", "--upgrade", package_name])
        logging.info(f"Successfully updated {package_name}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to update {package_name}. Error: {e}")
        raise
