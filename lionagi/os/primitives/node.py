from typing import Any, ClassVar
import os
import pandas as pd
from pathlib import Path

from lion_core.generic.node import Node as CoreNode
from lion_core.exceptions import LionValueError


from .node_converter import NodeConverterRegistry


class Node(CoreNode):

    _converter_registry: ClassVar = NodeConverterRegistry

    @property
    def registered_converters(self) -> list[str]:
        """List all registered converter names."""
        return list(self.get_converter_registry()._converters.keys())

    @classmethod
    def from_obj(cls, obj: Any, **kwargs: Any) -> "Node":
        try:
            kind_ = None
            if os.path.isfile(obj):
                kind_ = Path(obj).suffix.strip(".")
            elif isinstance(obj, str):
                obj: str = obj.strip()
                if obj.startswith("<"):
                    kind_ = "xml"
                elif obj.startswith("{"):
                    kind_ = "json"
            elif isinstance(obj, pd.Series):
                kind_ = "pd_series"
            else:
                type_ = str(type(obj))
                if "llama_index" in type_:
                    kind_ = "llamaindex"
                elif "lang_chain" in type_:
                    kind_ = "langchain"

            if kind_ is not None:
                return cls.convert_from(obj, kind_, **kwargs)
            obj = to_dict(obj, **kwargs)
            return cls.from_dict(obj)

        except Exception as e:
            raise ValueError(f"Failed to convert to Node. Error: {e}") from e

    def to_obj(self, kind_: str = None, **kwargs) -> Any:
        """Convert the component to a specified kind. default is dict."""
        if kind_ and kind_ not in self.registered_converters:
            raise LionValueError(
                f"Cannot convert to {kind_}. Because it is not registered."
            )
        if kind_ in self.registered_converters:
            return self.convert_to(kind_, **kwargs)
        return self.to_dict()

    def to_llamaindex(): ...

    def to_langchain(): ...

    def to_json(): ...

    def to_xml(): ...

    def to_xml_file(): ...

    def to_pd_series(): ...


__all__ = ["Node"]
