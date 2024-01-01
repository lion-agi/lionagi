from enum import Enum
from typing import Union, Callable

from ..bridge.langchain import langchain_loader, from_langchain
from ..bridge.llama_index import llama_index_reader, from_llama_index
from ..utils.sys_util import l_call


class ReaderType(str, Enum):
    DEFAULT = 'default'
    LANGCHAIN = 'langchain'
    LLAMAINDEX = 'llama_index'


def load(reader: Union[str, Callable],
         reader_type=ReaderType.LLAMAINDEX,
         reader_args=[],
         reader_kwargs={},
         load_args=[],
         load_kwargs={},
         to_datanode=True):
    if reader_type == ReaderType.LANGCHAIN:
        nodes = langchain_loader(reader, reader_args, reader_kwargs)
        if to_datanode:
            nodes = l_call(nodes, from_langchain)
        return nodes

    elif reader_type == ReaderType.LLAMAINDEX:
        nodes = llama_index_reader(reader, reader_args, reader_kwargs, load_args, load_kwargs)
        if to_datanode:
            nodes = l_call(nodes, from_llama_index)
        return nodes

    else:
        raise ValueError(f'{reader_type} is not supported. Please choose from {list(ReaderType)}')