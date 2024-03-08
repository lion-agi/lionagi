"""
Module for base component model definition using Pydantic.
"""

from abc import ABC
from functools import singledispatchmethod

from typing import Any, Type, TypeVar, Callable

import lionagi.integrations.bridge.pydantic_.base_model as pyd

from lionagi.libs.sys_util import SysUtil
from lionagi.libs import ln_dataframe as dataframe
from lionagi.libs import ln_convert as convert
from lionagi.libs import ln_nested as nested


T = TypeVar("T", bound="BaseComponent")


class BaseComponent(pyd.BaseModel, ABC):
    """
    A base component model that provides common attributes and utility methods for metadata management.
    It includes functionality to interact with metadata in various ways, such as retrieving, modifying,
    and validating metadata keys and values.

    Attributes:
        id_ (str): Unique identifier, defaulted using SysUtil.create_id.
        timestamp (str | None): Timestamp of creation or modification.
        metadata (dict[str, Any]): Metadata associated with the component.
    """

    id_: str = pyd.Field(default_factory=SysUtil.create_id, alias="node_id")
    timestamp: str | None = pyd.Field(default_factory=SysUtil.get_timestamp)
    metadata: dict[str, Any] = pyd.Field(default_factory=dict, alias="meta")

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

    # from_obj method, overloaded
    # implemented for dict, str, pd.Series, pd.DataFrame, list, pydantic.BaseModel

    @singledispatchmethod
    @classmethod
    def from_obj(cls: Type[T], obj: Any, *args, **kwargs) -> T:
        raise NotImplementedError(f"Unsupported type: {type(obj)}")

    @from_obj.register
    @classmethod
    def _(cls, dict_data: dict, *args, **kwargs) -> T:
        return cls.model_validate(dict_data, *args, **kwargs)

    @from_obj.register(str)
    @classmethod
    def _(cls, json_data: str, *args, **kwargs) -> T:
        try:
            return cls.from_obj(convert.to_dict(json_data), *args, **kwargs)
        except pyd.ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}")

    @from_obj.register(dataframe.ln_Series)
    @classmethod
    def _(cls, pd_series, *args, pd_kwargs: dict | None = None, **kwargs) -> T:
        pd_kwargs = pd_kwargs or {}
        pd_dict = convert.to_dict(pd_series, **pd_kwargs)
        return cls.from_obj(pd_dict, *args, **kwargs)

    @from_obj.register(dataframe.ln_DataFrame)
    @classmethod
    def _(cls, pd_df, *args, pd_kwargs: dict | None = None, **kwargs) -> list[T]:
        pd_kwargs = pd_kwargs or {}
        pd_dict = convert.to_dict(pd_df, as_list=True, **pd_kwargs)
        return cls.from_obj(pd_dict, *args, **kwargs)

    @from_obj.register(list)
    @classmethod
    def _(cls, list_data: list[Any], *args, **kwargs) -> list[T]:
        return [cls.from_obj(item, *args, **kwargs) for item in list_data]

    @from_obj.register(pyd.BaseModel)
    @classmethod
    def _(cls, model, *args, model_kwargs=None, **kwargs) -> T:
        model_kwargs = model_kwargs or {}
        model_dict = {}
        try:
            model_dict = model.model_dump(by_alias=True, **model_kwargs)
        except:
            model_dict = model.to_dict(**model_kwargs)
        return cls.model_validate(model_dict, *args, **kwargs)

    # to obj methods, not overloaded

    def to_json_data(self, *args, **kwargs) -> str:
        return self.model_dump_json(*args, by_alias=True, **kwargs)

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        return self.model_dump(*args, by_alias=True, **kwargs)

    def to_xml(self) -> str:
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

    def to_pd_series(
        self, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> dataframe.ln_Series:
        pd_kwargs = {} if pd_kwargs is None else pd_kwargs
        dict_ = self.to_dict(*args, **kwargs)
        return dataframe.ln_Series(dict_, **pd_kwargs)

    def copy(self, *args, **kwargs) -> T:
        return self.model_copy(*args, **kwargs)

    def meta_keys(self, flattened: bool = False, **kwargs) -> list[str]:
        if flattened:
            return nested.get_flattened_keys(self.metadata, **kwargs)
        return list(self.metadata.keys())

    def meta_has_key(self, key: str, flattened: bool = False, **kwargs) -> bool:
        if flattened:
            return key in nested.get_flattened_keys(self.metadata, **kwargs)
        return key in self.metadata

    def meta_get(self, key: str, indices=None, default: Any = None) -> Any:
        if indices:
            return nested.nget(self.metadata, key, indices, default)
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key, new_key)
            return True
        return False

    def meta_insert(self, indices: str | list, value: Any, **kwargs) -> bool:
        return nested.ninsert(self.metadata, indices, value, **kwargs)

    # ToDo: do a nested pop
    def meta_pop(self, key: str, default: Any = None) -> Any:
        return self.metadata.pop(key, default)

    def meta_merge(
        self, additional_metadata: dict[str, Any], overwrite: bool = False, **kwargs
    ) -> None:
        nested.nmerge(
            [self.metadata, additional_metadata], overwrite=overwrite, **kwargs
        )

        for key, value in additional_metadata.items():
            if overwrite or key not in self.metadata:
                self.metadata[key] = value

    def meta_clear(self) -> None:

        self.metadata.clear()

    def meta_filter(self, condition: Callable[[Any, Any], bool]) -> dict[str, Any]:
        return nested.nfilter(self.metadata, condition)

    def meta_validate(self, schema: dict[str, Type | Callable]) -> bool:
        for key, validator in schema.items():
            value = self.metadata.get(key)
            if isinstance(validator, type):
                if not isinstance(value, validator):
                    return False
            elif callable(validator):
                if not validator(value):
                    return False
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

