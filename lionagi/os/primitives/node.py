from __future__ import annotations
import contextlib
from typing import Any, ClassVar
import os
import pandas as pd
from pathlib import Path
from pydantic import field_validator

from lion_core.generic.node import Node as CoreNode
from lion_core.exceptions import LionValueError

from typing_extensions import deprecated


from .node_converter import NodeConverterRegistry


class Node(CoreNode):

    _converter_registry: ClassVar = NodeConverterRegistry

    @property
    def registered_converters(self) -> list[str]:
        """List all registered converter names."""
        return list(self.get_converter_registry()._converters.keys())

    @field_validator("embedding")
    def _validate_embedding(cls, value: Any) -> list:
        if not value:
            return []
        if isinstance(value, str):
            if len(value) < 10:
                return []

            string_elements = value.strip("[]").split(",")
            # Convert each string element to a float
            with contextlib.suppress(ValueError):
                return [float(element) for element in string_elements]
        raise ValueError("Invalid embedding format.")

    @deprecated('use `self.convert_to("json")` instead.')
    def to_json(self, **kwargs) -> str:
        return self.convert_to("json", **kwargs)

    @deprecated('use `self.convert_to("json_file")` instead.')
    def to_json_file(self, **kwargs) -> None:
        self.convert_to("json_file", **kwargs)

    @deprecated('use `self.convert_to("xml")` instead.')
    def to_xml(self, **kwargs) -> str:
        return self.convert_to("xml", **kwargs)

    @deprecated('use `self.convert_to("xml_file")` instead.')
    def to_xml_file(self, filepath: str | Path, **kwargs) -> None:
        self.convert_to("xml_file", filepath=filepath, **kwargs)

    @deprecated('use `self.convert_to("llama_index_node")` instead.')
    def to_llama_index_node(self, **kwargs) -> Any:
        return self.convert_to("llama_index_node", **kwargs)

    @deprecated('use `self.convert_to("langchain_doc")` instead.')
    def to_langchain_doc(self, **kwargs) -> Any:
        return self.convert_to("langchain_doc", **kwargs)

    @deprecated('use `self.convert_to("pd_series")` instead.')
    def to_pandas_series(self, **kwargs) -> pd.Series:
        return self.convert_to("pd_series", **kwargs)

    @classmethod
    def from_obj(cls, object_, **kwargs):
        kind_ = _dispatch_from_obj(object_)
        try:
            return cls.convert_from(object_, object_key=kind_, **kwargs)
        except Exception as e:
            raise ValueError(f"Failed to convert to Node. Error: {e}") from e

    def to_obj(self, object_key: str, /, **kwargs):
        if object_key not in self.registered_converters:
            raise LionValueError(
                f"Cannot convert to <{object_key}>. Because it is not registered."
            )
        return self.convert_to(object_key, **kwargs)


def _dispatch_from_obj(object_: Any) -> Node:
    kind_ = None
    if os.path.isfile(object_):
        kind_ = Path(object_).suffix.strip(".") + "_file"

    elif isinstance(object_, str):
        object_: str = object_.strip()
        if object_.startswith("<"):
            kind_ = "xml"
        elif object_.startswith("{"):
            kind_ = "json"

    elif isinstance(object_, pd.Series):
        kind_ = "pd_series"

    else:
        type_ = str(type(object_))
        if "llama_index" in type_:
            kind_ = "llama_index_node"
        elif "lang_chain" in type_:
            kind_ = "langchain_doc"

    return kind_


__all__ = [Node]
