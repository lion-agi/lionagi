from typing import Any, Literal

from lionabc import Relational, Structure
from lionabc.exceptions import ItemExistsError, LionRelationError
from pydantic import Field, field_serializer

from lion_core.generic.component import Component
from lion_core.generic.note import Note
from lion_core.generic.pile import Pile, pile
from lion_core.graph.edge import Edge
from lion_core.sys_utils import SysUtil


class Graph(Component, Relational, Structure):
    """
    Represents a graph structure containing nodes and edges.

    This class models a graph with internal nodes and edges, providing
    methods for graph manipulation and analysis.

    Attributes:
        internal_nodes (Pile): The internal nodes of the graph.
        internal_edges (Pile): The internal edges of the graph.
        node_edge_mapping (Note): The mapping of nodes to edges for
                search purposes.
    """

    internal_nodes: Pile = Field(
        default_factory=lambda: pile({}, {Relational}),
        description="The internal nodes of the graph.",
    )
    internal_edges: Pile = Field(
        default_factory=lambda: pile({}, {Edge}),
        description="The internal edges of the graph.",
    )
    node_edge_mapping: Note = Field(
        default_factory=Note,
        description="The mapping for node and edges for search",
        exclude=True,
    )

    @field_serializer("internal_nodes", "internal_edges")
    def _serialize_internal_piles(self, value) -> Any:
        """
        Serialize the internal nodes and edges.

        Args:
            value: The Pile of internal nodes or edges to serialize.

        Returns:
            Serialized representation of the Pile.
        """
        value = value.to_dict()
        value = value["pile_"]
        return value

    def add_node(self, node: Relational) -> None:
        """
        Add a node to the graph.

        Args:
            node (Node): The node to add.

        Raises:
            LionRelationError: If the node already exists in the graph or
                if the node type is invalid.
        """
        try:
            if not isinstance(node, Relational):
                raise LionRelationError(
                    "Failed to add node: Invalid node type: "
                    "not a <Relational> entity."
                )
            _id = SysUtil.get_id(node)
            self.internal_nodes.insert(len(self.internal_nodes), node)
            self.node_edge_mapping.insert(_id, {"in": {}, "out": {}})
        except ItemExistsError as e:
            raise LionRelationError(f"Error adding node: {e}")

    def add_edge(self, edge: Edge, /) -> None:
        """
        Add an edge to the graph.

        Args:
            edge (Edge): The edge to add.

        Raises:
            LionRelationError: If the edge already exists in the graph or
                if either the head or tail node does not exist in the graph.
        """
        try:
            if not isinstance(edge, Edge):
                raise LionRelationError(
                    "Failed to add edge: Invalid edge type."
                )
            if (
                edge.head not in self.internal_nodes
                or edge.tail not in self.internal_nodes
            ):
                raise LionRelationError(
                    "Failed to add edge: Either edge head or tail node does"
                    " not exist in the graph."
                )
            self.internal_edges.insert(len(self.internal_edges), edge)
            self.node_edge_mapping[edge.head, "out", edge.ln_id] = edge.tail
            self.node_edge_mapping[edge.tail, "in", edge.ln_id] = edge.head
        except ItemExistsError as e:
            raise LionRelationError(f"Error adding node: {e}")

    def remove_node(self, node: Relational | str, /) -> None:
        """
        Remove a node from the graph.

        This method removes a node and all connected edges from the graph.

        Args:
            node (Node | str): The node or node ID to remove.

        Raises:
            LionRelationError: If the node does not exist in the graph.
        """
        _id = SysUtil.get_id(node)
        if _id not in self.internal_nodes:
            raise LionRelationError(
                f"Node {node} not found in the graph nodes."
            )

        in_edges: dict = self.node_edge_mapping[_id, "in"]
        for edge_id, node_id in in_edges.items():
            self.node_edge_mapping[node_id, "out"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        out_edges = self.node_edge_mapping[_id, "out"]
        for edge_id, node_id in out_edges.items():
            self.node_edge_mapping[node_id, "in"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        self.node_edge_mapping.pop(_id)
        return self.internal_nodes.pop(_id)

    def remove_edge(self, edge: Edge | str, /) -> None:
        """
        Remove an edge from the graph.

        Args:
            edge (Edge | str): The edge or edge ID to remove.

        Raises:
            LionRelationError: If the edge does not exist in the graph.
        """
        _id = SysUtil.get_id(edge)
        if _id not in self.internal_edges:
            raise LionRelationError(
                f"Edge {edge} not found in the graph edges."
            )

        edge = self.internal_edges[_id]
        self.node_edge_mapping[edge.head, "out"].pop(_id)
        self.node_edge_mapping[edge.tail, "in"].pop(_id)
        return self.internal_edges.pop(_id)

    def find_node_edge(
        self,
        node: Any,
        /,
        direction: Literal["both", "in", "out"] = "both",
    ) -> Pile[Edge]:
        """
        Find edges connected to a node in a specific direction.

        Args:
            node (Any): The node to find edges for.
            direction (Literal["both", "in", "out"], optional):
                The direction to search ("in", "out", or "both").
                Defaults to "both".

        Returns:
            Pile[Edge]: A Pile of edges connected to the node in the
                specified direction.

        Raises:
            LionRelationError: If the node is not found in the graph.
            ValueError: If the direction is not one of "both", "in", or "out".
        """
        if direction not in {"both", "in", "out"}:
            raise ValueError("The direction should be 'both', 'in', or 'out'.")

        _id = SysUtil.get_id(node)
        if _id not in self.internal_nodes:
            raise LionRelationError(
                f"Node {node} not found in the graph nodes."
            )

        result = []

        if direction in {"in", "both"}:
            for edge_id in self.node_edge_mapping[_id, "in"].keys():
                result.append(self.internal_edges[edge_id])

        if direction in {"out", "both"}:
            for edge_id in self.node_edge_mapping[_id, "out"].keys():
                result.append(self.internal_edges[edge_id])

        return self.internal_nodes.__class__(items=result, item_type={Edge})

    def get_heads(self) -> Pile:
        """
        Get all head nodes in the graph.

        Head nodes are nodes with no incoming edges.

        Returns:
            Pile: A Pile containing all head nodes.
        """

        result = []
        for node_id in self.node_edge_mapping.keys():
            if self.node_edge_mapping[node_id, "in"] == {}:
                result.append(self.internal_nodes[node_id])

        return self.internal_nodes.__class__(
            items=result, item_type={Relational}
        )

    def get_predecessors(self, node: Relational, /) -> Pile:
        """
        Get all predecessor nodes of a given node.

        Predecessors are nodes that have outgoing edges to the given node.

        Args:
            node (Node): The node to find predecessors for.

        Returns:
            Pile: A Pile containing all predecessor nodes.
        """
        edges = self.find_node_edge(node, direction="in")
        result = []
        for edge in edges:
            node_id = edge.head
            result.append(self.internal_nodes[node_id])
        return self.internal_nodes.__class__(
            items=result, item_type={Relational}
        )

    def get_successors(self, node: Relational, /) -> Pile:
        """
        Get all successor nodes of a given node.

        Successors are nodes that have incoming edges from the given node.

        Args:
            node (Node): The node to find successors for.

        Returns:
            Pile: A Pile containing all successor nodes.
        """
        edges = self.find_node_edge(node, direction="out")
        result = []
        for edge in edges:
            node_id = edge.tail
            result.append(self.internal_nodes[node_id])
        return self.internal_nodes.__class__(
            items=result, item_type={Relational}
        )

    def __contains__(self, item: object) -> bool:
        return item in self.internal_nodes or item in self.internal_edges


__all__ = ["Graph"]

# File: lion_core/graph/graph.py
