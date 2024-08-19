from lion_core.converter import Converter

from lionagi.os.libs import to_dict
from .utils import LLAMAINDEX_META_FIELDS


class LlamaIndexNodeConverter(Converter):

    @staticmethod
    def from_obj(cls, obj, **kwargs) -> dict:
        dict_ = to_dict(obj, **kwargs)

        dict_["content"] = dict_.pop("text", None)
        metadata = dict_.pop("metadata", {})

        for field in LLAMAINDEX_META_FIELDS:
            metadata[field] = dict_.pop(field, None)

        metadata["llama_index_class"] = metadata.pop("class_name", None)
        metadata["llama_index_id"] = metadata.pop("id_", None)
        metadata["llama_index_relationships"] = metadata.pop("relationships", None)
        dict_["metadata"] = metadata
        return dict_

    @staticmethod
    def to_obj(self, node_type="TextNode", **kwargs):
        from .textnode import to_llama_index_node

        dict_ = to_dict(self, **kwargs)
        return to_llama_index_node(node_type=node_type, **dict_)
