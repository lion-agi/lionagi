import json
from typing import Union, Callable

from lionagi.schema.base_schema import DataNode


def from_llama_index(llama_node, **kwargs):
    info_json = json.loads(llama_node.json(**kwargs))
    return DataNode(**info_json)


def to_llama_index_textnode(datanode, **kwargs):
    # to llama_index textnode
    from llama_index.schema import TextNode

    dnode = json.loads(datanode.to_json())
    dnode['text'] = dnode.pop('content')
    dnode['id_'] = dnode.pop('node_id')
    dnode = {**dnode, **kwargs}
    return TextNode(**dnode)


def llama_index_reader(reader: Union[str, Callable], reader_args=[], reader_kwargs={}, load_data_args=[], load_data_kwargs={}):
    try:
        if reader == 'SimpleDirectoryReader':
            from llama_index import SimpleDirectoryReader
            reader_ = SimpleDirectoryReader
        elif isinstance(reader, str):
            from llama_index import download_loader
            reader_ = download_loader(reader)
        else:
            reader_ = reader
    except Exception as e:
        raise ValueError(f'Invalid reader: {reader}, Error: {e}')

    try:
        loader = reader_(*reader_args, **reader_kwargs)
        documents = loader.load_data(*load_data_args, **load_data_kwargs)
        return documents
    except Exception as e:
        raise ValueError(f'Failed to read. Error: {e}')


def llama_index_node_parser(documents, parser: Union[str, Callable], parser_args=[], parser_kwargs={}):
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