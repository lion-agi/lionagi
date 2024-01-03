from enum import Enum
from typing import Union, Callable

from lionagi.bridge.langchain import langchain_loader, from_langchain
from lionagi.bridge.llama_index import llama_index_reader, from_llama_index
from lionagi.utils.call_util import lcall
from lionagi.utils.load_utils import dir_to_nodes


class ReaderType(str, Enum):
    PLAIN = 'PLAIN'
    LANGCHAIN = 'langchain'
    LLAMAINDEX = 'llama_index'
    SELFDEFINED = 'self_defined'


def _datanode_parser(nodes, parser):
    """
    Parses a list of nodes using the given parser function.
    
    Args:
        nodes (List[Any]): The list of nodes to be parsed.
        
        parser (Callable): The parser function to transform nodes into DataNode instances.
    
    Returns:
        List[Any]: A list of parsed nodes.
    
    Raises:
        ValueError: If the parser function fails.
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
        args (List[Any]): Positional arguments for the dir_to_nodes function.
        
        kwargs (dict): Keyword arguments for the dir_to_nodes function.
    
    Returns:
        List[Any]: A list of DataNode instances.
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
        reader (Union[str, Callable]): The reader function or its name as a string.
        
        reader_type (ReaderType): The type of the reader. Defaults to ReaderType.PLAIN.
        
        reader_args (List[Any]): Positional arguments for the reader function. Defaults to an empty list.
        
        reader_kwargs (dict): Keyword arguments for the reader function. Defaults to an empty dict.
        
        load_args (List[Any]): Positional arguments for the loader function. Defaults to an empty list.
        
        load_kwargs (dict): Keyword arguments for the loader function. Defaults to an empty dict.
        
        to_datanode (Union[bool, Callable]): Determines whether to convert the result into DataNode instances, or
                                             a callable to convert the result. Defaults to True.
    
    Returns:
        List[Any]: A list of loaded and potentially parsed documents.
    
    Raises:
        ValueError: If the reader fails or an unsupported reader type is provided.
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
