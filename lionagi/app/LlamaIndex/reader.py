from typing import Any, Union, List, Dict
from lionagi.os.libs.sys_util import check_import, import_module
from .util import parse_reader_name


def get_llama_index_reader(reader: Union[Any, str] = None) -> Any:
    """
    Retrieves a llama index reader object based on the specified reader name
    or class.

    This function checks if the specified reader is a recognized type or name
    and returns the appropriate llama index reader class. If a string is
    provided, it attempts to match it with known reader names and import the
    corresponding reader class dynamically. If a reader class is provided, it
    validates that the class is a subclass of BasePydanticReader.

    Args:
        reader (Union[Any, str], optional): The reader identifier, which can be
            a reader class, a string alias for a reader class, or None. If
            None, returns the SimpleDirectoryReader class.

    Returns:
        Any: The llama index reader class corresponding to the specified
        reader.

    Raises:
        TypeError: If the reader is neither a string nor a subclass of
        BasePydanticReader.
        ValueError: If the specified reader string does not correspond to a
        known reader.
        AttributeError: If there is an issue importing the specified reader.
    """

    check_import("llama_index", pip_name="llama-index")
    from llama_index.core import SimpleDirectoryReader
    from llama_index.core.readers.base import BasePydanticReader

    if reader in [
        "SimpleDirectoryReader",
        SimpleDirectoryReader,
        "simple-directory-reader",
        "simple_directory_reader",
        "simple",
        "simple_reader",
        "simple-reader",
    ]:
        return SimpleDirectoryReader

    if not isinstance(reader, str) and not issubclass(reader, BasePydanticReader):
        raise TypeError("reader must be a string or BasePydanticReader.")

    if isinstance(reader, str):
        package_name, pip_name = parse_reader_name(reader)
        if not package_name and not pip_name:
            raise ValueError(
                f"{reader} is not found. Please directly input llama-index "
                f"reader class or check llama-index documentation for "
                f"supported readers."
            )

        try:
            check_import(package_name, pip_name=pip_name)
            reader_class = getattr(import_module(package_name), reader)
            return reader_class

        except Exception as e:
            raise AttributeError(
                f"Failed to import/download {reader}, please check llama-index "
                f"documentation to download it manually and input the reader "
                f"object: {e}"
            )

    if issubclass(reader, BasePydanticReader):
        return reader


def llama_index_read_data(
    reader: Union[None, str, Any] = None,
    reader_args: List[Any] = None,
    reader_kwargs: Dict[str, Any] = None,
    loader_args: List[Any] = None,
    loader_kwargs: Dict[str, Any] = None,
) -> Any:
    """
    Reads data using a specified llama index reader and its arguments.

    This function initializes a llama index reader with the given arguments
    and keyword arguments, then loads data using the reader's `load_data`
    method with the provided loader arguments and keyword arguments.

    Args:
        reader (Union[None, str, Any], optional): The reader to use. This can
            be a class, a string identifier, or None. If None, a default
            reader is used.
        reader_args (List[Any], optional): Positional arguments to initialize
            the reader.
        reader_kwargs (Dict[str, Any], optional): Keyword arguments to
            initialize the reader.
        loader_args (List[Any], optional): Positional arguments for the
            reader's `load_data` method.
        loader_kwargs (Dict[str, Any], optional): Keyword arguments for the
            reader's `load_data` method.

    Returns:
        Any: The documents or data loaded by the reader.

    Raises:
        ValueError: If there is an error initializing the reader or loading
        the data.
    """
    try:
        reader_args = reader_args or []
        reader_kwargs = reader_kwargs or {}
        loader_args = loader_args or []
        loader_kwargs = loader_kwargs or {}

        reader_class = get_llama_index_reader(reader)

        loader = reader_class(*reader_args, **reader_kwargs)
        documents = loader.load_data(*loader_args, **loader_kwargs)
        return documents
    except Exception as e:
        raise ValueError(f"Failed to read and load data. Error: {e}")
