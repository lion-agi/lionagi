from .base_node import BaseNode
from typing import Any


class DataNode(BaseNode):

    def to_llama_index(self, **kwargs) -> Any:
        """
        Converts node to llama index format.

        Args:
            **kwargs: Variable length argument list.

        Returns:
            The llama index representation of the node.

        Examples:
            node = DataNode()
            llama_index = node.to_llama_index()
        """
        from lionagi.bridge.llama_index import to_llama_index_textnode
        return to_llama_index_textnode(self, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """
        Converts node to langchain document format.

        Args:
            **kwargs: Variable length argument list.

        Returns:
            The langchain document representation of the node.

        Examples:
            node = DataNode()
            langchain_doc = node.to_langchain()
        """
        from lionagi.bridge.langchain import to_langchain_document
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


class File(DataNode):

    ...
    

class Chunk(DataNode):

    ...    
