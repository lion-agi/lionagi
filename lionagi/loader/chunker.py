from enum import Enum
from typing import Union, Callable

from ..bridge.langchain import langchain_text_splitter, from_langchain
from ..bridge.llama_index import llama_index_node_parser, from_llama_index
from ..schema.base_schema import DataNode
from ..utils import lcall, file_to_chunks

# define an enum to represent different types of chunkers
class ChunkerType(str, Enum):
    PLAIN = 'plain'                 # default
    LANGCHAIN = 'langchain'         # using langchain functions
    LLAMAINDEX = 'llama_index'      # using llamaindex functions
    SELFDEFINED = 'self_defined'    # create custom functions

# Function to convert documents to a specific format based on the chunker type
def datanodes_convert(documents, chunker_type):
    """
    Converts a lionagi DataNode documents to a specific format based on the chunker type.
    
    Args:
        documents (List[DataNode]): A list of DataNode instances to be converted.
        
        chunker_type (ChunkerType): The chunker type to determine the conversion format.
    
    Returns:
        List[DataNode]: The list of converted DataNode instances.
    """
    for i in range(len(documents)):
        if type(documents[i]) == DataNode:
            if chunker_type == ChunkerType.LLAMAINDEX:
                documents[i] = documents[i].to_llama_index()
            elif chunker_type == ChunkerType.LANGCHAIN:
                documents[i] = documents[i].to_langchain()
    return documents

# Function to chunk text documents
def text_chunker(documents, args, kwargs):
    """
    Chunks text documents into smaller pieces.
    
    Args:
        documents (List[DataNode]): A list of DataNode instances to be chunked.
        args (List[Any]): Positional arguments to be passed to the chunking function.
        kwargs (dict): Keyword arguments to be passed to the chunking function.
    
    Returns:
        List[DataNode]: A list of chunked DataNode instances.
    """
    def chunk_node(node):
        chunks = file_to_chunks(node.to_dict(), *args, **kwargs)
        lcall(chunks, lambda chunk: chunk.pop('node_id'))
        chunk_nodes = lcall(chunks, lambda x: DataNode(**x))
        return chunk_nodes

    nodes = []
    for doc in documents:
        nodes += chunk_node(doc)
    return nodes


def _datanode_parser(nodes, parser):
    """
    Parses raw data into DataNode instances using the provided parser function.
    
    Args:
        nodes (List[Any]): A list of raw data to be parsed.
        parser (Callable): A function that parses raw data into DataNode instances.
    
    Returns:
        List[DataNode]: A list of parsed DataNode instances.
    
    Raises:
        ValueError: If the parser function fails.
    """
    try:
        nodes = parser(nodes)
    except Exception as e:
        raise ValueError(f'DataNode parser {parser} failed. Error:{e}')
    return nodes


def chunk(documents,
          chunker,
          chunker_type=ChunkerType.PLAIN,
          chunker_args=[],
          chunker_kwargs={},
          chunking_kwargs={},
          documents_convert_func=None,
          to_datanode: Union[bool, Callable] = True):
    """
    Chunks documents using the specified chunker and chunker type.
    
    Args:
        documents (List[Any]): A list of documents to be chunked.
        chunker (Callable): The chunking function to be used.
        chunker_type (ChunkerType): The type of the chunker. Defaults to ChunkerType.PLAIN.
        chunker_args (List[Any]): Positional arguments for the chunker function. Defaults to an empty list.
        chunker_kwargs (dict): Keyword arguments for the chunker function. Defaults to an empty dict.
        chunking_kwargs (dict): Additional keyword arguments for the chunking process. Defaults to an empty dict.
        documents_convert_func (Callable): A function to convert documents to a specific format. Defaults to None.
        to_datanode (Union[bool, Callable]): Determines whether to convert the result into DataNode instances, or
                                             a callable to convert the result. Defaults to True.
    
    Returns:
        List[DataNode]: A list of chunked DataNode instances after applying the chunker.
    
    Raises:
        ValueError: If the chunker fails or an unsupported chunker type is provided.
    """
    if chunker_type == ChunkerType.PLAIN:
        try:
            if chunker == 'text_chunker':
                chunker = text_chunker
            nodes = chunker(documents, chunker_args, chunker_kwargs)
            return nodes
        except Exception as e:
            raise ValueError(f'Reader {chunker} is currently not supported. Error: {e}')
    if chunker_type == ChunkerType.LANGCHAIN:
        if documents_convert_func:
            documents = documents_convert_func(documents, 'langchain')
        nodes = langchain_text_splitter(documents, chunker, chunker_args, chunker_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            if isinstance(documents, str):
                nodes = lcall(nodes, lambda x: DataNode(content=x))
            else:
                nodes = lcall(nodes, from_langchain)
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    elif chunker_type == ChunkerType.LLAMAINDEX:
        if documents_convert_func:
            documents = documents_convert_func(documents, 'llama_index')
        nodes = llama_index_node_parser(documents, chunker, chunker_args, chunker_kwargs, chunking_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            nodes = lcall(nodes, from_llama_index)
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    elif chunker_type == ChunkerType.SELFDEFINED:
        try:
            splitter = chunker(*chunker_args, **chunker_kwargs)
            nodes = splitter.split(documents, **chunking_kwargs)
        except Exception as e:
            raise ValueError(f'Self defined chunker {chunker} is not valid. Error: {e}')

        if isinstance(to_datanode, bool) and to_datanode is True:
            raise ValueError(f'Please define a valid parser to DataNode.')
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    else:
        raise ValueError(f'{chunker_type} is not supported. Please choose from {list(ChunkerType)}')
    