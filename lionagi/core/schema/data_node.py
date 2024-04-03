from typing import Any
from lionagi.integrations.bridge import LlamaIndexBridge, LangchainBridge

from lionagi.core.schema.base_node import BaseNode


class DataNode(BaseNode):
    """
    Extends `BaseNode` for integration with llama index and langchain_ formats.

    This class provides additional functionality for converting between `DataNode` instances
    and specific formats utilized by llama index and langchain_, facilitating interoperability
    with these systems.

    Methods:
        - `to_llama_index`: Serializes the `DataNode` for use with llama index.
        - `to_langchain`: Serializes the `DataNode` for use with langchain_.
        - `from_llama_index`: Deserializes a llama index node into a `DataNode`.
        - `from_langchain`: Deserializes a langchain_ document into a `DataNode`.
    """

    def to_llama_index(self, node_type: Any = None, **kwargs) -> Any:
        """
        convert the node for use with llama index.

        Args:
            node_type: The type of node in the llama index format.
            **kwargs: Additional arguments for customization.

        Returns:
            The serialized node in llama index format.

        Examples:
            >>> node = DataNode(content="Example content")
            >>> llama_index_format = node.to_llama_index()
        """
        return LlamaIndexBridge.to_llama_index_node(self, node_type=node_type, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """
        convert the node for use with langchain.

        Args:
            **kwargs: Additional arguments for customization.

        Returns:
            The serialized node in langchain_ document format.

        Examples:
            >>> node = DataNode(content="Example content")
            >>> langchain_format = node.to_langchain()
        """
        return LangchainBridge.to_langchain_document(self, **kwargs)

    @classmethod
    def from_llama_index(cls, llama_node: Any, **kwargs) -> "DataNode":
        """
        convert a llama index node into a `DataNode`.

        Args:
            llama_node: The llama index node to deserialize.
            **kwargs: Additional arguments for customization.

        Returns:
            A `DataNode` instance based on the provided llama index node.

        Examples:
            >>> llama_node = get_some_llama_index_node()
            >>> data_node = DataNode.from_llama_index(llama_node)
        """
        llama_dict = llama_node.to_dict(**kwargs)
        return cls.from_obj(llama_dict)

    @classmethod
    def from_langchain(cls, lc_doc: Any) -> "DataNode":
        """
        convert a langchain_ document into a `DataNode`.

        Args:
            lc_doc: The langchain_ document to deserialize.

        Returns:
            A `DataNode` instance based on the provided langchain_ document.

        Examples:
            >>> lc_doc = get_some_langchain_document()
            >>> data_node = DataNode.from_langchain(lc_doc)
        """
        info_json = lc_doc.to_json()
        info_node = {"lc_id": info_json["id"]}
        info_node = {**info_node, **info_json["kwargs"]}
        return cls(**info_node)
