import json
from typing import Union, Callable, List, Any, Dict

from lionagi.schema.base_schema import DataNode
from lionagi.utils.parse_utils import change_key 

def from_llama_index(llama_node: Any, **kwargs: Any) -> DataNode:
    """
    Converts a Llama Index node into a DataNode object.

    Parameters:
        llama_node (Any): The Llama Index node to be converted.
        **kwargs: Additional keyword arguments for JSON serialization.

    Returns:
        DataNode: A DataNode object created from the Llama Index node.
    """
    llama_dict = llama_node.to_dict(**kwargs)
    return DataNode.from_dict(llama_dict)

def to_llama_index_textnode(datanode: DataNode, **kwargs: Any) -> Any:
    """
    Converts a DataNode into a Llama Index TextNode.

    Parameters:
        datanode (DataNode): The DataNode to be converted.
        **kwargs: Additional keyword arguments to be included in the TextNode.

    Returns:
        TextNode: A Llama Index TextNode created from the DataNode.
    """
    # to llama_index textnode
    from llama_index.schema import TextNode

    dnode = datanode.to_dict()
    change_key(dnode, old_key='content', new_key='text')
    change_key(dnode, old_key='node_id', new_key='id_')
    
    dnode = {**dnode, **kwargs}
    return TextNode.from_dict(dnode)

def get_llama_reader(reader: Union[str, Callable]) -> Callable:
    """
    Gets a Llama Index reader function.

    Parameters:
        reader (Union[str, Callable]): The name of the reader function or the reader function itself.
        reader_args (List[Any]): Positional arguments to pass to the reader function.
        reader_kwargs (Dict[str, Any]): Keyword arguments to pass to the reader function.

    Returns:
        Callable: The Llama Index reader function.

    Raises:
        ValueError: If the specified reader is invalid.
    """
    if isinstance(reader, str):
        
        if reader == 'SimpleDirectoryReader':
            from llama_index import SimpleDirectoryReader
            return SimpleDirectoryReader
        else:
            from llama_index import download_loader
            return download_loader(reader)
    return reader

def llama_index_reader(reader: Union[str, Callable], 
                       reader_args: List[Any] = [], 
                       reader_kwargs: Dict[str, Any] = {}, 
                       load_data_args: List[Any] = [], 
                       load_data_kwargs: Dict[str, Any] = {}) -> List[Any]:
    """
    Loads documents using a specified Llama Index reader.

    Parameters:
        reader (Union[str, Callable]): The name of the reader function or the reader function itself.
        reader_args (List[Any]): Positional arguments to pass to the reader function.
        reader_kwargs (Dict[str, Any]): Keyword arguments to pass to the reader function.
        load_data_args (List[Any]): Positional arguments for the load_data method.
        load_data_kwargs (Dict[str, Any]): Keyword arguments for the load_data method.

    Returns:
        List[Any]: A list of documents loaded by the reader.

    Raises:
        ValueError: If the specified reader is invalid or if the reader fails to load documents.
    """
    try:
        reader = get_llama_reader(reader)
    except Exception as e:
        raise ValueError(f'Invalid reader: {reader}, Error: {e}')

    try:
        loader = reader(*reader_args, **reader_kwargs)
        documents = loader.load_data(*load_data_args, **load_data_kwargs)
        return documents
    
    except Exception as e:
        raise ValueError(f'Failed to read. Error: {e}')

def llama_index_node_parser(documents: List[Any], 
                            parser: Union[str, Callable], 
                            parser_args: List[Any] = [], 
                            parser_kwargs: Dict[str, Any] = {}) -> List[Any]:
    """
    Parses documents into nodes using a specified Llama Index node parser.

    Parameters:
        documents (List[Any]): The documents to parse.
        parser (Union[str, Callable]): The name of the parser function or the parser function itself.
        parser_args (List[Any]): Positional arguments to pass to the parser function.
        parser_kwargs (Dict[str, Any]): Keyword arguments to pass to the parser function.

    Returns:
        List[Any]: A list of nodes parsed from the documents.

    Raises:
        ValueError: If the specified parser is invalid or if the parser fails to parse the documents.
    """
    import llama_index.node_parser as node_parser
    import llama_index.text_splitter as text_splitter

    try:
        parser_ = getattr(node_parser, parser)
    except:
        try:
            if isinstance(parser, str):
                parser_ = getattr(text_splitter, parser)
            else:
                parser_ = parser
        except Exception as e:
            raise ValueError(f'Invalid node parser: {parser}. Error: {e}')

    try:
        parser_obj = parser_(*parser_args, **parser_kwargs)
        nodes = parser_obj.get_nodes_from_documents(documents)
        return nodes

    except:
        try:
            parser_obj = parser_.from_defaults(*parser_args, **parser_kwargs)
            nodes = parser_obj.get_nodes_from_documents(documents)
            return nodes
        except Exception as e:
            raise ValueError(f'Failed to parse. Error: {e}')
        