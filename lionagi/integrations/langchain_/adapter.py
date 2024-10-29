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
        lion_fields = {
            k: v for k, v in dict_.items() if k in subj_cls.model_fields
        }
        lion_fields["langchain_metadata"] = dict_.pop("metadata", LN_UNDEFINED)
        if (
            isinstance(lion_fields["langchain_metadata"], dict)
            and "lion_metadata" in lion_fields["langchain_metadata"]
        ):
            lion_fields["metadata"] = lion_fields["langchain_metadata"].pop(
                "lion_metadata"
            )
        return lion_fields

    @classmethod
    def to_obj(cls, subj: Component, /):

        dict_ = to_dict(subj)

        lion_fields = {
            k: v for k, v in dict_.items() if k in subj.model_fields
        }
        extra_fields = {
            k: v for k, v in dict_.items() if k not in subj.model_fields
        }

        extra_fields["embedding"] = lion_fields.pop("embedding", [])
        extra_fields["metadata"] = extra_fields.pop("langchain_metadata", {})
        extra_fields["metadata"]["lion_metadata"] = lion_fields
        extra_fields["page_content"] = dict_.pop("page_content", "")
        return cls.LangchainDocument(**extra_fields)
