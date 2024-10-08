from typing import Any, TypeVar

from lion_core.generic.base import RealElement
from lion_core.protocols.data_adapter import DataAdapter
from lionfuncs import check_import, to_dict, to_str

T = TypeVar("T", bound=RealElement)


lc_meta_fields = ["id", "metadata", "page_content", "type"]

lion_meta_fields = [
    "ln_id",
    "timestamp",
    "metadata",
    "extra_fields",
]


def _from_original_langchain_doc(dict_: dict) -> dict:

    langchain_meta = {}
    for i in lc_meta_fields:
        if i in dict_:
            langchain_meta[f"lc_{i}"] = dict_.pop(i)

    if "page_content" in dict_:
        dict_["content"] = dict_.pop("page_content")

    dict_["lc_meta"] = langchain_meta
    return dict_


def _from_lion_converted_langchain_doc(dict_: dict) -> dict:

    lion_fields = {}
    if "lion_meta" in dict_:
        lion_fields = dict_.pop("lion_meta")

    for k in list(lion_fields.keys()):
        if f"lion_{k}" in lion_fields:
            lion_fields[k] = lion_fields.pop(f"lion_{k}")

    dict_ = _from_original_langchain_doc(dict_)
    dict_.update(lion_fields)
    return dict_


def _original_lion_to_langchain_doc(dict_: dict) -> dict:
    lion_meta = {}

    for i in lion_meta_fields:
        if i in dict_:
            lion_meta[f"lion_{i}"] = dict_.pop(i)

    text_ = dict_.pop("content", "")
    if not isinstance(text_, str):
        try:
            text_ = to_str(text_)
        except Exception as e:
            raise ValueError(
                f"Failed to convert content to string. Error: {e}"
            )

    dict_["page_content"] = text_
    dict_["lion_meta"] = lion_meta
    return dict_


def _previously_converted_lion_to_langchain_doc(dict_: dict) -> dict:
    dict_ = _from_original_langchain_doc(dict_)

    lc_fields = {}
    if "lc_meta" in dict_:
        lc_fields = dict_.pop("lc_meta")

    for k in list(lc_fields.keys()):
        if f"lc_{k}" in lc_fields:
            dict_[k] = lc_fields.pop(f"lc_{k}")

    return dict_


class LangChainDocumentAdapter(DataAdapter):

    obj_key = "langchain_doc"
    verbose = False
    config = None
    LangchainDocument = check_import(
        "langchain", module_name="schema", import_name="Document"
    )

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:

        dict_ = obj.model_dump()
        if "lion_meta" in dict_:
            return _from_lion_converted_langchain_doc(dict_)
        return _from_original_langchain_doc(dict_)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        dict_ = subj.to_dict()
        if "lion_meta" in dict_:
            return cls.LangchainDocument(
                **_previously_converted_lion_to_langchain_doc(dict_)
            )
        return cls.LangchainDocument(**_original_lion_to_langchain_doc(dict_))
