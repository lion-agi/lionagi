"""
Module for base component model definition using Pydantic.
"""

from typing import Any, TypeVar

import lionagi.integrations.bridge.pydantic_.base_model as pyd
from lionagi.core.schema.base.base_component import BaseComponent

from lionagi.libs import ln_convert as convert

T = TypeVar("T", bound="BaseComponent")


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

    content: str | dict[str, Any] | None | Any = pyd.ln_Field(
        default=None,
        validation_alias=pyd.ln_AliasChoices("text", "page_content", "chunk_content"),
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

    related_nodes: list[str] = pyd.ln_Field(default_factory=list)
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


class Tool(BaseRelatableNode):
    """
    Represents a tool, extending BaseRelatableNode with specific functionalities and configurations.

    Attributes:
        func: The main function or capability of the tool.
        schema_: An optional schema defining the structure and constraints of data the tool works with.
        manual: Optional documentation or manual for using the tool.
        parser: An optional parser associated with the tool for data processing or interpretation.
    """

    func: Any
    schema_: dict | None = None
    manual: Any | None = None
    parser: Any | None = None

    @pyd.ln_field_serializer("func")
    def serialize_func(self, func):
        return func.__name__


TOOL_TYPE = bool | Tool | str | list[Tool | str | dict] | dict
