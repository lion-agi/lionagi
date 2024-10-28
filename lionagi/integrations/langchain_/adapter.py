from lion_core.protocols.adapters import Adapter
from lion_core.types import LN_UNDEFINED
from lionfuncs import check_import, to_dict

from lionagi.core.generic.component import Component


class LangChainDocumentAdapter(Adapter):

    obj_key = "langchain_doc"
    LangchainDocument = check_import(
        package_name="langchain",
        module_name="schema",
        import_name="Document",
        error_message=(
            "Failed to autoinstall langchain. Please try installing langchain "
            "manually to use this adapter."
        ),
    )

    @classmethod
    def from_obj(cls, subj_cls: type[Component], obj, /):
        dict_ = to_dict(obj)
        dict_["langchain_metadata"] = dict_.pop("metadata", LN_UNDEFINED)
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
        return cls.LangchainDocument(**dict_)
