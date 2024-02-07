from typing import Union, Callable, List, Any, Dict, TypeVar
from ..utils.sys_util import change_dict_key, install_import, is_package_installed
from ..schema.data_node import DataNode


T = TypeVar('T', bound='DataNode')

def from_llama_index(llama_node: Any, **kwargs: Any) -> T:
    """
    Converts a Llama Index node into a DataNode object.

    Args:
        llama_node (Any): The Llama Index node to be converted.
        **kwargs: Additional keyword arguments for JSON serialization.

    Returns:
        T: A DataNode object created from the Llama Index node.

    Example:
        llama_node = LlamaIndexNode(...)
        datanode = from_llama_index(llama_node, serialize_dates=True)
    """
    llama_dict = llama_node.to_dict(**kwargs)
    return DataNode.from_dict(llama_dict)

def to_llama_index_textnode(datanode: T, **kwargs: Any) -> Any:
    """
    Converts a DataNode into a Llama Index TextNode.

    Args:
        datanode (T): The DataNode to be converted.
        **kwargs: Additional keyword arguments to be included in the TextNode.

    Returns:
        Any: A Llama Index TextNode created from the DataNode.

    Example:
        datanode = DataNode(...)
        textnode = to_llama_index_textnode(datanode, additional_arg=1)
    """
    try:
        from llama_index.schema import TextNode
    except ImportError:
        try:
            install_import(
                package_name='llama_index', 
                module_name='schema',
                import_name='TextNode'
            )
            from llama_index.schema import TextNode
        except Exception as e:
            raise ImportError(f'Unable to import required module from llama_index. Please make sure that llama_index is installed. Error: {e}')

    dnode = datanode.to_dict()
    change_dict_key(dnode, old_key='content', new_key='text')
    change_dict_key(dnode, old_key='node_id', new_key='id_')
    dnode['text'] = str(dnode['text'])
    
    dnode = {**dnode, **kwargs}
    return TextNode.from_dict(dnode)

def get_llama_reader(reader: Union[str, Callable]) -> Callable:
    """
    Gets a Llama Index reader function.

    Args:
        reader (Union[str, Callable]): The name of the reader function or the reader function itself.

    Returns:
        Callable: The Llama Index reader function.

    Raises:
        ValueError: If the specified reader is invalid.

    Example:
        reader = get_llama_reader("SimpleDirectoryReader")
        # or for a custom function
        def custom_reader(): pass
        reader = get_llama_reader(custom_reader)
    """
    
    try:
        if isinstance(reader, str):
            if reader == 'SimpleDirectoryReader':
                try:
                    from llama_index import SimpleDirectoryReader
                    return SimpleDirectoryReader
                except ImportError or ModuleNotFoundError:
                    try:
                        install_import(
                            package_name='llama_index',
                            import_name='SimpleDirectoryReader'
                        )
                        from llama_index import SimpleDirectoryReader
                        return SimpleDirectoryReader
                    except Exception as e:
                        raise ImportError(f'Failed to import SimpleDirectoryReader. Error: {e}')
            else:                
                try:
                    from llama_index import download_loader
                    return download_loader(reader)
                except ImportError:
                    try:
                        install_import(
                            package_name='llama_index',
                            import_name='download_loader'
                        )
                        return download_loader(reader)
                    except Exception as e:
                        raise ImportError(f'Failed to import download_loader from LlamaIndex. Error: {e}')
        else:
            return reader
    except Exception as e:
        raise ValueError(f'Invalid reader: {reader}, Error: {e}')

def llama_index_reader(reader: Union[str, Callable], 
                       reader_args: List[Any] = [], 
                       reader_kwargs: Dict[str, Any] = {}, 
                       load_data_args: List[Any] = [], 
                       load_data_kwargs: Dict[str, Any] = {}) -> List[Any]:
    """
    Loads documents using a specified Llama Index reader.

    Args:
        reader (Union[str, Callable]): The name of the reader function or the reader function itself.
        reader_args (List[Any]): Positional arguments to pass to the reader function.
        reader_kwargs (Dict[str, Any]): Keyword arguments to pass to the reader function.
        load_data_args (List[Any]): Positional arguments for the load_data method.
        load_data_kwargs (Dict[str, Any]): Keyword arguments for the load_data method.

    Returns:
        List[Any]: A list of documents loaded by the reader.

    Raises:
        ValueError: If the specified reader is invalid or if the reader fails to load documents.

    Example:
        documents = llama_index_reader("SimpleDirectoryReader", reader_args=["/path/to/data"])
    """
    reader = get_llama_reader(reader)

    try:
        loader = reader(*reader_args, **reader_kwargs)
        documents = loader.load_data(*load_data_args, **load_data_kwargs)
        return documents
    
    except Exception as e:
        raise ValueError(f'Failed to read. Error: {e}')

