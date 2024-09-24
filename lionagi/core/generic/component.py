from typing import Any, TypeVar, ClassVar

from lion_core import LN_UNDEFINED
from pandas import Series

from lion_core.generic.component import Component as CoreComponent

from lionagi.libs.lionfuncs import to_dict, to_str

from lion_core.exceptions import LionValueError
from .utils.component_converter_registry import ComponentConverterRegistry

T = TypeVar("T")


class Component(CoreComponent):

    _converter_registry: ClassVar = ComponentConverterRegistry

    @classmethod
    def from_obj(cls, obj: Any, /, validation_kwargs={}, **kwargs) -> T:
        try:
            dict_ = to_dict(obj, **kwargs)
            type_ = to_str(type_, strip_lower=True)

            for field in ["page_content", "text", "chunk_content", "data"]:
                if field in dict_:
                    dict_["content"] = dict_.pop(field)
                    break
            if "llama_index" in type_:
                dict_["llama_index_class"] = dict_.pop("class_name", LN_UNDEFINED)
                dict_["llama_index_id"] = dict_.pop("id_", LN_UNDEFINED)
                dict_["llama_index_relationships"] = dict_.pop(
                    "relationships", LN_UNDEFINED
                )
            if "langchain" in type_:
                dict_["langchain"] = dict_.pop("lc", None)
                dict_["lc_type"] = dict_.pop("type", None)
                dict_["lc_id"] = dict_.pop("id", None)

            return cls.from_dict(dict_, **validation_kwargs)
        except Exception as e:
            raise LionValueError("Invalid object for deserialization.") from e

    def to_json_str(self, **kwargs) -> str:
        """Convert the component to a JSON string."""
        return self.convert_to("json", **kwargs)

    def to_xml(self, **kwargs) -> str:
        """Convert the component to an XML string."""
        return self.convert_to("xml", **kwargs)

    def to_pd_series(self, **kwargs) -> Series:
        """Convert the node to a Pandas Series."""
        return self.convert_to("pd_series", **kwargs)

    def to_llama_index_node(self, **kwargs) -> Any:
        """Serializes this node for LlamaIndex."""
        return self.convert_to("llama_index", **kwargs)

    def to_langchain_doc(self, **kwargs) -> Any:
        """Serializes this node for Langchain."""
        return self.convert_to("langchain", **kwargs)

    def __str__(self):
        dict_ = self.to_dict()
        return Series(dict_).__str__()

    def __repr__(self):
        dict_ = self.to_dict()
        return Series(dict_).__repr__()
