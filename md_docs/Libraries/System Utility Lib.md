
# SysUtil API Reference

The `SysUtil` class provides utility functions for various system-related tasks.

### `sleep`
`(delay: float) -> None`

Pauses execution for a specified duration.

Parameters:
- `delay` (float): The amount of time, in seconds, to pause execution.

### `get_now`
`(datetime_: bool = False, tz=None) -> float | datetime`

Returns the current time either as a Unix timestamp or a datetime object.

Parameters:
- `datetime_` (bool): If True, returns a datetime object; otherwise, returns a Unix timestamp.
- `tz` (timezone): The timezone for the datetime object.

Returns:
float | datetime: The current time as a Unix timestamp or a datetime object.

### `change_dict_key`
`(dict_: `dict[Any, Any]`, old_key: str, new_key: str) -> None`

Safely changes a key in a dictionary if the old key exists.

Parameters:
- `dict_` (`dict[Any, Any]`): The dictionary in which to change the key.
- `old_key` (str): The old key to be changed.
- `new_key` (str): The new key to replace the old key.

### `get_timestamp`

^bfa89d

`(tz: timezone = timezone.utc, sep: str = "_") -> str`

Returns a timestamp string with optional custom separators and timezone.

Parameters:
- `tz` (`timezone`): The timezone for the timestamp (default: `timezone.utc`).
- `sep` (`str`): The separator to use in the timestamp string, replacing `'-', ':',` and `'.'` (default:` "_"`).

Returns:
`str`: A string representation of the current timestamp.

### `is_schema`
`(dict_: dict[Any, Any], schema: dict[Any, type]) -> bool`

Validates if the given dictionary matches the expected schema types.

Parameters:
- `dict_` (`dict[Any, Any]`): The dictionary to validate.
- `schema` (`dict[Any, type]`): The expected schema dictionary.

Returns:
`bool`: True if the dictionary matches the schema, False otherwise.

### `create_copy`
`(input_: Any, num: int = 1) -> Any | list[Any]`

Creates deep copies of the input, either as a single copy or a list of copies.

Parameters:
- `input_` (`Any`): The input to be copied.
- `num` (`int`): The number of copies to create (default: 1).

Returns:
`Any | list[Any]`: A single copy of the input or a list of deep copies.

### `create_id`
`(n: int = 32) -> str`

Generates a unique identifier based on the current time and random bytes.

Parameters:
- `n` (`int`): The length of the generated identifier (default: 32).

Returns:
`str`: A unique identifier string.

### `get_bins`
`(input_: list[str], upper: int | None = 2000) -> list[list[int]]`

Organizes indices of strings into bins based on a cumulative upper limit.

Parameters:
- `input_` (`list[str]`): The list of strings to be binned.
- `upper` (`int | None`): The cumulative length upper limit for each bin (default: 2000).

Returns:
`list[list[int]]`: A list of bins, each bin is a list of indices from the input list.

### `get_cpu_architecture`
`() -> str`

Returns a string identifying the CPU architecture.

Returns:
str: A string identifying the CPU architecture ('apple_silicon' or 'other_cpu').

### `install_import`
`(package_name: str, module_name: str = None, import_name: str = None, pip_name: str = None) -> None`

Attempts to import a package, installing it with pip if not found.

Parameters:
- `package_name` (str): The base name of the package to import.
- `module_name` (str): The submodule name to import from the package, if applicable (default: None).
- `import_name` (str): The specific name to import from the module or package (default: None).
- `pip_name` (str): The pip package name if different from `package_name` (default: None).

### `import_module`
`(module_path: str) -> None`

Imports a module from the specified module path.

Parameters:
- `module_path` (str): The path of the module to import.

Returns:
The imported module.

### `is_package_installed`
`(package_name: str) -> bool`

Checks if a package is currently installed.

Parameters:
- `package_name` (str): The name of the package to check.

Returns:
bool: True if the package is installed, False otherwise.

### `check_import`
`(package_name: str, module_name: str | None = None, import_name: str | None = None, pip_name: str | None = None, attempt_install: bool = True, error_message: str = "") -> None`

Checks if a package is installed; if not, attempts to install and import it.