def get_llama_parser(parser: Union[str, Callable]) -> Callable:
    """
    Gets a Llama Index parser function or object.

    Args:
        parser (Union[str, Callable]): The name of the parser function or the parser function itself.

    Returns:
        Callable: The Llama Index parser function or object.

    Raises:
        ValueError: If the specified parser is invalid.

    Example:
        parser = get_llama_parser("DefaultNodeParser")
        # or for a custom function
        def custom_parser(): pass
        parser = get_llama_parser(custom_parser)
    """
    
    try:
        import llama_index.node_parser as node_parser
    except ImportError:
        try:
            install_import(
                package_name='llama_index',
                module_name='node_parser'
            )
            import llama_index.node_parser as node_parser
        except ImportError:
            raise ImportError('Failed to import Llama Index. Please install Llama Index to use this function.')
        except Exception as e:
            raise ValueError(f'Invalid node parser: {parser}. Error: {e}')

    try:
        import llama_index.text_splitter as text_splitter
    except ImportError:
        try:
            install_import(
                package_name='llama_index',
                module_name='text_splitter'
            )
            import llama_index.text_splitter as text_splitter
        except ImportError:
            raise ImportError('Failed to import Llama Index. Please install Llama Index to use this function.')
        
    try:
        if parser == 'CodeSplitter':
            if not is_package_installed('tree_sitter_languages'):
                install_import(package_name='tree_sitter_languages')
                
        a = getattr(node_parser, parser)
        if a is not None:
            return a
        else:
            raise ImportError(f'Failed to import {parser} from Llama Index.')
    except Exception as e1:
        try:
            if isinstance(parser, str):
                return getattr(text_splitter, parser)
            else:
                return parser
        except Exception as e2:
            raise ValueError(f'Invalid node parser: {parser}. Error: {e1}, {e2}')


def llama_index_node_parser(documents: List[Any], 
                            parser: Union[str, Callable], 
                            parser_args: List[Any] = [], 
                            parser_kwargs: Dict[str, Any] = {},
                            parsing_kwargs: Dict[str, Any] = {}) -> List[Any]:
    """
    Parses documents into nodes using a specified Llama Index node parser.

    Args:
        documents (List[Any]): The documents to parse.
        parser (Union[str, Callable]): The name of the parser function or the parser function itself.
        parser_args (List[Any]): Positional arguments to pass to the parser function.
        parser_kwargs (Dict[str, Any]): Keyword arguments to pass to the parser function.
        parsing_kwargs (Dict[str, Any]): Keyword arguments for the parsing process.

    Returns:
        List[Any]: A list of nodes parsed from the documents.

    Raises:
        ValueError: If the specified parser is invalid or if the parser fails to parse the documents.

    Example:
        nodes = llama_index_node_parser(documents, "DefaultNodeParser")
    """

    try:
        parser = get_llama_parser(parser)
        parser_obj = parser(*parser_args, **parser_kwargs)
        nodes = parser_obj.get_nodes_from_documents(documents, **parsing_kwargs)
        return nodes

    except ImportError as e:
        module_name = str(e).split("\'")[-2]
        try:
            install_import(package_name=module_name)
            parser = get_llama_parser(parser)
            parser_obj = parser(*parser_args, **parser_kwargs)
            nodes = parser_obj.get_nodes_from_documents(documents, **parsing_kwargs)
            return nodes
        except Exception as e:
            raise ImportError(f'Failed to install and import {module_name}. Error: {e}')
            
            
    except Exception as e1:
        try:
            parser_obj = parser.from_defaults(*parser_args, **parser_kwargs)
            nodes = parser_obj.get_nodes_from_documents(documents, **parsing_kwargs)
            return nodes
        except Exception as e2:
            raise ValueError(f'Failed to parse. Error: {e1}, {e2}')
        