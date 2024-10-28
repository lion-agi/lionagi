from lion_core.protocols.adapters import Adapter
from lion_core.types import LN_UNDEFINED
from lionfuncs import check_import, to_dict

from lionagi.core.generic.component import Component


class LlamaIndexNodeAdapter(Adapter):

    obj_key = "llama_index_node"
    TextNode = check_import(
        package_name="llama_index",
        module_name="core.schema",
        import_name="TextNode",
        pip_name="llama-index",
        error_message=(
            "Failed to autoinstall llama-index. Please try installing llama-index "
            "manually to use this adapter."
        ),
    )

    @classmethod
    def from_obj(cls, subj_cls: type[Component], obj, /):
        dict_ = to_dict(obj)
        dict_["llama_index_metadata"] = dict_.pop("metadata", LN_UNDEFINED)
        dict_["metadata"] = dict_.pop("lion_metadata", LN_UNDEFINED)
        dict_["lion_class"] = dict_.pop("lion_class", LN_UNDEFINED)
        return {k: v for k, v in dict_.items() if v is not LN_UNDEFINED}

    @classmethod
    def to_obj(cls, subj: Component, /):

        dict_ = subj.to_dict()
        lion_meta = dict_.pop("metadata", {})
        lion_meta["lion_class"] = dict_.pop("lion_class", LN_UNDEFINED)
        lion_meta = {
            k: v for k, v in lion_meta.items() if v is not LN_UNDEFINED
        }
        dict_["lion_metadata"] = lion_meta
        dict_ = {k: v for k, v in dict_.items() if v is not LN_UNDEFINED}
        return cls.TextNode(**dict_)


class LlamaIndexStroageContextAdapter(Adapter): ...


__all__ = ["LlamaIndexNodeAdapter", "LlamaIndexStroageContextAdapter"]
