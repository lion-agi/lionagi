from typing import Any, TypeVar

from lionagi.integrations.bridge import LlamaIndexBridge, LangchainDocument
from .from_obj_mixins import BaseFromObjectMixin
from .to_obj_mixins import BaseToObjectMixin


T = TypeVar("T")


class DataNodeToObjMixin(BaseToObjectMixin):

    def to_llama_index(self, node_type=None, **kwargs) -> Any:
        return LlamaIndexBridge.to_llama_index_node(self, node_type=node_type, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        return LangchainBridge.to_langchain_document(self, **kwargs)


class DataNodeFromObjMixin(BaseFromObjectMixin):

    @BaseFromObjectMixin.from_obj.register(LangchainDocument)
    @classmethod
    def _from_langchain(cls, lc_doc) -> "T":
        info_json = lc_doc.to_json()
        info_node = {"lc_id": info_json["id"]}
        info_node = {**info_node, **info_json["kwargs"]}
        return cls(**info_node)
