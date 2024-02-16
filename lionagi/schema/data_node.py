from typing import Any
from lionagi.schema.base_node import BaseNode
from lionagi.bridge.llama_index import to_llama_index_textnode
from lionagi.bridge.langchain import to_langchain_document


class DataNode(BaseNode):
    """
    Represents a data node with extended functionality for integration with llama index and langchain formats.

    This class extends `BaseNode` to include methods for converting between DataNode instances and specific formats
    used by llama index and langchain, facilitating interoperability with these systems.

    Methods provided allow for serialization to and deserialization from these formats, supporting a variety of use cases.
    """
    
    def to_llama_index(self, **kwargs) -> Any:
        """
        Converts the node to a format compatible with llama index.

        This method serializes the DataNode into a format recognized by the llama index system, allowing for
        integration and usage within that ecosystem.

        Args:
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The llama index format representation of the node.

        Examples:
            >>> node = DataNode(content="Example content")
            >>> llama_index = node.to_llama_index()
        """
        return to_llama_index_textnode(self, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """
        Converts the node to a langchain document format.

        This method serializes the DataNode into a document format used by langchain, enabling the node's
        use within langchain applications and workflows.

        Args:
            **kwargs: Additional keyword arguments for customization.

        Returns:
            Any: The langchain document representation of the node.

        Examples:
            >>> node = DataNode(content="Example content")
            >>> langchain_doc = node.to_langchain()
        """
        return to_langchain_document(self, **kwargs)

    @classmethod
    def from_llama_index(cls, llama_node: Any, **kwargs) -> "DataNode":
        """
        Creates a DataNode instance from a llama index node.

        Args:
            llama_node: The llama index node object.
            **kwargs: Variable length argument list.

        Returns:
            An instance of DataNode.

        Examples:
            llama_node = SomeLlamaIndexNode()
            data_node = DataNode.from_llama_index(llama_node)
        """
        llama_dict = llama_node.to_dict(**kwargs)
        return cls.from_dict(llama_dict)

    @classmethod
    def from_langchain(cls, lc_doc: Any) -> "DataNode":
        """
        Creates a DataNode instance from a langchain document.

        Args:
            lc_doc: The langchain document object.

        Returns:
            An instance of DataNode.

        Examples:
            lc_doc = SomeLangChainDocument()
            data_node = DataNode.from_langchain(lc_doc)
        """
        info_json = lc_doc.to_json()
        info_node = {'lc_id': info_json['id']}
        info_node = {**info_node, **info_json['kwargs']}
        return cls(**info_node)
    