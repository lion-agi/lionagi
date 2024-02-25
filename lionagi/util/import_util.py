import logging
import platform
import subprocess
import sys
import importlib
import importlib.metadata  # For listing installed packages


class ImportUtil:

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
            if not ImportUtil.is_package_installed(package_name):
                logging.info(
                    f"Package {package_name} not found. Attempting to install."
                )
                ImportUtil.install_import(
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
