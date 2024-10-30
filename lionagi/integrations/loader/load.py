from collections.abc import Callable

from lionagi.core.collections import pile
from lionagi.core.generic import Node

from ..bridge.langchain_.langchain_bridge import LangchainBridge
from ..bridge.llamaindex_.llama_index_bridge import LlamaIndexBridge
from .load_util import ReaderType, _datanode_parser, dir_to_nodes


def text_reader(args, kwargs):
    """
    Reads text files from a directory and converts them to Node instances.

    Args:
        args: Positional arguments for the dir_to_nodes function.
        kwargs: Keyword arguments for the dir_to_nodes function.

    Returns:
        A list of Node instances.

    Example usage:
        >>> args = ['path/to/text/files']
        >>> kwargs = {'file_extension': 'txt'}
        >>> nodes = text_reader(args, kwargs)
    """
    return dir_to_nodes(*args, **kwargs)


def load(
    reader: str | Callable = "text_reader",
    input_dir=None,
    input_files=None,
    recursive: bool = False,
    required_exts: list[str] = None,
    reader_type=ReaderType.PLAIN,
    reader_args=None,
    reader_kwargs=None,
    load_args=None,
    load_kwargs=None,
    to_lion: bool | Callable = True,
):
    """
    Loads data using the specified reader and converts it to Node instances.

    Args:
        reader (str | Callable): The reader function or its name. Defaults to "text_reader".
        input_dir (str, optional): The directory to read files from. Defaults to None.
        input_files (list[str], optional): Specific files to read. Defaults to None.
        recursive (bool, optional): Whether to read files recursively. Defaults to False.
        required_exts (list[str], optional): List of required file extensions. Defaults to None.
        reader_type (ReaderType, optional): The type of reader to use. Defaults to ReaderType.PLAIN.
        reader_args (list, optional): Positional arguments for the reader function. Defaults to None.
        reader_kwargs (dict, optional): Keyword arguments for the reader function. Defaults to None.
        load_args (list, optional): Positional arguments for loading. Defaults to None.
        load_kwargs (dict, optional): Keyword arguments for loading. Defaults to None.
        to_lion (bool | Callable, optional): Whether to convert the data to Node instances or a custom parser. Defaults to True.

    Returns:
        pile: A pile of Node instances.

    Raises:
        ValueError: If the reader_type is not supported.

    Example usage:
        >>> nodes = load(input_dir='path/to/text/files', required_exts=['txt'])
    """

    if reader_args is None:
        reader_args = []
    if reader_kwargs is None:
        reader_kwargs = {}
    if load_args is None:
        load_args = []
    if load_kwargs is None:
        load_kwargs = {}

    if reader_type == ReaderType.PLAIN:
        reader_kwargs["dir_"] = input_dir
        reader_kwargs["ext"] = required_exts
        reader_kwargs["recursive"] = recursive

        return read_funcs[ReaderType.PLAIN](reader, reader_args, reader_kwargs)

    if reader_type == ReaderType.LANGCHAIN:
        return read_funcs[ReaderType.LANGCHAIN](
            reader, reader_args, reader_kwargs, to_lion
        )

    elif reader_type == ReaderType.LLAMAINDEX:
        if input_dir is not None:
            reader_kwargs["input_dir"] = input_dir
        if input_files is not None:
            reader_kwargs["input_files"] = input_files
        if recursive:
            reader_kwargs["recursive"] = True
        if required_exts is not None:
            reader_kwargs["required_exts"] = required_exts

        return read_funcs[ReaderType.LLAMAINDEX](
            reader, reader_args, reader_kwargs, load_args, load_kwargs, to_lion
        )

    elif reader_type == ReaderType.SELFDEFINED:
        return read_funcs[ReaderType.SELFDEFINED](
            reader, reader_args, reader_kwargs, load_args, load_kwargs, to_lion
        )

    else:
        raise ValueError(
            f"{reader_type} is not supported. Please choose from {list(ReaderType)}"
        )


