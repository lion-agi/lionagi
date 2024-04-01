"""
Module for base component model definition using Pydantic.
"""

from abc import ABC
from typing import Any, TypeVar

from pydantic import Field, AliasChoices
from lionagi.libs import SysUtil, convert

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
    A base class for nodes, representing a fundamental unit in a graph or tree structure.

    This class extends BaseComponent with content handling capabilities.

    Attributes:
        content (str | dict[str, Any] | None | Any): The content of the node, which can be a string,
            a dictionary with any structure, None, or any other type. It is flexible to accommodate
            various types of content. This attribute also supports aliasing through validation_alias
            for compatibility with different naming conventions like "text", "page_content", or
            "chunk_content".
        label (str | None): The label of the node.
        in_relations (dict[str, str | Any | None]): The incoming relations of the node.
        out_relations (dict[str, str | Any | None]): The outgoing relations of the node.
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
        """
        Get the related nodes of the node.

        Returns:
            list: A list of the ids of the related nodes.
        """
        return convert.to_list(
            list(self.in_relations.keys()) + list(self.out_relations.keys())
        )

    @property
    def has_relations(self) -> bool:
        """
        Check if the node has any relations.

        Returns:
            bool: True if the node has relations, False otherwise.
        """
        return True if len(self.relations) > 0 else False

    def get_relation(self, node: BaseComponent) -> str | None:
        """
        Get the relation with a specific node.

        Args:
            node (BaseComponent | str): The node or node id to get the relation with.

        Returns:
            str | None: The relation with the node, or None if no relation exists.
        """
        if isinstance(node, BaseComponent):
            if node.id_ in self.in_relations:
                return self.in_relations[node.id_]
            elif node.id_ in self.out_relations:
                return self.out_relations[node.id_]
        elif isinstance(node, str):
            if node in self.in_relations:
                return self.in_relations[node]
            elif node in self.out_relations:
                return self.out_relations[node]
        else:
            return None

    def add_relation(
        self,
        node: BaseComponent | str,
        relationship: Any = None,
        direction: str | None = None,
    ) -> bool:
        """
        Add a relation to the node.

        Args:
            node (BaseComponent | str): The node or node id to add the relation with.
            relationship (Any): The relationship to add.
            direction (str | None): The direction of the relation, either "in" or "out".

        Returns:
            bool: True if the relation was added successfully, False otherwise.
        """
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

    def pop_relation(self, relationship: Any, node: BaseComponent | str) -> Any:
        """
        Remove a relation from the node.

        Args:
            relationship (Any): The relationship to remove.
            node (BaseComponent | str): The node or node id to remove the relation with.

        Returns:
            Any: The removed relationship.
        """
        k = (
            relationship.id_
            if isinstance(relationship, BaseComponent)
            else relationship
        )

        if k in self.in_relations:
            self.in_relations.pop(k)
        if k in self.out_relations:
            self.out_relations.pop(k)

        if k in node.in_relations:
            node.in_relations.pop(k)
        if k in node.out_relations:
            node.out_relations.pop(k)

        return relationship

    @property
    def predecessors(self):
        """
        Get the predecessors of the node.

        Returns:
            list: A list of the ids of the predecessor nodes.
        """
        return list(self.in_relations.keys())

    @property
    def successors(self):
        """
        Get the successors of the node.

        Returns:
            list: A list of the ids of the successor nodes.
        """
        return list(self.out_relations.keys())

    @property
    def all_relationships(self):
        """
        Get all the relationships of the node.

        Returns:
            list: A list of all the relationship ids.
        """
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
        Get the content of the node as a string.

        Returns:
            str: The content of the node as a string, or "null" if the content is not serializable.
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
        Get a string representation of the node.

        Returns:
            str: A string representation of the node, including the id, content preview,
                metadata preview, and timestamp (if available).
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
