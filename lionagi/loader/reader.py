from enum import Enum
from typing import Union, Callable

from lionagi.bridge.langchain import langchain_loader, from_langchain
from lionagi.bridge.llama_index import llama_index_reader, from_llama_index
from lionagi.utils.call_util import lcall


class ReaderType(str, Enum):
    # DEFAULT = 'default'
    LANGCHAIN = 'langchain'
    LLAMAINDEX = 'llama_index'
    SELFDEFINED = 'self_defined'


def _datanode_parser(nodes, parser):
    try:
        nodes = parser(nodes)
    except Exception as e:
        raise ValueError(f'DataNode parser {parser} failed. Error:{e}')
    return nodes


def _to_datanode_temp(nodes, func):
    output = []
    for node in nodes:
        output.append(func(node))
    return output


def load(reader: Union[str, Callable],
         reader_type=ReaderType.LLAMAINDEX,
         reader_args=[],
         reader_kwargs={},
         load_args=[],
         load_kwargs={},
         to_datanode: Union[bool, Callable] = True):
    if reader_type == ReaderType.LANGCHAIN:
        nodes = langchain_loader(reader, reader_args, reader_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            # nodes = lcall(nodes, from_langchain)
            nodes = _to_datanode_temp(nodes, from_langchain)
        elif isinstance(to_datanode, Callable):
            nodes = _datanode_parser(nodes, to_datanode)
        return nodes

    elif reader_type == ReaderType.LLAMAINDEX:
        nodes = llama_index_reader(reader, reader_args, reader_kwargs, load_args, load_kwargs)
        if isinstance(to_datanode, bool) and to_datanode is True:
            # nodes = lcall(nodes, from_llama_index)
            nodes = _to_datanode_temp(nodes, from_llama_index)
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