Parameters:
- `package_name` (str): The name of the package to check and potentially install.
- `module_name` (str | None): The submodule name to import from the package, if applicable (default: None).
- `import_name` (str | None): The specific name to import from the module or package (default: None).
- `pip_name` (str | None): The pip package name if different from `package_name` (default: None).
- `attempt_install` (bool): If attempt to install the package if uninstalled (default: True).
- `error_message` (str): Error message when the package is not installed and not attempt to install (default: "").

### `list_installed_packages`
`() -> list`

List all installed packages using importlib.metadata.

Returns:
list: A list of installed package names.

### `uninstall_package`
`(package_name: str) -> None`

Uninstall a specified package.

Parameters:
- `package_name` (str): The name of the package to uninstall.

### `update_package`
`(package_name: str) -> None`

Update a specified package.

Parameters:
- `package_name` (str): The name of the package to update.

### `clear_dir`
`(dir_path: Path | str, recursive: bool = False, exclude: list[str] = None) -> None`

Clears all files (and, if recursive, directories) in the specified directory, excluding files that match any pattern in the exclude list.

Parameters:
- `dir_path` (Path | str): The path to the directory to clear.
- `recursive` (bool): If True, clears directories recursively (default: False).
- `exclude` (list[str]): A list of string patterns to exclude from deletion (default: None).

Raises:
- `FileNotFoundError`: If the specified directory does not exist.

### `split_path`
`(path: Path | str) -> tuple[Path, str]`

Splits a path into its directory and filename components.

Parameters:
- `path` (Path | str): The path to split.

Returns:
tuple[Path, str]: A tuple containing the directory and filename.

### `create_path`
`(directory: Path | str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix: bool = False, custom_timestamp_format: str | None = None) -> Path`

Creates a path with an optional timestamp in the specified directory.

Parameters:
- `directory` (Path | str): The directory where the file will be located.
- `filename` (str): The filename. Must include a valid extension.
- `timestamp` (bool): If True, adds a timestamp to the filename (default: True).
- `dir_exist_ok` (bool): If True, does not raise an error if the directory exists (default: True).
- `time_prefix` (bool): If True, adds the timestamp as a prefix; otherwise, as a suffix (default: False).
- `custom_timestamp_format` (str | None): A custom format for the timestamp (default: "%Y%m%d%H%M%S").

Returns:
Path: The full path to the file.

Raises:
- `ValueError`: If the filename is invalid.

### `list_files`
`(dir_path: Path | str, extension: str = None) -> list[Path]`

Lists all files in the specified directory, optionally filtered by extension.

Parameters:
- `dir_path` (Path | str): The path to the directory.
- `extension` (str): The file extension to filter by (default: None).

Returns:
list[Path]: A list of file paths.

Raises:
- `NotADirectoryError`: If the specified path is not a directory.

### `copy_file`
`(src: Path | str, dest: Path | str) -> None`

Copies a file from the source path to the destination path.

Parameters:
- `src` (Path | str): The source file path.
- `dest` (Path | str): The destination file path.

Raises:
- `FileNotFoundError`: If the source file does not exist or is not a file.

### `get_size`
`(path: Path | str) -> int`

Returns the size of a file or the total size of all files in a directory.

Parameters:
- `path` (Path | str): The path to the file or directory.

Returns:
int: The size in bytes.

Raises:
- `FileNotFoundError`: If the specified path does not exist.

## Usage Examples

```python
from lionagi.libs.sys_util import SysUtil

# Pause execution for 1 second
SysUtil.sleep(1)

# Get the current timestamp
timestamp = SysUtil.get_timestamp()
print(timestamp)  # Output: 2023_06_09_12_34_56

# Generate a unique identifier
unique_id = SysUtil.create_id()
print(unique_id)  # Output: a8f5f167f44f4964e6c998dee827110c

# Check if a package is installed
is_installed = SysUtil.is_package_installed("pandas")
print(is_installed)  # Output: True or False

# Create a path with a timestamp
file_path = SysUtil.create_path("data", "example.txt")
print(file_path)  # Output: data/example_20230609123456.txt

# Copy a file
SysUtil.copy_file("source.txt", "destination.txt")

# Get the size of a file or directory
file_size = SysUtil.get_size("example.txt")
print(file_size)  # Output: 1024
```

These examples demonstrate how to use various utility functions provided by the `SysUtil` class, such as pausing execution, generating timestamps and unique identifiers, installing and importing packages, creating file paths with timestamps, copying files, and getting file sizes.