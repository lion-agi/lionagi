from typing import Type, Any
from pathlib import Path
from lionagi.os.primitives import Pile, Node


class LlamaIndexBridge:

    from .utils import LLAMAINDEX_META_FIELDS

    meta_fields = LLAMAINDEX_META_FIELDS

    @staticmethod
    def to_llamaindex(*, node_type=None, **kwargs) -> Any:
        """convert a lionagi node to llamaindex node"""
        from .textnode import to_llama_index_node

        return to_llama_index_node(node_type=node_type, **kwargs)

    @staticmethod
    def converter() -> Type:
        from .converter import LlamaIndexNodeConverter

        return LlamaIndexNodeConverter

    @staticmethod
    def load_vectorstore(dir: str | Path) -> Pile[Node]:
        """return a pile of lion node"""
        from .loader import load_llamaindex_vector_store

        return load_llamaindex_vector_store(dir)

    @staticmethod
    def load_file(
        reader=None,
        /,
        *args,
        reader_args=[],
        reader_kwargs={},
        **kwargs,
    ) -> list:
        """return list of llamaindex documents"""
        from .loader import llamaindex_loader

        return llamaindex_loader(
            reader,
            *args,
            reader_args=reader_args,
            reader_kwargs=reader_kwargs,
            **kwargs,
        )

    @staticmethod
    def read_file(
        reader=None,
        /,
        reader_args=[],
        reader_kwargs={},
        loader_args=[],
        loader_kwargs={},
    ) -> Pile[Node]:
        """return a pile of lion node"""
        from .loader import llamaindex_reader

        return llamaindex_reader(
            reader,
            reader_args=reader_args,
            reader_kwargs=reader_kwargs,
            loader_args=loader_args,
            loader_kwargs=loader_kwargs,
        )

    @staticmethod
    def parse_node(
        documents,
        /,
        node_parser,
        *args,
        **kwargs,
    ) -> list:
        """return a list of parsed llamaindex nodes"""
        from .node_parser import llamaindex_parse_node

        return llamaindex_parse_node(
            documents,
            node_parser=node_parser,
            *args,
            **kwargs,
        )

    @staticmethod
    def create_index(
        nodes: list,
        *args,  # additional index init args
        index_type: Type | None = None,
        llm=None,
        model_config: dict = None,
        return_llama_nodes=False,
        **kwargs,  # additional index init kwargs
    ) -> Any | tuple:
        """in take a list of llamaindex/lion nodes and return an index, and optionally the llamaindex nodes"""

        from .index import create_llamaindex

        return create_llamaindex(
            nodes,
            *args,
            index_type=index_type,
            llm=llm,
            model_config=model_config,
            return_llama_nodes=return_llama_nodes,
            **kwargs,
        )
