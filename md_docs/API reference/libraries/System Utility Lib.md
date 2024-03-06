```
from lionagi.libs.sys_util import SysUtil
```

# System Utility Library (`SysUtil`)

The `SysUtil` class provides a collection of static methods designed to facilitate common system operations, including time management, data structure manipulation, file handling, and package management.

## Methods Overview

### `sleep`

Pauses execution for a specified duration.

#### Arguments

- `delay (float)`: The amount of time, in seconds, to pause execution.

### `get_now`

Returns the current time either as a Unix timestamp or a datetime object.

#### Arguments

- `datetime_ (bool)`: If True, returns a datetime object; otherwise, returns a Unix timestamp.

#### Returns

- `float | datetime`: The current time as a Unix timestamp or a datetime object.

### `change_dict_key`

Safely changes a key in a dictionary if the old key exists.

#### Arguments

- `dict_ (dict)`: The dictionary in which to change the key.
- `old_key (str)`: The old key to be changed.
- `new_key (str)`: The new key to replace the old key.

### `get_timestamp`

Returns a timestamp string with optional custom separators and timezone.

#### Arguments

- `tz (timezone)`: The timezone for the timestamp.
- `sep (str)`: The separator to use in the timestamp string, replacing '-', ':', and '.'.

#### Returns

- `str`: A string representation of the current timestamp.

## Examples

### Pausing Execution

```python
SysUtil.sleep(2)  # Pauses execution for 2 seconds.
```

### Getting Current Time

```python
timestamp = SysUtil.get_now()  # Unix timestamp.
datetime_obj = SysUtil.get_now(datetime_=True)  # datetime object.
```

### Changing Dictionary Key

```python
dict_ = {'old_key': 100}
SysUtil.change_dict_key(dict_, 'old_key', 'new_key')
# dict_ is now {'new_key': 100}
```

### Generating Timestamp

```python
from datetime import timezone, timedelta

# Using UTC timezone
utc_timestamp = SysUtil.get_timestamp(tz=timezone.utc)
print(utc_timestamp)  # Output format: "YYYY_MM_DDTHH_MM_SS.ssssss+00_00"

# Using a specific timezone (e.g., Eastern Time Zone)
eastern_tz = timezone(timedelta(hours=-5))  # Adjust the hours offset as necessary
eastern_timestamp = SysUtil.get_timestamp(tz=eastern_tz)
print(eastern_timestamp)  # Output format: "YYYY_MM_DDTHH_MM_SS.ssssss-05_00"
```

Continuing with the `SysUtil` class, let's explore the next set of methods focusing on data validation, deep copying, unique identifier generation, and efficient binning strategies.

### `is_schema`

Validates if the given dictionary matches the expected schema types.

#### Arguments

- `dict_ (dict)`: The dictionary to validate.
- `schema (dict)`: The expected schema with types.

#### Returns

- `bool`: True if the dictionary matches the schema, False otherwise.

### `create_copy`

Creates deep copies of the input, either as a single copy or a list of copies.

#### Arguments

- `input_ (Any)`: The input to be copied.
- `num (int)`: The number of copies to create.

#### Returns

- `Any | list[Any]`: A single copy of the input or a list of deep copies.

### `create_id`

Generates a unique identifier based on the current time and random bytes.

#### Arguments

- `n (int)`: The length of the generated identifier.

#### Returns

- `str`: A unique identifier string.

### `get_bins`

Organizes indices of strings into bins based on a cumulative upper limit.

#### Arguments

- `input_ (list[str])`: The list of strings to be binned.
- `upper (int | None)`: The cumulative length upper limit for each bin.

#### Returns

- `list[list[int]]`: A list of bins, each bin is a list of indices from the input list.

## Examples

### Validating Schema

```python
schema = {"name": str, "age": int}
dict_ = {"name": "John", "age": 30}
is_valid = SysUtil.is_schema(dict_, schema)
print(is_valid)  # Output: True
```

### Creating Deep Copies

```python
original = {"key": "value"}
copies = SysUtil.create_copy(original, num=2)
# `copies` will be a list of 2 deep copied dictionaries.
```

### Generating Unique Identifier

```python
unique_id = SysUtil.create_id(16)
print(unique_id)  # Output: A 16-character long unique identifier string.
```

### Organizing Strings into Bins

```python
input_strings = ["hello", "world", "lionagi", "system", "util"]
bins = SysUtil.get_bins(input_strings, upper=10)
# This will create bins with indices of `input_strings` such that the cumulative length of strings in each bin does not exceed 10.
```

### `get_cpu_architecture`

Returns a string identifying the CPU architecture, with special categorization for some architectures.

