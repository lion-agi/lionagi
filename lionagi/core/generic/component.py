"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""Component class, base building block in LionAGI."""


from collections.abc import Sequence
from functools import singledispatchmethod
from typing import Any, TypeVar, TypeAlias, Union

from pandas import DataFrame, Series
from pydantic import BaseModel, Field, ValidationError, AliasChoices


from lionagi.os.lib import (
    strip_lower,
    to_dict,
    to_str,
    fuzzy_parse_json,
)
from lionagi.os.lib.sys_util import get_timestamp, create_id
from lionagi.os._setting.meta_fields import base_lion_fields
from ..abc.element import Element
from .exceptions import LionTypeError, LionValueError
from ...lionagi.core.abc.mixins import ComponentMixin


T = TypeVar("T")

_init_class = {}


class Component(Element, ComponentMixin):
    """
    Represents a distinguishable, temporal entity in LionAGI.

    Encapsulates essential attributes and behaviors needed for individual
    components within the system's architecture. Each component is uniquely
    identifiable, with built-in version control and metadata handling.

    Attributes:
        ln_id (str): A unique identifier for the component.
        timestamp (str): The UTC timestamp when the component was created.
        metadata (dict): Additional metadata for the component.
        extra_fields (dict): Additional fields for the component.
        content (Any): Optional content of the component.
    """

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("meta", "info"),
        description="Additional metadata for the component.",
    )

    extra_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional fields for the component.",
        validation_alias=AliasChoices(
            "extra", "additional_fields", "schema_extra", "extra_schema"
        ),
    )

    content: Any = Field(
        default=None,
        description="The optional content of the node.",
        validation_alias=AliasChoices("text", "page_content", "chunk_content", "data"),
    )

    embedding: list[float] = Field(
        default=[],
        description="The optional embedding of the node.",
    )

    class Config:
        """Model configuration settings."""

        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        use_enum_values = True

    @singledispatchmethod
    @classmethod
    def from_obj(cls, obj: Any, /, **kwargs) -> T:
        """
        Create Component instance(s) from various input types.

        This method dynamically handles different types of input data,
        allowing the creation of Component instances from dictionaries,
        strings (JSON), lists, pandas Series, pandas DataFrames, and
        instances of other classes, including Pydantic models. Additionally,
        it includes support for custom types such as LlamaIndex and
        Langchain specific data.

        The type of the input data determines how it is processed:
        - `dict`: Treated as field-value pairs for the Component.
        - `str`: Expected to be JSON format; parsed into a dictionary first.
        - `list`: Each item is processed independently, and a list of
                  Components is returned.
        - `pandas.Series`: Converted to a dictionary; treated as field-value
                           pairs.
        - `pandas.DataFrame`: Each row is treated as a separate Component;
                              returns a list of Components.
        - `Pydantic BaseModel`: Extracts data directly from the Pydantic
                                model.
        - `LlamaIndex model`: Converts using LlamaIndex-specific logic to
                              extract data suitable for Component creation.
        - `Langchain model`: Processes Langchain-specific structures to
                             produce Component data.

        Args:
            obj: The input object to create Component instance(s) from.
            **kwargs: Additional keyword arguments to pass to the creation
                      method.

        Returns:
            T: The created Component instance(s).

        Raises:
            LionTypeError: If the input type is not supported.
        """
        if isinstance(obj, (dict, str, list, Series, DataFrame, BaseModel)):
            return cls._dispatch_from_obj(obj, **kwargs)

        type_ = str(type(obj))

        if "llama_index" in type_:
            return cls._from_llama_index(obj)
        elif "langchain" in type_:
            return cls._from_langchain(obj)

        raise LionTypeError(f"Unsupported type: {type(obj)}")

    @classmethod
    def _dispatch_from_obj(cls, obj: Any, **kwargs) -> T:
        """Dispatch the from_obj method based on the input type."""
        if isinstance(obj, dict):
            return cls._from_dict(obj, **kwargs)
        elif isinstance(obj, str):
            return cls._from_str(obj, **kwargs)
        elif isinstance(obj, list):
            return cls._from_list(obj, **kwargs)
        elif isinstance(obj, Series):
            return cls._from_pd_series(obj, **kwargs)
        elif isinstance(obj, DataFrame):
            return cls._from_pd_dataframe(obj, **kwargs)
        elif isinstance(obj, BaseModel):
            return cls._from_base_model(obj, **kwargs)

    @classmethod
    def _from_dict(cls, obj: dict, /, *args, **kwargs) -> T:
        """Create a Component instance from a dictionary."""
        try:
            dict_ = {**obj, **kwargs}
            if "embedding" in dict_:
                dict_["embedding"] = cls._validate_embedding(dict_["embedding"])

            if "lion_class" in dict_:
                cls = _init_class.get(dict_.pop("lion_class"), cls)

            if "lc" in dict_:
                dict_ = cls._process_langchain_dict(dict_)
            else:
                dict_ = cls._process_generic_dict(dict_)
        
            self = cls.model_validate(dict_, *args, **kwargs)
            if "extra_fields" in dict_:
                for field, value in dict_["extra_fields"].items():
                    setattr(self, field, value)
            return self

        except ValidationError as e:
            raise LionValueError("Invalid dictionary for deserialization.") from e

    @classmethod
    def _process_generic_dict(cls, dict_: dict) -> dict:
        """Process a generic dictionary."""
        meta_ = dict_.pop("metadata", None) or {}

        if not isinstance(meta_, dict):
            meta_ = {"extra_meta": meta_}

        for key in list(dict_.keys()):
            if key not in base_lion_fields:
                meta_[key] = dict_.pop(key)

        if not dict_.get("content", None):
            for field in ["page_content", "text", "chunk_content", "data"]:
                if field in meta_:
                    dict_["content"] = meta_.pop(field)
                    break

        dict_["metadata"] = meta_

        if "ln_id" not in dict_:
            dict_["ln_id"] = meta_.pop("ln_id", create_id())
        if "timestamp" not in dict_:
            dict_["timestamp"] = get_timestamp(sep=None)[:-6]
        if "metadata" not in dict_:
            dict_["metadata"] = {}
        if "extra_fields" not in dict_:
            dict_["extra_fields"] = {}
        return dict_

    @classmethod
    def _from_str(cls, obj: str, /, *args, fuzzy_parse: bool = False, **kwargs) -> T:
        """Create a Component instance from a JSON string."""
        obj = fuzzy_parse_json(obj) if fuzzy_parse else to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise LionValueError("Invalid JSON for deserialization: ") from e

    @classmethod
    def _from_list(cls, obj: list, /, *args, **kwargs) -> list[T]:
        """Create a list of node instances from a list of objects."""
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    def as_type(self, type_name: str, **kwargs) -> T:
        match strip_lower(type_name):
            case "json_str", "str":
                return self.to_json_str(**kwargs)
            case "json", "dict":
                return self.to_dict(**kwargs)
            case "xml", "xml_str":
                return self.to_xml(**kwargs)
            case "pd_series":
                return self.to_pd_series(**kwargs)
            case "llama_index", "llama":
                return self.to_llama_index_node(**kwargs)
            case "langchain", "lc":
                return self.to_langchain_doc(**kwargs)
            case "pydantic", "pydanticmodel", "basemodel":
                return BaseModel(**self.to_dict(**kwargs))
            case "list":
                return [self]
            case _:
                raise LionTypeError(f"Unsupported type: {type_name}")

    def to_json_str(self, *args, dropna=False, **kwargs) -> str:
        """Convert the component to a JSON string."""
        dict_ = self.to_dict(*args, dropna=dropna, **kwargs)
        return to_str(dict_)

    def to_dict(self, *args, dropna=False, **kwargs) -> dict[str, Any]:
        """Convert the component to a dictionary."""
        dict_ = self.model_dump(*args, by_alias=True, **kwargs)

        for field_name in list(self.extra_fields.keys()):
            if field_name not in dict_:
                dict_[field_name] = getattr(self, field_name, None)

        dict_.pop("extra_fields", None)
        dict_["lion_class"] = self.class_name
        if dropna:
            dict_ = {k: v for k, v in dict_.items() if v is not None}
        return dict_

    def to_xml(self, *args, dropna=False, **kwargs) -> str:
        """Convert the component to an XML string."""
        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj: dict, parent: ET.Element) -> None:
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(*args, dropna=dropna, **kwargs), root)
        return ET.tostring(root, encoding="unicode")

    def __setattr__(self, name, value):
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        super().__setattr__(name, value)
        self._add_last_update(name)

    def __str__(self):
        dict_ = self.to_dict()
        return Series(dict_).__str__()

    def __repr__(self):
        dict_ = self.to_dict()
        return Series(dict_).__repr__()

    def __len__(self):
        return 1


LionIDable: TypeAlias = Union[str, Element]


def get_lion_id(item: LionIDable) -> str:
    """Get the Lion ID of an item."""
    if isinstance(item, Sequence) and len(item) == 1:
        item = item[0]
    if isinstance(item, str) and len(item) == 32:
        return item
    if getattr(item, "ln_id", None) is not None:
        return item.ln_id
    raise LionTypeError("Item must be a single LionIDable object.")
