import importlib.util
import logging
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class SysUtil:
    """
    Provides a nested_structure of static utility methods for system operations,
    including CPU architecture detection, directory management, dictionary
    manipulation, dynamic module importation, package installation checks, data type
    validation, schema matching, path splitting, timestamp conversion, and XML processing.

    This class is designed to facilitate common system and data manipulation tasks that
    can be leveraged across various applications, simplifying operations such as
    identifying CPU architecture, clearing directories, renaming keys in dictionaries,
    dynamically importing or installing modules, checking for installed packages,
    validating data types and schemas, splitting file paths, converting timestamps to
    datetime objects, and converting XML to dictionaries.

    Methods: get_cpu_architecture: Determines the machine's CPU architecture.
    clear_dir: Deletes all files in a specified directory, handling exceptions, and
    logging. change_dict_key: Renames a key in a dictionary if the old key exists.
    install_import: Dynamically imports a module or specific name from a module,
    installing the package via pip if necessary. is_package_installed: Checks if a
    Python package is installed. is_same_dtype: Validates if all elements in a
    container are of the same specified data type. is_schema: Validates if a dictionary
    matches a specified schema. split_path: Separates a file path into its directory
    and filepath components. timestamp_to_datetime: Converts a UNIX timestamp to a
    `datetime` object. xml_to_dict: Converts an XML ElementTree Element to a dictionary.
    """

    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Determines the current machine's CPU architecture, categorizing as
        'apple_silicon' or 'other_cpu'.

        This function checks the platform's CPU architecture to identify if it is Apple
        Silicon (ARM-based architecture) or another CPU type, facilitating
        architecture-specific logic or optimizations.

        Returns:
            str: 'apple_silicon' if the CPU is ARM-based, otherwise 'other_cpu'.

        Examples:
            >>> SysUtil.get_cpu_architecture()
            'apple_silicon' # Output may vary depending on execution environment.
            >>> SysUtil.get_cpu_architecture()
            'other_cpu' # For non-ARM architectures.
        """
        arch = platform.machine()
        if 'arm' in arch or 'aarch64' in arch:
            return 'apple_silicon'
        else:
            return 'other_cpu'

    @staticmethod
    def clear_dir(dir_path: str) -> None:
        """
        Deletes all files in the specified directory path. Logs actions and errors.

        Args:
            dir_path (str): The path to the directory to clear.

        Raises:
            FileNotFoundError: If the specified directory does not exist.

        Examples:
            >>> SysUtil.clear_dir('/path/to/directory')
            # Assumes directory '/path/to/directory' exists and contains files.

        Note: This function logs each file deletion and any errors encountered in the
        configured logging handler.
        """
        if not os.path.exists(dir_path):
            raise FileNotFoundError("The specified directory does not exist.")

        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logging.info(f'Successfully deleted {file_path}')
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')
                raise

    @staticmethod
    def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
        """
        renames a key in a dictionary if the old key exists.

        Args:
            dict_ (Dict[Any, Any]): The dictionary to modify.
            old_key (str): The old key that should be renamed.
            new_key (str): The new key name.

        Raises:
            KeyError: If the old key does not exist in the dictionary.

        examples:
            >>> my_dict = {'old_key': 'value'}
            >>> SysUtil.change_dict_key(my_dict, 'old_key', 'new_key')
            >>> print(my_dict)
            {'new_key': 'value'}
        """
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @staticmethod
    def create_path(directory: str | Path, filename: str, timestamp: bool = True,
                    dir_exist_ok: bool = True, time_prefix: bool = False) -> str:
        """
        constructs a file path with optional timestamping and ensures directory creation.

        this function builds a complete file path based on provided directory and
        filepath, with options for adding a timestamp to the filepath and ensuring the
        target directory is created if it does not exist.

        Args: directory (str): The target directory for the file. filepath (str): The
        name of the file, including an extension if applicable. timestamp (bool): Whether
        to add a timestamp to the filepath. defaults to True. dir_exist_ok (bool): If
        True, does not raise an error if the directory already exists. defaults to
        True. time_prefix (bool): If True, adds the timestamp as a prefix to the
        filepath; otherwise, adds it as a suffix.

        Returns: str: The fully constructed file path, incorporating the directory,
        optional timestamp, and filepath.

        examples:
            >>> SysUtil.create_path('/tmp', 'log.txt', time_prefix=True)
            '/tmp/2023-01-01T00_00_00_log.txt'
            >>> SysUtil.create_path('/tmp', 'data.csv', timestamp=False)
            '/tmp/data.csv'

        """
        # Convert directory to pathlib.Path object for robust path handling
        dir_path = Path(directory)

        # Handle filepath and extension
        name, ext = os.path.splitext(filename)
        ext = ext or ''  # Ensure ext is a string, even if empty

        # Construct the timestamp string
        timestamp_str = SysUtil.get_timestamp() if timestamp else ''
        filename = f"{timestamp_str}{name}" if time_prefix else f"{name}{timestamp_str}"
        full_filename = f"{filename}{ext}"  # Reattach extension

        # Use pathlib for path construction and directory creation
        full_path = dir_path / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)  # Create directory
        # if needed

        return str(full_path)

    @staticmethod
    def get_timestamp(separator='_') -> str:
        """
        Generates a current timestamp formatted for use in filenames, allowing for a
        custom separator.

        Creates a timestamp string using the current date and time. The format is
        adapted to be safe for use in filenames across different operating systems by
        replacing characters generally not allowed in filenames, such as colons and
        periods, with a specified separator.

        Args: separator (str, optional): The character used to replace disallowed
        characters in the timestamp. Defaults to '_'.

        Returns: str: A string representing the current timestamp, formatted with the
        specified separator for filepath compatibility.

        Examples:
            >>> SysUtil.get_timestamp()
            '2023-03-25T12_00_00'
            >>> SysUtil.get_timestamp('-')
            '2023-03-25T12-00-00'

        """
        return datetime.now().isoformat().replace(":", separator).replace(".", separator)

    @staticmethod
    def install_import(package_name, module_name=None, import_name=None, pip_name=None):
        """
        dynamically imports a module or a specific name from a module. if the import
        fails, attempts to install the package via pip and retries the import.

        Args: package_name (str): The package name to import. module_name (str,
        optional): The module name to import from the package. defaults to None.
        import_name (str, optional): The specific name to import from the module or
        package. defaults to None. pip_name (str, optional): The pip package name if
        different from package_name. defaults to None.

        examples:
            >>> SysUtil.install_import('numpy')
            Successfully imported numpy.
            # If numpy is not installed, it attempts to install it first.
        """
        # Defaults to package_name if pip_name is not explicitly provided
        if pip_name is None:
            pip_name = package_name

        full_import_path = (
            package_name if module_name is None else f"{package_name}.{module_name}"
        )
        try:
            if import_name:
                # For importing a specific name from a module or submodule
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)

            else:
                # For importing the module or package itself
                __import__(full_import_path)
            print(f"Successfully imported {import_name or full_import_path}.")

        except ImportError:
            print(f"Module {full_import_path} or attribute {import_name} not found. "
                  f"Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)

            else:
                __import__(full_import_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Checks if a Python package is installed.

        Args:
            package_name (str): The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.

        Examples:
            >>> SysUtil.is_package_installed('numpy')
            True
            # This will return False if numpy is not installed.
        """
        package_spec = importlib.util.find_spec(package_name)
        return package_spec is not None

    @staticmethod
    def check_import(package_name, module_name=None, import_name=None, pip_name=None):
        try:
            if not SysUtil.is_package_installed(package_name=package_name):
                SysUtil.install_import(
                    package_name=package_name, module_name=module_name,
                    import_name=import_name, pip_name=pip_name)
        except Exception as e:
            raise ValueError(f'Failed to import {package_name}. Error: {e}')

    @staticmethod
    def is_same_dtype(input_: Any, dtype: type = None) -> bool:
        """
        validates if all elements in a container (list or dict) are of the same
        specified data type.

        Args: input_ (Any): The container (list or dict) to validate. dtype (type,
        optional): The data type to validate against. if None, the type of the first
        element is used.

        Returns:
            bool: True if all elements match the specified data type, False otherwise.

        examples:
            >>> SysUtil.is_same_dtype([1, 2, 3])
            True
            >>> SysUtil.is_same_dtype([1, 'two', 3], int)
            False
        """

        if isinstance(input_, list):
            dtype = dtype or type(input_[0])
            return all(isinstance(i, dtype) for i in input_)

        elif isinstance(input_, dict):
            dtype = dtype or type(list(input_.values())[0])
            return all(isinstance(v, dtype) for _, v in input_.items())

        else:
            dtype = dtype or type(input_)
            return isinstance(input_, dtype)

    @staticmethod
    def is_schema(dict_: Dict, schema: Dict) -> bool:
        """
        validates if a dictionary matches a specified schema, checking types of its keys.

        Args:
            dict_ (Dict): The dictionary to validate.
            schema (Dict): The schema with expected types for each key.

        Returns:
            bool: True if the dictionary matches the schema, False otherwise.

        Examples:
            >>> schema_ = {"name": str, "age": int}
            >>> SysUtil.is_schema({"name": "John", "age": 30}, schema_)
            True
            >>> SysUtil.is_schema({"name": "John", "age": "thirty"}, schema_)
            False
        """
        for key, expected_type in schema.items():

            if not isinstance(dict_[key], expected_type):
                return False

        return True

    @staticmethod
    def split_path(path: str) -> tuple:
        """Separates a file path into its directory and filepath components.

        Args:
            path (str): The path to split.

        Returns:
            tuple: A tuple containing the directory and filepath.

        Examples:
            >>> SysUtil.split_path('/path/to/file.txt')
            ('/path/to', 'file.txt')
        """
        folder_name = os.path.dirname(path)
        file_name = os.path.basename(path)

        return folder_name, file_name

    @staticmethod
    def timestamp_to_datetime(timestamp: float) -> datetime:
        """Converts a UNIX timestamp to a `datetime` object.

        Args:
            timestamp (float): The UNIX timestamp to convert.

        Returns:
            datetime: The `datetime` object representing the given timestamp.

        Examples:
            >>> SysUtil.timestamp_to_datetime(1609459200.0)
            datetime.datetime(2021, 1, 1, 0, 0)
        """
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        """Converts an XML ElementTree Element to a dictionary.

        Args:
            root (ET.Element): The root element of the XML tree.

        Returns: Dict[str, Any]: A dictionary representation of the XML element and its
        children.

        Examples:
            >>> root_ = ET.fromstring('<parent><child>value</child></parent>')
            >>> SysUtil.xml_to_dict(root_)
            {'child': 'value'}
        """
        data = {}
        for child in root:
            data[child.tag] = child.text

        return data