#### Returns

- `str`: A string identifying the CPU architecture ('apple_silicon' or 'other_cpu').

### `install_import`

Attempts to import a package, installing it with pip if not found.

#### Arguments

- `package_name (str)`: The base name of the package to import.
- `module_name (str | None)`: Optional submodule name.
- `import_name (str | None)`: Specific name to import from the module or package.
- `pip_name (str | None)`: The pip package name if different from `package_name`.

### `import_module`

Imports a module given its path.

#### Arguments

- `module_path (str)`: The full path of the module to import.

#### Returns

- Module object of the imported module.

### `is_package_installed`

Checks if a package is currently installed.

#### Arguments

- `package_name (str)`: The name of the package to check.

#### Returns

- `bool`: True if the package is installed, False otherwise.

## Examples

### Identifying CPU Architecture

```python
architecture = SysUtil.get_cpu_architecture()
print(architecture)  # Output could be "apple_silicon" or "other_cpu".
```

### Installing and Importing a Package

Assuming the package is not already installed, this example shows how to automatically install and import it:

```python
SysUtil.install_import('requests')  # This will install the 'requests' package if not already installed and then import it.
```

### Importing a Module

```python
module = SysUtil.import_module('os')
print(module)  # This will print the <module 'os' from 'path'> indicating successful import.
```

### Checking if a Package is Installed

```python
is_installed = SysUtil.is_package_installed('pandas')
print(is_installed)  # Output: True if pandas is installed, otherwise False.
```


### `list_installed_packages`

Lists all installed packages in the environment.

#### Returns

- `list`: A list of names of all installed packages.

### `uninstall_package`

Uninstalls a specified package from the environment.

#### Arguments

- `package_name (str)`: The name of the package to uninstall.

### `update_package`

Updates a specified package to the latest version available.

#### Arguments

- `package_name (str)`: The name of the package to update.

### `clear_dir`

Clears all files (and, if `recursive`, directories) in the specified directory, excluding files matching any patterns in the exclude list.

#### Arguments

- `dir_path (Path | str)`: The path to the directory to clear.
- `recursive (bool)`: If True, clears directories recursively. Defaults to False.
- `exclude (list[str])`: A list of string patterns to exclude from deletion.

### `split_path`

Splits a path into its directory and filename components.

#### Arguments

- `path (Path | str)`: The path to split.

#### Returns

- `tuple[Path, str]`: A tuple containing the directory and filename.

### `create_path`

Creates a path with an optional timestamp in the specified directory.

#### Arguments

- `directory (Path | str)`: The directory where the file will be located.
- `filename (str)`: The filename, including a valid extension.
- `timestamp (bool)`: Adds a timestamp to the filename if True.
- `dir_exist_ok (bool)`: If True, does not raise an error if the directory exists.
- `time_prefix (bool)`: Adds the timestamp as a prefix if True; as a suffix otherwise.
- `custom_timestamp_format (str | None)`: Custom format for the timestamp.

#### Returns

- `Path`: The full path to the file.

### `list_files`

Lists all files in the specified directory, optionally filtered by extension.

#### Arguments

- `dir_path (Path | str)`: The directory to list files from.
- `extension (str)`: Optional filter for file extension.

#### Returns

- `list[Path]`: A list of paths to files.

### `copy_file`

Copies a file from one location to another.

#### Arguments

- `src (Path | str)`: The source file path.
- `dest (Path | str)`: The destination file path.

### `get_size`

Gets the size of a file or the total size of files in a directory.

#### Arguments

- `path (Path | str)`: The path to the file or directory.

#### Returns

- `int`: The size in bytes.

## Examples

### Listing Installed Packages

```python
installed_packages = SysUtil.list_installed_packages()
print(installed_packages)
```

### Uninstalling a Package

```python
SysUtil.uninstall_package('some_package')
```

### Updating a Package

```python
SysUtil.update_package('some_package')
```

### Clearing a Directory

```python
SysUtil.clear_dir('/path/to/directory', recursive=True)
```

### Splitting a Path

```python
directory, filename = SysUtil.split_path('/path/to/file.txt')
print(directory, filename)
```

### Creating a Path with Timestamp

```python
path = SysUtil.create_path('/path/to/directory', 'file.txt')
print(path)
```

### Listing Files in a Directory

```python
files = SysUtil.list_files('/path/to/directory', extension='txt')
print(files)
```

### Copying a File

```python
SysUtil.copy_file('/path/to/source.txt', '/path/to/destination.txt')
```

### Getting File or Directory Size

```python
size = SysUtil.get_size('/path/to/file_or_directory')
print(size)
```

