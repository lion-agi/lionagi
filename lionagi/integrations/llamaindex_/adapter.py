from lion_core.protocols.adapters import Adapter
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
        lion_fields = {
            k: v for k, v in dict_.items() if k in subj_cls.model_fields
        }
        lion_fields["llama_index_metadata"] = dict_.pop("metadata", {})
        if (
            isinstance(lion_fields["llama_index_metadata"], dict)
            and "lion_metadata" in lion_fields["llama_index_metadata"]
        ):
            lion_fields["metadata"] = lion_fields["llama_index_metadata"].pop(
                "lion_metadata"
            )
            if (a := lion_fields.pop("class_name", None)) is not None:
                lion_fields["llama_index_metadata"]["class_name"] = a
        return lion_fields

    @classmethod
    def to_obj(cls, subj: Component, /):

        dict_ = subj.to_dict()

        lion_fields = {
            k: v for k, v in dict_.items() if k in subj.model_fields
        }
        extra_fields = {
            k: v for k, v in dict_.items() if k not in subj.model_fields
        }

        extra_fields["embedding"] = lion_fields.pop("embedding", [])
        extra_fields["metadata"] = extra_fields.pop("llama_index_metadata", {})
        extra_fields["metadata"]["lion_metadata"] = lion_fields
        return cls.TextNode(**extra_fields)


class LlamaIndexStroageContextAdapter(Adapter): ...


__all__ = ["LlamaIndexNodeAdapter", "LlamaIndexStroageContextAdapter"]
