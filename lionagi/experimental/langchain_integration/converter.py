from lion_core.converter import Converter

from lionagi import lionfuncs as ln
from .utils import LC_META_FIELDS


class LangChainConverter(Converter):

    _object = "langchain"

    @classmethod
    def convert_obj_to_sub_dict(cls, object_, **kwargs):

        ln_dict = {}
        data = ln.to_dict(object_, **kwargs)
        langchain_meta = {}
        for i in LC_META_FIELDS:
            if i in data:
                langchain_meta[i] = data.pop(i)
        if "lion_meta" in data:
            ln_dict.update(data.pop("lion_meta"))
        elif "metadata" in data and "lion_meta" in ln.to_dict(data["metadata"]):
            ln_dict.update(ln.to_dict(data["metadata"]).pop("lion_meta"))

        data["lc_meta"] = langchain_meta

        ln_dict["embedding"] = data.pop("embedding", None)
        ln_dict["content"] = data.pop("page_content", None)
        ln_dict["extra_fields"] = data

        return ln_dict

    @classmethod
    def convert_sub_to_obj_dict(cls, subject, **kwargs) -> dict:
        data = ln.to_dict(subject, **kwargs)
        data["page_content"] = data.pop("content", "")
        lion_meta = {}
        if "ln_id" in data:
            lion_meta["ln_id"] = data.pop("ln_id")
        if "timestamp" in data:
            lion_meta["timestamp"] = data.pop("timestamp")
        if "metadata" in data:
            lion_meta["metadata"] = ln.to_dict(data.pop("metadata"))
        if "lion_class" in data:
            lion_meta["lion_class"] = data.pop("lion_class")

        data["metadata"] = lion_meta
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def to_obj(cls, subject, convert_kwargs={}, **kwargs):
        from lionagi.libs.sys_util import SysUtil

        Document = SysUtil.check_import(
            package_name="langchain",
            module_name="schema",
            import_name="Document",
        )
        dict_ = cls.convert_sub_to_obj_dict(subject, **convert_kwargs)
        return Document(**dict_, **kwargs)
