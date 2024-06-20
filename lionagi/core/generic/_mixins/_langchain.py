from typing import Any

from lionagi.os.lib.sys_util import change_dict_key
from lionagi.os._setting.meta_fields import lc_meta_fields, base_lion_fields


class LangChainComponentMixin:

    def to_langchain_doc(self, **kwargs) -> Any:
        """Serializes this node for Langchain."""
        from lionagi.app.LangChain.bridge import LangchainBridge

        return LangchainBridge.to_langchain_document(self, **kwargs)

    @classmethod
    def _from_langchain(cls, obj: Any):
        """Create a Component instance from a Langchain object."""
        dict_ = obj.to_json()
        return cls.from_obj(dict_)

    @classmethod
    def _process_langchain_dict(cls, dict_: dict) -> dict:
        """Process a dictionary containing Langchain-specific data."""
        change_dict_key(dict_, "page_content", "content")

        metadata = dict_.pop("metadata", {})
        metadata.update(dict_.pop("kwargs", {}))

        if not isinstance(metadata, dict):
            metadata = {"extra_meta": metadata}

        for field in base_lion_fields:
            if field in metadata:
                dict_[field] = metadata.pop(field)

        for key in list(metadata.keys()):
            if key not in lc_meta_fields:
                dict_[key] = metadata.pop(key)

        for field in lc_meta_fields:
            if field in dict_:
                metadata[field] = dict_.pop(field)

        change_dict_key(metadata, "lc", "langchain")
        change_dict_key(metadata, "type", "lc_type")
        change_dict_key(metadata, "id", "lc_id")

        extra_fields = {k: v for k, v in metadata.items() if k not in lc_meta_fields}
        metadata = {k: v for k, v in metadata.items() if k in lc_meta_fields}
        dict_["metadata"] = metadata
        dict_.update(extra_fields)

        return dict_
