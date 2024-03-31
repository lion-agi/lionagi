"""
Module for base component model definition using Pydantic.
"""

from abc import ABC
from typing import Any, TypeVar

from pydantic import Field, AliasChoices
from lionagi.libs import SysUtil, convert

from functools import singledispatchmethod
from .base_mixin import BaseComponentMixin

T = TypeVar("T", bound="BaseComponent")


class BaseComponent(BaseComponentMixin, ABC):
    """
    A base component model that provides common attributes and utility methods for metadata management.
    It includes functionality to interact with metadata in various ways, such as retrieving, modifying,
    and validating metadata keys and values.

    Attributes:
        id_ (str): Unique identifier, defaulted using SysUtil.create_id.
        timestamp (str | None): Timestamp of creation or modification.
        metadata (dict[str, Any]): Metadata associated with the component.
    """

    id_: str = Field(default_factory=SysUtil.create_id, alias="node_id")
    timestamp: str | None = Field(default_factory=SysUtil.get_timestamp)
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")

    class Config:
        """Model configuration settings."""

        extra = "allow"
        arbitrary_types_allowed = True
        populate_by_name = True
        validate_assignment = True
        validate_return = True
        str_strip_whitespace = True

    @classmethod
    def class_name(cls) -> str:
        """
        Retrieves the name of the class.
        """
        return cls.__name__

    @property
    def property_schema(self):
        return self.model_json_schema()["properties"]

    @property
    def property_keys(self):
        return list(self.model_json_schema()["properties"].keys())

    def copy(self, *args, **kwargs) -> T:
        """
        Creates a deep copy of the instance, with an option to update specific fields.

        Args:
            *args: Variable length argument list for additional options.
            **kwargs: Arbitrary keyword arguments specifying updates to the instance.

        Returns:
            BaseComponent: A new instance of BaseComponent as a deep copy of the original, with updates applied.
        """
        return self.model_copy(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"


class BaseNode(BaseComponent):
    """
    A base class for nodes, representing a fundamental unit in a graph or tree structure,
    extending BaseComponent with content handling capabilities.

    Attributes:
        content: The content of the node, which can be a string, a dictionary with any structure,
        None, or any other type. It is flexible to accommodate various types of content.
        This attribute also supports aliasing through validation_alias for compatibility with
        different naming conventions like "text", "page_content", or "chunk_content".
    """

    content: str | dict[str, Any] | None | Any = Field(
        default=None,
        validation_alias=AliasChoices("text", "page_content", "chunk_content"),
    )

    label: str | None = None
    in_relations: dict[str, str | Any | None] = Field(default={})
    out_relations: dict[str, str | Any | None] = Field(default={})

    @property
    def related_nodes(self):
        return convert.to_list(
            list(self.in_relations.keys()) + list(self.out_relations.keys())
        )

    @property
    def has_relations(self) -> bool:
        return True if len(self.relations) > 0 else False

    def add_relation(
        self, node: BaseComponent, relationship=None, direction=None
    ) -> None:
        if isinstance(node, BaseComponent):
            if direction == "in":
                self.in_relations[node.id_] = relationship
            elif direction == "out":
                self.out_relations[node.id_] = relationship
            return True
        elif isinstance(node, str):
            if direction == "in":
                self.in_relations[node] = relationship
            elif direction == "out":
                self.out_relations[node] = relationship
            return True
        else:
            return False

    @singledispatchmethod
    def pop_relation(self, node: Any, default=None) -> None:
        raise NotImplementedError

    @pop_relation.register(BaseComponent)
    def _(self, node: BaseComponent, default=None) -> None:
        if node.id_ in self.in_relations:
            return self.in_relations.pop(node.id_, default)
        return self.out_relations.pop(node.id_, default)

    @pop_relation.register(str)
    def _(self, node: str, default=None) -> None:
        if node in self.in_relations:
            return self.in_relations.pop(node, default)
        return self.out_relations.pop(node, default)

    @pop_relation.register(list)
    def _(self, node: list[str | BaseComponent], default=None) -> None:
        outs = []
        for _node in convert.to_list(node):
            outs.append(self.pop_relation(_node))
        return outs if any(outs) else default

    @property
    def predecessors(self):
        return list(self.in_relations.keys())

    @property
    def successors(self):
        return list(self.out_relations.keys())

    @property
    def all_relationships(self):
        a = []
        try:
            for i in self.in_relations.values():
                a.append(i.id_)
        except:
            pass
        try:
            for i in self.out_relations.values():
                a.append(i.id_)
        except:
            pass
        return a

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
                f"{self.content[:50]}..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ""
        meta_preview = (
            f"{str(self.metadata)[:50]}..."
            if len(str(self.metadata)) > 50
            else str(self.metadata)
        )
        return (
            f"{self.class_name()}({self.id_}, {content_preview}, {meta_preview},"
            f"{timestamp})"
        )
