from typing import Any, TypeVar

from lionagi.core.schema.base_node import BaseNode
from lionagi.integrations.bridge import LlamaIndexBridge, LangchainBridge
from lionagi.core.schema.base_mixin import DataNodeFromObjectMixin


T = TypeVar("T")

class DataNode(BaseNode, DataNodeFromObjectMixin):

    def to_llama_index(self, node_type=None, **kwargs) -> Any:
        return LlamaIndexBridge.to_llama_index_node(self, node_type=node_type, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        return LangchainBridge.to_langchain_document(self, **kwargs)
