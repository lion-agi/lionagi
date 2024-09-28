from typing import Any, TypeVar

from lion_core.converter import Converter
from lion_core.generic.base import RealElement
from lionfuncs import check_import, to_dict

T = TypeVar("T", bound=RealElement)


class LangChainConverter(Converter):

    obj_key = "langchain"
    LangchainDocument = check_import(
        "langchain", module_name="schema", import_name="Document"
    )

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict[str, Any]:
        dict_ = to_dict(obj, **kwargs)
        l_ = ["id_", "metadata", "type"]
        for i in l_:
            if i in dict_:
                dict_[f"lc_{i}"] = dict_.pop(i)
        dict_["content"] = dict_.pop("page_content", "")
        if "lion_metadata" in dict_:
            dict_["metadata"] = dict_.pop("lion_metadata")

        elif "lion_metadata" in dict_["lc_metadata"]:
            if not isinstance(dict_["lc_metadata"], dict):
                try:
                    dict_["lc_metadata"] = to_dict(dict_["lc_metadata"])
                    dict_["metadata"] = dict_["lc_metadata"].pop("lion_metadata", {})
                except Exception:
                    pass

        return dict_

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        dict_ = subj.to_dict(**kwargs)
        dict_["lion_metadata"] = dict_.pop("metadata", {})
        dict_["page_content"] = dict_.pop("content", "")

        for i in ["id_", "metadata", "type"]:
            if f"lc_{i}" in dict_:
                dict_[i] = dict_.pop(f"lc_{i}")

        return cls.LangchainDocument(**dict_)
