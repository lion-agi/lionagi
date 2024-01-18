from typing import Union, Callable

from ..utils import lcall
from ..bridge import langchain_loader, from_langchain, llama_index_reader, from_llama_index
from .load_util import dir_to_nodes, ReaderType


def _datanode_parser(nodes, parser):
    """
    Parses raw data into DataNode instances using the provided parser function.

    Args:
        nodes: The list of raw data to be parsed.
        parser: The parser function to transform nodes into DataNode instances.

    Returns:
        A list of parsed DataNode instances.

    Raises:
        ValueError: If the parser function fails.

    Example usage:
        >>> raw_nodes = [{'content': 'Example content'}]
        >>> parser = lambda x: [DataNode(**node) for node in x]
        >>> datanodes = _datanode_parser(raw_nodes, parser)
    """
    try:
        nodes = parser(nodes)
    except Exception as e:
        raise ValueError(f'DataNode parser {parser} failed. Error:{e}')
    return nodes

def text_reader(args, kwargs):
    """
    Reads text files from a directory and converts them to DataNode instances.

    Args:
        args: Positional arguments for the dir_to_nodes function.
        kwargs: Keyword arguments for the dir_to_nodes function.

    Returns:
        A list of DataNode instances.

    Example usage:
        >>> args = ['path/to/text/files']
        >>> kwargs = {'file_extension': 'txt'}
        >>> nodes = text_reader(args, kwargs)
    """
    return dir_to_nodes(*args, **kwargs)


def load(reader: Union[str, Callable],
         reader_type=ReaderType.PLAIN,
         reader_args=[],
         reader_kwargs={},
         load_args=[],
         load_kwargs={},
         to_datanode: Union[bool, Callable] = True):
    """
    Loads documents using the specified reader and reader type.

    Args:
        reader: The reader function or its name as a string.
        reader_type: The type of the reader. Defaults to ReaderType.PLAIN.
        reader_args: Positional arguments for the reader function. Defaults to an empty list.
        reader_kwargs: Keyword arguments for the reader function. Defaults to an empty dict.
        load_args: Positional arguments for the loader function. Defaults to an empty list.
        load_kwargs: Keyword arguments for the loader function. Defaults to an empty dict.
        to_datanode: Determines whether to convert the result into DataNode instances, or
                     a callable to convert the result. Defaults to True.

    Returns:
        A list of loaded and potentially parsed documents.

    Raises:
        ValueError: If the reader fails or an unsupported reader type is provided.

    Example usage:
        >>> reader = 'text_reader'
        >>> reader_args = ['path/to/text/files']
        >>> reader_kwargs = {'file_extension': 'txt'}
        >>> nodes = load(reader, reader_args=reader_args, reader_kwargs=reader_kwargs)
    """
    if reader_type == ReaderType.PLAIN:
        try:
            if reader == 'text_reader':
                reader = text_reader
            nodes = reader(reader_args, reader_kwargs)
            return nodes
        except Exception as e:
            raise ValueError(f'Reader {reader} is currently not supported. Error: {e}')
    if reader_type == ReaderType.LANGCHAIN:
        nodes = langchain_loader(reader, reader_args, reader_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            nodes = lcall(nodes, from_langchain)
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    elif reader_type == ReaderType.LLAMAINDEX:
        nodes = llama_index_reader(reader, reader_args, reader_kwargs, load_args, load_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            nodes = lcall(nodes, from_llama_index)
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    elif reader_type == ReaderType.SELFDEFINED:
        try:
            loader = reader(*reader_args, **reader_kwargs)
            nodes = loader.load(*load_args, **load_kwargs)
        except Exception as e:
            raise ValueError(f'Self defined reader {reader} is not valid. Error: {e}')

        if isinstance(to_datanode, bool) and to_datanode is True:
            raise ValueError(f'Please define a valid parser to DataNode.')
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    else:
        raise ValueError(f'{reader_type} is not supported. Please choose from {list(ReaderType)}')