def _plain_reader(reader, reader_args, reader_kwargs):
    """
    Reads data using a plain reader.

    Args:
        reader (str | Callable): The reader function or its name.
        reader_args (list): Positional arguments for the reader function.
        reader_kwargs (dict): Keyword arguments for the reader function.

    Returns:
        pile: A pile of Node instances.

    Raises:
        ValueError: If the reader is not supported.

    Example usage:
        >>> nodes = _plain_reader('text_reader', ['path/to/files'], {'ext': 'txt'})
    """
    try:
        if reader == "text_reader":
            reader = text_reader
        nodes = reader(reader_args, reader_kwargs)
        return pile(nodes)
    except Exception as e:
        raise ValueError(
            f"Reader {reader} is currently not supported. Error: {e}"
        ) from e


def _langchain_reader(
    reader, reader_args, reader_kwargs, to_lion: bool | Callable
):
    """
    Reads data using a Langchain reader.

    Args:
        reader (str | Callable): The reader function or its name.
        reader_args (list): Positional arguments for the reader function.
        reader_kwargs (dict): Keyword arguments for the reader function.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of Node instances or custom parsed nodes.

    Example usage:
        >>> nodes = _langchain_reader('langchain_reader', ['arg1'], {'key': 'value'}, True)
    """
    nodes = LangchainBridge.langchain_loader(
        reader, reader_args, reader_kwargs
    )
    if isinstance(to_lion, bool) and to_lion is True:
        return pile([Node.from_langchain(i) for i in nodes])

    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


def _llama_index_reader(
    reader,
    reader_args,
    reader_kwargs,
    load_args,
    load_kwargs,
    to_lion: bool | Callable,
):
    """
    Reads data using a LlamaIndex reader.

    Args:
        reader (str | Callable): The reader function or its name.
        reader_args (list): Positional arguments for the reader function.
        reader_kwargs (dict): Keyword arguments for the reader function.
        load_args (list): Positional arguments for loading.
        load_kwargs (dict): Keyword arguments for loading.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of Node instances or custom parsed nodes.

    Example usage:
        >>> nodes = _llama_index_reader('llama_reader', ['arg1'], {'key': 'value'}, [], {}, True)
    """
    nodes = LlamaIndexBridge.llama_index_read_data(
        reader, reader_args, reader_kwargs, load_args, load_kwargs
    )
    if isinstance(to_lion, bool) and to_lion is True:
        return pile([Node.from_llama_index(i) for i in nodes])

    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


def _self_defined_reader(
    reader,
    reader_args,
    reader_kwargs,
    load_args,
    load_kwargs,
    to_lion: bool | Callable,
):
    """
    Reads data using a self-defined reader.

    Args:
        reader (str | Callable): The reader function or its name.
        reader_args (list): Positional arguments for the reader function.
        reader_kwargs (dict): Keyword arguments for the reader function.
        load_args (list): Positional arguments for loading.
        load_kwargs (dict): Keyword arguments for loading.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of Node instances or custom parsed nodes.

    Raises:
        ValueError: If the self-defined reader is not valid.

    Example usage:
        >>> nodes = _self_defined_reader(custom_reader, ['arg1'], {'key': 'value'}, [], {}, custom_parser)
    """
    try:
        loader = reader(*reader_args, **reader_kwargs)
        nodes = loader.load(*load_args, **load_kwargs)
    except Exception as e:
        raise ValueError(
            f"Self defined reader {reader} is not valid. Error: {e}"
        ) from e

    if isinstance(to_lion, bool) and to_lion is True:
        raise ValueError("Please define a valid parser to Node.")
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


read_funcs = {
    ReaderType.PLAIN: _plain_reader,
    ReaderType.LANGCHAIN: _langchain_reader,
    ReaderType.LLAMAINDEX: _llama_index_reader,
    ReaderType.SELFDEFINED: _self_defined_reader,
}
