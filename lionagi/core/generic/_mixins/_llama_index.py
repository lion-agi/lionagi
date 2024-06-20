from typing import Any, Type
from lionagi.os.lib.sys_util import change_dict_key
from lionagi.os._setting.meta_fields import llama_meta_fields


class LlamaIndexComponentMixin:

    def to_llama_index_node(self, **kwargs) -> Any:
        """Serializes this node for LlamaIndex."""
        from lionagi.app.LlamaIndex.bridge import LlamaIndexBridge

        return LlamaIndexBridge.to_llama_index_node(self, **kwargs)

    @classmethod
    def _from_llama_index(cls, obj: Any):
        """Create a Component instance from a LlamaIndex object."""
        dict_ = obj.to_dict()

        change_dict_key(dict_, "text", "content")
        metadata = dict_.pop("metadata", {})

        for field in llama_meta_fields:
            metadata[field] = dict_.pop(field, None)

        change_dict_key(metadata, "class_name", "llama_index_class")
        change_dict_key(metadata, "id_", "llama_index_id")
        change_dict_key(metadata, "relationships", "llama_index_relationships")

        dict_["metadata"] = metadata
        return cls.from_obj(dict_)
