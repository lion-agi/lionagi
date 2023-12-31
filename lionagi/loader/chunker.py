from enum import Enum
from typing import Union, Callable

from ..bridge.langchain import langchain_text_splitter, from_langchain
from ..bridge.llama_index import llama_index_node_parser, from_llama_index
from ..utils.call_utils import l_call
from ..schema import DataNode


class ChunkerType(str, Enum):
    DEFAULT = 'default'
    LANGCHAIN = 'langchain'
    LLAMAINDEX = 'llama_index'


def _documents_convert(documents, chunker_type):
    for i in range(len(documents)):
        if type(documents[i]) == DataNode:
            if chunker_type == ChunkerType.LLAMAINDEX:
                documents[i] = documents[i].to_llama_index()
            elif chunker_type == ChunkerType.LANGCHAIN:
                documents[i] = documents[i].content
    return documents


def chunk(documents,
          chunker,
          chunker_type=ChunkerType.LLAMAINDEX,
          chunker_args=[],
          chunker_kwargs={},
          to_datanode=True):
    if chunker_type == ChunkerType.LANGCHAIN:
        nodes = langchain_text_splitter(documents, chunker, chunker_args, chunker_kwargs)
        if to_datanode:
            nodes = l_call(nodes, lambda x: DataNode(content=x))
        return nodes

    elif chunker_type == ChunkerType.LLAMAINDEX:
        nodes = llama_index_node_parser(documents, chunker, chunker_args, chunker_kwargs)
        if to_datanode:
            nodes = l_call(nodes, from_llama_index)
        return nodes

    else:
        raise ValueError(f'{chunker_type} is not supported. Please choose from {list(ChunkerType)}')
    