class BaseNode(BaseComponent):


    content: str | dict[str, Any] | None | Any = pyd.Field(
        default=None,
        validation_alias=pyd.AliasChoices("text", "page_content", "chunk_content"),
    )

    @property
    def content_str(self):
        """
        Attempts to serialize the node's content to a string.

        Returns:
            str: The serialized content string. If serialization fails, returns "null" and
                logs an error message indicating the content is not serializable.
        """
        try:
            return convert.to_str(self.content)
        except ValueError:
            print(
                f"Content is not serializable for Node: {self._id}, defaulting to 'null'"
            )
            return "null"

    def __str__(self):
        """
        Provides a string representation of the BaseNode instance, including a content preview,
        metadata preview, and optionally the timestamp if present.

        Returns:
            str: A string representation of the instance.
        """
        timestamp = f" ({self.timestamp})" if self.timestamp else ""
        if self.content:
            content_preview = (
                self.content[:50] + "..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ""
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
    """
    Extends BaseNode with functionality to manage relationships with other nodes.

    Attributes:
        related_nodes: A list of identifiers (str) for nodes that are related to this node.
        label: An optional label for the node, providing additional context or classification.
    """

    related_nodes: list[str] = pyd.Field(default_factory=list)
    label: str | None = None

    def add_related_node(self, node_id: str) -> bool:
        """
        Adds a node to the list of related nodes if it's not already present.

        Args:
            node_id: The identifier of the node to add.

        Returns:
            bool: True if the node was added, False if it was already in the list.
        """
        if node_id not in self.related_nodes:
            self.related_nodes.append(node_id)
            return True
        return False

    def remove_related_node(self, node_id: str) -> bool:
        """
        Removes a node from the list of related nodes if it's present.

        Args:
            node_id: The identifier of the node to remove.

        Returns:
            bool: True if the node was removed, False if it was not found in the list.
        """

        if node_id in self.related_nodes:
            self.related_nodes.remove(node_id)
            return True
        return False


TOOL_TYPE = bool | dict     # Tool | str | list[Tool | str | dict] |
