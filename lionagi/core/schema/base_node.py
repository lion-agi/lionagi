"""
Module for defining base component models using Pydantic, with a focus on
graph or tree structure components like nodes and relationships.
"""

from typing import Any, Dict, List, TypeVar
from pydantic import Field
from enum import Enum

from lionagi.libs import convert
from .base_component import BaseComponent
from .edge import Edge

T = TypeVar("T")


class EdgeDirection(str, Enum):
    """Defines possible directions for edges in a graph."""

    IN = "in"  # Incoming-edge direction
    OUT = "out"  # Outgoing-edge direction


class BaseNode(BaseComponent):
    """
    Represents a node within a graph or tree structure, extending a base component model.

    Attributes:
        content: Content stored within the node, which can be a string,
            a dictionary, None, or any other type, providing flexibility for different use cases.
        in_relations: A dictionary mapping other node IDs to incoming `Relationship` objects.
        out_relations: A dictionary mapping other node IDs to outgoing `Relationship` objects.

    The class provides properties and methods for accessing and modifying the node's relationships
    and its content in a flexible manner suitable for various graph-based applications.

    Note:
        Clarification:
        1. Node refers to this class, BaseNode.
        2. Relationship (alias edge) refers to the Relationship class object.
        3. relation is a {node_id: edge}
    """

    in_relations: Dict[str, Edge] = Field(
        default_factory=dict,
        description="Incoming relationships indexed by other node IDs.",
    )
    out_relations: Dict[str, Edge] = Field(
        default_factory=dict,
        description="Outgoing relationships indexed by other node IDs.",
    )

    @property
    def relations(self) -> Dict[str, Edge]:
        """
        Combines incoming and outgoing relationships into a single dictionary.
        """
        return {**self.in_relations, **self.out_relations}

    @property
    def in_edges(self) -> List[Edge]:
        """
        Lists all incoming relationships to the node.
        """
        return list(self.in_relations.values())

    @property
    def out_edges(self) -> List[Edge]:
        """
        Lists all outgoing relationships from the node.
        """
        return list(self.out_relations.values())

    @property
    def edges(self) -> List[Edge]:
        """
        Lists all relationships connected to the node, both incoming and outgoing.
        """
        return self.in_edges + self.out_edges

    @property
    def predecessors(self) -> List[str]:
        """
        Lists node IDs for all nodes that have an outgoing relationship to this node.
        """
        return list(self.in_relations.keys())

    @property
    def successors(self) -> List[str]:
        """
        Lists node IDs for all nodes that this node has an outgoing relationship to.
        """
        return list(self.out_relations.keys())

    @property
    def related_nodes(self) -> List[str]:
        """
        Lists all node IDs related to this node,
        both predecessors and successors.
        """
        return self.predecessors + self.successors

    @property
    def is_related(self) -> bool:
        """
        Checks if the node is connected to any other nodes through edges.
        """
        return bool(self.edges)

    def has_edge(self, edge: Edge | str) -> bool:
        """
        Checks if a specific edge is connected to the node.

        Args:
            edge: The edge or edge ID to check.

        Returns:
            True if the edge exists, False otherwise.
        """
        k = edge.id_ if isinstance(edge, Edge) else edge
        return k in [e.id_ for e in self.edges]

    def get_edge(self, related_node: BaseComponent | str) -> Edge | None:
        """
        Retrieves the edge ID for a specific related node.

        Args:
            related_node: The related node or its ID.

        Returns:
            The edge ID if found, None otherwise.
        """
        k = (
            related_node.id_
            if isinstance(related_node, BaseComponent)
            else related_node
        )
        return self.relations.get(k, None)

    def is_predecessor_of(self, node: BaseComponent | str) -> bool:
        """
        Determines if this node is a predecessor of another node.

        Args:
            node: The node or its ID to check against.

        Returns:
            True if this node is a predecessor, False otherwise.
        """
        k = node.id_ if isinstance(node, BaseComponent) else node
        return k in self.successors

    def is_successor_of(self, node: BaseComponent | str) -> bool:
        """
        Determines if this node is a successor of another node.

        Args:
            node: The node or its ID to check against.

        Returns:
            True if this node is a successor, False otherwise.
        """
        k = node.id_ if isinstance(node, BaseComponent) else node
        return k in self.predecessors

    def is_related_with(self, node: BaseComponent | str) -> bool:
        """
        Checks if this node is related to another node, either as a predecessor or successor.

        Args:
            node: The node or its ID to check against.

        Returns:
            True if related, False otherwise.
        """
        k = node.id_ if isinstance(node, BaseComponent) else node
        return k in self.related_nodes

    def add_edge(
        self,
        node: BaseComponent,
        edge: Edge | None | str = None,
        direction: EdgeDirection | None = EdgeDirection.OUT,
        label: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Adds an edge between this node and another node, creating a new `Relationship` if needed.

        Args:
            node: The node to connect with.
            relationship: An existing `Relationship` object, if any.
            direction: The direction of the relationship ('in' or 'out').
            label: A label for the relationship.
            **kwargs: Additional arguments for the `Relationship` constructor, if a new relationship is created.

        Returns:
            True if the edge was successfully added, False otherwise.
        """
        try:
            _edge = edge
            if not edge:
                if direction == EdgeDirection.OUT:
                    _edge = Edge(
                        source_node_id=self.id_,
                        target_node_id=node.id_,
                        label=label,
                        **kwargs,
                    )
                elif direction == EdgeDirection.IN:
                    _edge = Edge(
                        source_node_id=node.id_,
                        target_node_id=self.id_,
                        label=label,
                        **kwargs,
                    )

            if direction == EdgeDirection.OUT:
                self.out_relations[node.id_] = _edge
                node.in_relations[self.id_] = _edge

            elif direction == EdgeDirection.IN:
                self.in_relations[node.id_] = _edge
                node.out_relations[self.id_] = _edge

            return True
        except Exception:
            return False

    def pop_edge(self, node: BaseComponent, edge: Edge | str) -> Edge | None:
        """
        Removes a specific edge between this node and another node.

        Args:
            node: The other node involved in the edge.
            edge: The edge or its ID to remove.

        Returns:
            The removed edge-object, or None if not found.
        """
        k = edge.id_ if isinstance(edge, Edge) else edge
        for i in [
            self.in_relations,
            self.out_relations,
            node.in_relations,
            node.out_relations,
        ]:
            if k in i:
                i.pop(k)
        return edge

    @property
    def content_str(self):
        """
        Provides a string representation of the node's content.

        Returns:
            A string representation of the content, or "null" if conversion fails.
        """
        try:
            return convert.to_str(self.content)
        except ValueError:

            return "null"

    def __str__(self):
        """
        Generates a string representation of the BaseNode, showing key information.

        Returns:
            A formatted string representing the node, including content preview and metadata.
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
