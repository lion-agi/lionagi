"""
Module for base component model definition using Pydantic.
"""

import json
from abc import ABC
from typing import Any, Dict, Type, TypeVar, Callable, List
from pydantic import BaseModel, Field, ValidationError, AliasChoices, field_serializer

import pandas as pd

from lionagi.util.sys_util import SysUtil

T = TypeVar("T", bound="BaseComponent")


class BaseComponent(BaseModel, ABC):
    """A base component model with common attributes and methods for inheritance.

    Attributes:
        id_ (str): Unique identifier, defaulted using SysUtil.create_id.
        timestamp (str | None): Timestamp of creation or modification.
        metadata (Dict[str, Any]): Metadata associated with the component.

    """
    id_: str = Field(default_factory=SysUtil.create_id, alias="node_id")
    timestamp: str | None = Field(default_factory=SysUtil.get_timestamp)
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="meta")

    class Config:
        """Model configuration settings."""
        extra = "allow"
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def class_name(cls) -> str:
        """
        Returns the class name of the model.
        """
        return cls.__name__

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], **kwargs) -> T:
        """
        Creates an instance from a dictionary.
        kwargs for pydantic model_validate method.
        """
        return cls.model_validate(data, **kwargs)

    @classmethod
    def from_json(cls: Type[T], json_str: str, **kwargs) -> T:
        """
        Creates an instance from a JSON string.
        kwargs for pydantic model_validate_json method.
        """
        try:
            return cls.model_validate_json(json_str, **kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}")

    @classmethod
    def from_pd_series(
        cls: Type[T], pd_series: pd.Series, pd_kwargs=None, **kwargs
    ) -> T:
        """
        Creates an instance from a pandas Series.
        pd_kwargs for pd_series.to_dict method.
        kwargs for pydantic model_validate method
        """
        pd_kwargs = pd_kwargs or {}
        dict_ = pd_series.to_dict(**pd_kwargs)
        return cls.from_dict(dict_, **kwargs)

    # @classmethod
    # def from_xml(cls: Type[T], xml_str: str, **kwargs) -> T:
    #     """
    #     Creates an instance from an XML string.
    #     kwargs for pydantic model_validate method.
    #     """
    #     import xml.etree.ElementTree as ET
    #
    #     root = ET.fromstring(xml_str)
    #     data = cls._xml_to_dict(root)
    #     return cls.from_dict(data, **kwargs)

    @staticmethod
    def _xml_to_dict(root) -> Dict[str, Any]:
        """Converts a flat XML structure to a dictionary."""
        return {child.tag: child.text for child in root}

    def to_json_string(self, *args, **kwargs) -> str:
        """
        Serializes the instance to a JSON string.
        kwargs for pydantic model_dump_json method.
        """
        return self.model_dump_json(*args, by_alias=True, **kwargs)

    def to_dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Serializes the instance to a dictionary.
        kwargs for pydantic model_dump method.
        """
        return self.model_dump(*args, by_alias=True, **kwargs)

    def to_xml(self) -> str:
        """Serializes the instance to an XML string."""
        import xml.etree.ElementTree as ET

        root = ET.Element(self.__class__.__name__)

        def convert(dict_obj, parent):
            for key, val in dict_obj.items():
                if isinstance(val, dict):
                    element = ET.SubElement(parent, key)
                    convert(val, element)
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(val)

        convert(self.to_dict(), root)
        return ET.tostring(root, encoding="unicode")

    def to_pd_series(self, *args, pd_kwargs=None, **kwargs) -> pd.Series:
        """
        Converts the instance to a pandas Series.
        kwargs for pydantic model_dump method
        pd_kwargs for pd.Series constructor
        """
        pd_kwargs = {} if pd_kwargs is None else pd_kwargs

        return pd.Series(self.to_dict(*args, **kwargs), **pd_kwargs)

    def copy(self, *args, **kwargs):
        """
        Clones the instance with optional attribute updates.
        kwargs for pydantic model_copy method.
        """
        return self.model_copy(*args, **kwargs)

    @property
    def meta_keys(self) -> List[str]:
        """Lists keys in metadata dictionary."""
        return list(self.metadata.keys())

    def has_meta_key(self, key: str) -> bool:
        """Checks if a key exists in metadata."""
        return key in self.metadata

    def meta_get(self, key: str, default: Any = None) -> Any:
        """Retrieves metadata value by key with default."""
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        """Renames a key in metadata if it exists."""
        if old_key in self.metadata:
            self.metadata[new_key] = self.metadata.pop(old_key)
            return True
        return False

    def meta_pop(self, key: str, default: Any = None) -> Any:
        """Pops a key from metadata, returning its value or default."""
        return self.metadata.pop(key, default)

    def meta_merge(
        self, additional_metadata: Dict[str, Any], overwrite: bool = False
    ) -> None:
        """Merges another dictionary into metadata with optional overwrite."""
        for key, value in additional_metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = value

    def meta_clear(self) -> None:
        """Clears metadata dictionary."""
        self.metadata.clear()

    def meta_filter(self, filter_func: Callable[[Any], bool]) -> Dict[str, Any]:
        """Filters metadata based on a predicate function."""
        return {k: v for k, v in self.metadata.items() if filter_func(v)}

    def meta_validate(self, schema: Dict[str, Type[Any]]) -> bool:
        """Validates metadata against a specified type schema."""
        return all(
            isinstance(value, schema.get(key, type(None)))
            for key, value in self.metadata.items()
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"


class BaseNode(BaseComponent):
    content: str | Dict[str, Any] | None | Any = Field(
        default=None,
        validation_alias=AliasChoices("text", "page_content", "chunk_content"),
    )

    @property
    def content_str(self):
        if isinstance(self.content, Dict):
            return json.dumps(self.content)
        elif isinstance(self.content, str):
            return self.content
        else:
            try:
                return str(self.content)
            except ValueError:
                print(f"Content is not serializable for Node: {self._id}")
                return "null"

    def __str__(self):
        timestamp = f" ({self.timestamp})" if self.timestamp else ""
        if self.content:
            content_preview = (
                self.content[:50] + "..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ''
        meta_preview = (
            str(self.metadata)[:50] + "..."
            if len(str(self.metadata)) > 50
            else str(self.metadata)
        )
        return (
            f"{self.class_name()}({self.id_}, {content_preview}, {meta_preview},"
            f"{timestamp})"
        )


class BaseRelatableNode(BaseNode):
    related_nodes: List[str] = Field(default_factory=list)
    label: str | None = None

    def add_related_node(self, node_id: str) -> bool:
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False


class Tool(BaseRelatableNode):
    func: Any
    schema_: Dict = None
    manual: Any | None = None
    parser: Any | None = None

    @field_serializer("func")
    def serialize_func(self, func):
        return func.__name__
