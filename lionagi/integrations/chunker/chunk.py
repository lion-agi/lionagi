from collections.abc import Callable
from typing import Union

from lionagi.core.collections import pile
from lionagi.core.generic import Node
from lionagi.libs import func_call
from lionagi.libs.ln_convert import to_list

from ..bridge.langchain_.langchain_bridge import LangchainBridge
from ..bridge.llamaindex_.llama_index_bridge import LlamaIndexBridge
from ..loader.load_util import ChunkerType, _datanode_parser, file_to_chunks


def datanodes_convert(documents, chunker_type):
    """
    Converts documents to the specified chunker type.

    Args:
        documents (list): List of documents to be converted.
        chunker_type (ChunkerType): The type of chunker to convert the documents to.

    Returns:
        list: The converted documents.

    Example usage:
        >>> documents = [Node(...), Node(...)]
        >>> converted_docs = datanodes_convert(documents, ChunkerType.LLAMAINDEX)
    """
    for i in range(len(documents)):
        if type(documents[i]) == Node:
            if chunker_type == ChunkerType.LLAMAINDEX:
                documents[i] = documents[i].to_llama_index()
            elif chunker_type == ChunkerType.LANGCHAIN:
                documents[i] = documents[i].to_langchain()
    return documents


def text_chunker(documents, args, kwargs):
    """
    Chunks text documents into smaller pieces.

    Args:
        documents (list): List of documents to be chunked.
        args (tuple): Positional arguments for the chunking function.
        kwargs (dict): Keyword arguments for the chunking function.

    Returns:
        pile: A pile of chunked Node instances.

    Example usage:
        >>> documents = [Node(...), Node(...)]
        >>> chunked_docs = text_chunker(documents, args, kwargs)
    """

    def chunk_node(node):
        chunks = file_to_chunks(node.to_dict(), *args, **kwargs)
        func_call.lcall(chunks, lambda chunk: chunk.pop("ln_id"))
        return [Node.from_obj({**chunk}) for chunk in chunks]

    a = to_list(
        [chunk_node(doc) for doc in documents], flatten=True, dropna=True
    )
    return pile(a)


def chunk(
    docs,
    field: str = "content",
    chunk_size: int = 1500,
    overlap: float = 0.1,
    threshold: int = 200,
    chunker="text_chunker",
    chunker_type=ChunkerType.PLAIN,
    chunker_args=None,
    chunker_kwargs=None,
    chunking_kwargs=None,
    documents_convert_func=None,
    to_lion: bool | Callable = True,
):
    """
    Chunks documents using the specified chunker.

    Args:
        docs (list): List of documents to be chunked.
        field (str, optional): The field to chunk. Defaults to "content".
        chunk_size (int, optional): The size of each chunk. Defaults to 1500.
        overlap (float, optional): The overlap between chunks. Defaults to 0.1.
        threshold (int, optional): The threshold for chunking. Defaults to 200.
        chunker (str, optional): The chunker function or its name. Defaults to "text_chunker".
        chunker_type (ChunkerType, optional): The type of chunker to use. Defaults to ChunkerType.PLAIN.
        chunker_args (list, optional): Positional arguments for the chunker function. Defaults to None.
        chunker_kwargs (dict, optional): Keyword arguments for the chunker function. Defaults to None.
        chunking_kwargs (dict, optional): Additional keyword arguments for chunking. Defaults to None.
        documents_convert_func (Callable, optional): Function to convert documents. Defaults to None.
        to_lion (bool | Callable, optional): Whether to convert the data to Node instances or a custom parser. Defaults to True.

    Returns:
        pile: A pile of chunked Node instances.

    Raises:
        ValueError: If the chunker_type is not supported.

    Example usage:
        >>> chunked_docs = chunk(docs, field='text', chunk_size=1000, overlap=0.2)
    """

    if chunker_args is None:
        chunker_args = []
    if chunker_kwargs is None:
        chunker_kwargs = {}
    if chunking_kwargs is None:
        chunking_kwargs = {}

    if chunker_type == ChunkerType.PLAIN:
        chunker_kwargs["field"] = field
        chunker_kwargs["chunk_size"] = chunk_size
        chunker_kwargs["overlap"] = overlap
        chunker_kwargs["threshold"] = threshold
        return chunk_funcs[ChunkerType.PLAIN](
            docs, chunker, chunker_args, chunker_kwargs
        )

    elif chunker_type == ChunkerType.LANGCHAIN:
        return chunk_funcs[ChunkerType.LANGCHAIN](
            docs,
            documents_convert_func,
            chunker,
            chunker_args,
            chunker_kwargs,
            to_lion,
        )

    elif chunker_type == ChunkerType.LLAMAINDEX:
        return chunk_funcs[ChunkerType.LLAMAINDEX](
            docs,
            documents_convert_func,
            chunker,
            chunker_args,
            chunker_kwargs,
            to_lion,
        )

    elif chunker_type == ChunkerType.SELFDEFINED:
        return chunk_funcs[ChunkerType.SELFDEFINED](
            docs,
            chunker,
            chunker_args,
            chunker_kwargs,
            chunking_kwargs,
            to_lion,
        )

    else:
        raise ValueError(
            f"{chunker_type} is not supported. Please choose from {list(ChunkerType)}"
        )


