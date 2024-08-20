from lion_core.converter import Converter

from lionagi.os.sys_config import BASE_LION_FIELDS
from lionagi.os.libs import to_dict

from .utils import LC_META_FIELDS


class LangChainDocConverter(Converter):

    @staticmethod
    def from_obj(cls, obj, **kwargs) -> dict:
        dict_ = to_dict(obj, **kwargs)
        dict_["content"] = dict_.pop("page_content", None)

        metadata = dict_.pop("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {"extra_meta": metadata}
        metadata.update(dict_.pop("kwargs", {}))

        for field in BASE_LION_FIELDS:
            if field in metadata:
                dict_[field] = metadata.pop(field)

        for key in list(metadata.keys()):
            if key not in LC_META_FIELDS:
                dict_[key] = metadata.pop(key)

        for field in LC_META_FIELDS:
            if field in dict_:
                metadata[field] = dict_.pop(field)

        metadata["langchain"] = metadata.pop("lc", None)
        metadata["lc_type"] = metadata.pop("type", None)
        metadata["lc_id"] = metadata.pop("id", None)
        extra_fields = {k: v for k, v in metadata.items() if k not in LC_META_FIELDS}
        metadata = {k: v for k, v in metadata.items() if k in LC_META_FIELDS}
        dict_["metadata"] = metadata
        dict_.update(extra_fields)

        return dict_

    @staticmethod
    def to_obj(self, **kwargs):
        from .documents import to_langchain_document

        dict_ = to_dict(self, **kwargs)
        return to_langchain_document(**dict_)
