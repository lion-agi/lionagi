from typing import Any, TypeVar

from lion_core.generic.base import RealElement
from lion_core.protocols.data_adapter import DataAdapter
from lionfuncs import check_import, to_str

T = TypeVar("T", bound=RealElement)


llama_meta_fields = [
    "id_",
    "metadata",
    "excluded_embed_metadata_keys",
    "excluded_llm_metadata_keys",
    "relationships",
    "mimetype",
    "start_char_idx",
    "end_char_idx",
    "text_template",
    "metadata_template",
    "metadata_seperator",
    "class_name",
]

lion_meta_fields = [
    "ln_id",
    "timestamp",
    "metadata",
    "extra_fields",
]


def _from_original_llama_node(dict_: dict) -> dict:

    llama_meta = {}
    for i in llama_meta_fields:
        if i in dict_:
            llama_meta[f"llama_index_{i}"] = dict_.pop(i)

    if "text" in dict_:
        dict_["content"] = dict_.pop("text")

    dict_["llama_meta"] = llama_meta
    return dict_


def _from_lion_converted_llama_node(dict_: dict) -> dict:

    lion_fields = {}
    if "lion_meta" in dict_:
        lion_fields = dict_.pop("lion_meta")

    for k in list(lion_fields.keys()):
        if f"lion_{k}" in lion_fields:
            lion_fields[k] = lion_fields.pop(f"lion_{k}")

    dict_ = _from_original_llama_node(dict_)
    dict_.update(lion_fields)
    return dict_


def _original_lion_to_llama_node(dict_: dict) -> dict:
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

    dict_["text"] = text_
    dict_["lion_meta"] = lion_meta
    return dict_


def _previously_converted_lion_to_llama_node(dict_: dict) -> dict:

    dict_ = _original_lion_to_llama_node(dict_)

    llama_fields = {}
    if "llama_meta" in dict_:
        llama_fields = dict_.pop("llama_meta")

    for k in list(llama_fields.keys()):
        if f"llama_index_{k}" in llama_fields:
            dict_[k] = llama_fields.pop(f"llama_index_{k}")

    return dict_


class LlamaIndexNodeAdapter(DataAdapter):

    obj_key = "llamaindex_node"
    verbose = False
    config = None
    TextNode = check_import(
        package_name="llama_index",
        module_name="core.schema",
        import_name="TextNode",
    )

    @classmethod
    def from_obj(
        cls,
        subj_cls: type[RealElement],
        obj: Any,
        /,
        **kwargs: Any,
    ) -> dict[str, Any]:

        dict_ = obj.to_dict()
        if "lion_meta" in dict_:
            return _from_lion_converted_llama_node(dict_)
        return _from_original_llama_node(dict_)

    @classmethod
    def to_obj(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ) -> Any:
        dict_ = subj.to_dict()

        if "lion_meta" in subj.metadata:
            return cls.TextNode(
                **_previously_converted_lion_to_llama_node(dict_)
            )
        return cls.TextNode(**_original_lion_to_llama_node(dict_))