def _self_defined_chunker(
    documents,
    chunker,
    chunker_args,
    chunker_kwargs,
    chunking_kwargs,
    to_lion: bool | Callable,
):
    """
    Chunks documents using a self-defined chunker.

    Args:
        documents (list): List of documents to be chunked.
        chunker (str | Callable): The chunker function or its name.
        chunker_args (list): Positional arguments for the chunker function.
        chunker_kwargs (dict): Keyword arguments for the chunker function.
        chunking_kwargs (dict): Additional keyword arguments for chunking.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of chunked Node instances or custom parsed nodes.

    Raises:
        ValueError: If the self-defined chunker is not valid.

    Example usage:
        >>> chunked_docs = _self_defined_chunker(docs, custom_chunker, ['arg1'], {'key': 'value'}, {}, custom_parser)
    """
    try:
        splitter = chunker(*chunker_args, **chunker_kwargs)
        nodes = splitter.split(documents, **chunking_kwargs)
    except Exception as e:
        raise ValueError(
            f"Self defined chunker {chunker} is not valid. Error: {e}"
        ) from e

    if isinstance(to_lion, bool) and to_lion is True:
        raise ValueError("Please define a valid parser to Node.")
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


def _llama_index_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
):
    """
    Chunks documents using a LlamaIndex chunker.

    Args:
        documents (list): List of documents to be chunked.
        documents_convert_func (Callable): Function to convert documents.
        chunker (str | Callable): The chunker function or its name.
        chunker_args (list): Positional arguments for the chunker function.
        chunker_kwargs (dict): Keyword arguments for the chunker function.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of chunked Node instances or custom parsed nodes.

    Example usage:
        >>> chunked_docs = _llama_index_chunker(docs, convert_func, llama_chunker, ['arg1'], {'key': 'value'}, True)
    """
    if documents_convert_func:
        documents = documents_convert_func(documents, "llama_index")
    nodes = LlamaIndexBridge.llama_index_parse_node(
        documents, chunker, chunker_args, chunker_kwargs
    )

    if isinstance(to_lion, bool) and to_lion is True:
        nodes = [Node.from_llama_index(i) for i in nodes]
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


def _langchain_chunker(
    documents,
    documents_convert_func,
    chunker,
    chunker_args,
    chunker_kwargs,
    to_lion: bool | Callable,
):
    """
    Chunks documents using a Langchain chunker.

    Args:
        documents (list): List of documents to be chunked.
        documents_convert_func (Callable): Function to convert documents.
        chunker (str | Callable): The chunker function or its name.
        chunker_args (list): Positional arguments for the chunker function.
        chunker_kwargs (dict): Keyword arguments for the chunker function.
        to_lion (bool | Callable): Whether to convert the data to Node instances or a custom parser.

    Returns:
        pile: A pile of chunked Node instances or custom parsed nodes.

    Example usage:
        >>> chunked_docs = _langchain_chunker(docs, convert_func, langchain_chunker, ['arg1'], {'key': 'value'}, True)
    """
    if documents_convert_func:
        documents = documents_convert_func(documents, "langchain")
    nodes = LangchainBridge.langchain_text_splitter(
        documents, chunker, chunker_args, chunker_kwargs
    )
    if isinstance(to_lion, bool) and to_lion is True:
        if isinstance(documents, str):
            nodes = [Node(content=i) for i in nodes]
        else:
            nodes = [Node.from_langchain(i) for i in nodes]
    elif isinstance(to_lion, Callable):
        nodes = _datanode_parser(nodes, to_lion)
    return nodes


def _plain_chunker(documents, chunker, chunker_args, chunker_kwargs):
    """
    Chunks documents using a plain chunker.

    Args:
        documents (list): List of documents to be chunked.
        chunker (str | Callable): The chunker function or its name.
        chunker_args (list): Positional arguments for the chunker function.
        chunker_kwargs (dict): Keyword arguments for the chunker function.

    Returns:
        pile: A pile of chunked Node instances.

    Raises:
        ValueError: If the chunker is not supported.

    Example usage:
        >>> chunked_docs = _plain_chunker(docs, 'text_chunker', ['arg1'], {'key': 'value'})
    """
    try:
        if chunker == "text_chunker":
            chunker = text_chunker
        return chunker(documents, chunker_args, chunker_kwargs)
    except Exception as e:
        raise ValueError(
            f"Reader {chunker} is currently not supported. Error: {e}"
        ) from e


chunk_funcs = {
    ChunkerType.PLAIN: _plain_chunker,
    ChunkerType.LANGCHAIN: _langchain_chunker,
    ChunkerType.LLAMAINDEX: _llama_index_chunker,
    ChunkerType.SELFDEFINED: _self_defined_chunker,
}
