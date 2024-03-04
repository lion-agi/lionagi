
# SysUtil Class API Reference

## Overview
`SysUtil` provides utility methods for common file and directory operations, simplifying tasks such as directory clearing, path splitting, file listing, and file copying. It's designed to enhance file system manipulation with convenience methods for Python projects.

### Methods

#### clear_dir
```python
def clear_dir(dir_path: Path | str, recursive: bool = False, exclude: list[str] = None) -> None:
```
- **Description**: Clears all files (and optionally subdirectories) within a specified directory, with support for exclusions.
- **Parameters**:
  - `dir_path` (Path | str): The path to the directory to clear.
  - `recursive` (bool, optional): If `True`, clears subdirectories recursively. Defaults to `False`.
  - `exclude` (list[str], optional): A list of filename patterns to exclude from deletion. Defaults to `None`.
- **Raises**:
  - `FileNotFoundError`: If the specified directory does not exist.

#### split_path
```python
def split_path(path: Path | str) -> tuple[Path, str]:
```
- **Description**: Splits a path into its parent directory and filename.
- **Parameters**:
  - `path` (Path | str): The path to split.
- **Returns**:
  - A tuple containing the parent directory (`Path`) and filename (`str`).

#### create_path
```python
def create_path(
    directory: Path | str,
    filename: str,
    timestamp: bool = True,
    dir_exist_ok: bool = True,
    time_prefix: bool = False,
    custom_timestamp_format: str | None = None,
) -> Path:
```
- **Description**: Constructs a file path with optional timestamp inclusion in the filename.
- **Parameters**:
  - `directory` (Path | str): The directory for the file.
  - `filename` (str): The filename, optionally including extension.
  - `timestamp` (bool, optional): If `True`, includes a timestamp in the filename. Defaults to `True`.
  - `dir_exist_ok` (bool, optional): If `True`, does not raise an error if the directory exists. Defaults to `True`.
  - `time_prefix` (bool, optional): If `True`, places the timestamp at the beginning of the filename. Defaults to `False`.
  - `custom_timestamp_format` (str | None, optional): Custom format for the timestamp. Defaults to `None`.
- **Returns**:
  - The constructed `Path` object.

#### list_files
```python
def list_files(dir_path: Path | str, extension: str = None) -> list[Path]:
```
- **Description**: Lists all files in a directory, optionally filtering by file extension.
- **Parameters**:
  - `dir_path` (Path | str): The directory to list files from.
  - `extension` (str, optional): The file extension to filter by. Defaults to `None`.
- **Returns**:
  - A list of `Path` objects representing the files.
- **Raises**:
  - `NotADirectoryError`: If the specified path is not a directory.

#### copy_file
```python
def copy_file(src: Path | str, dest: Path | str) -> None:
```
- **Description**: Copies a file from a source path to a destination path.
- **Parameters**:
  - `src` (Path | str): The source file path.
  - `dest` (Path | str): The destination path.
- **Raises**:
  - `FileNotFoundError`: If the source file does not exist.

#### get_size
```python
def get_size(path: Path | str) -> int:
```
- **Description**: Gets the size of a file or the total size of files in a directory.
- **Parameters**:
  - `path` (Path | str): The path to the file or directory.
- **Returns**:
  - The size in bytes.
- **Raises**:
  - `FileNotFoundError`: If the specified path does not exist.
