# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections import deque
from typing import Any, Literal

from pydantic import Field, field_serializer

from lionagi._errors import ItemExistsError, RelationError

from ..generic._id import ID
from ..generic.pile import Pile
from .edge import Edge
from .node import Node

__all__ = ("Graph",)


class Graph(Node):
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

    internal_nodes: Pile[Node] = Field(
        default_factory=lambda: Pile(item_type=Node),
        description="The internal nodes of the graph.",
    )
    internal_edges: Pile[Edge] = Field(
        default_factory=lambda: Pile(item_type=Edge),
        description="The internal edges of the graph.",
    )
    node_edge_mapping: dict = Field(
        default_factory=dict,
        description="The mapping for node and edges for search",
    )

    @field_serializer("internal_nodes", "internal_edges")
    def _serialize_internal_piles(self, value: Pile) -> Any:
        """
        Serialize the internal nodes and edges.

        Args:
            value: The Pile of internal nodes or edges to serialize.

        Returns:
            Serialized representation of the Pile.
        """
        value = value.to_dict()
        value = value["collections"]
        return value

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node (Node): The node to add.

        Raises:
            RelationError: If the node already exists in the graph or
                if the node type is invalid.
        """
        try:
            if not isinstance(node, Node):
                raise RelationError(
                    "Failed to add node: Invalid node type: "
                    "not a <Relational> entity."
                )
            _id = ID.get_id(node)
            self.internal_nodes.insert(len(self.internal_nodes), node)
            self.node_edge_mapping[_id] = {"in": {}, "out": {}}
        except ItemExistsError as e:
            raise RelationError(f"Error adding node: {e}")

    def add_edge(self, edge: Edge, /) -> None:
        """
        Add an edge to the graph.

        Args:
            edge (Edge): The edge to add.

        Raises:
            RelationError: If the edge already exists in the graph or
                if either the head or tail node does not exist in the graph.
        """
        try:
            if not isinstance(edge, Edge):
                raise RelationError("Failed to add edge: Invalid edge type.")
            if (
                edge.head not in self.internal_nodes
                or edge.tail not in self.internal_nodes
            ):
                raise RelationError(
                    "Failed to add edge: Either edge head or tail node does"
                    " not exist in the graph."
                )
            self.internal_edges.insert(len(self.internal_edges), edge)
            self.node_edge_mapping[edge.head]["out"][edge.id] = edge.tail
            self.node_edge_mapping[edge.tail]["in"][edge.id] = edge.head

        except ItemExistsError as e:
            raise RelationError(f"Error adding node: {e}")

    def remove_node(self, node: ID[Node].Ref, /) -> None:
        """
        Remove a node from the graph.

        This method removes a node and all connected edges from the graph.

        Args:
            node (Node | str): The node or node ID to remove.

        Raises:
            RelationError: If the node does not exist in the graph.
        """
        _id = ID.get_id(node)
        if _id not in self.internal_nodes:
            raise RelationError(f"Node {node} not found in the graph nodes.")

        in_edges: dict = self.node_edge_mapping[_id]["in"]
        for edge_id, node_id in in_edges.items():
            self.node_edge_mapping[node_id]["out"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        out_edges: dict = self.node_edge_mapping[_id]["out"]
        for edge_id, node_id in out_edges.items():
            self.node_edge_mapping[node_id]["in"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        self.node_edge_mapping.pop(_id)
        return self.internal_nodes.pop(_id)

    def remove_edge(self, edge: Edge | str, /) -> None:
        """
        Remove an edge from the graph.

        Args:
            edge (Edge | str): The edge or edge ID to remove.

        Raises:
            RelationError: If the edge does not exist in the graph.
        """
        _id = ID.get_id(edge)
        if _id not in self.internal_edges:
            raise RelationError(f"Edge {edge} not found in the graph edges.")

        edge = self.internal_edges[_id]
        self.node_edge_mapping[edge.head]["out"].pop(_id)
        self.node_edge_mapping[edge.tail]["in"].pop(_id)

        return self.internal_edges.pop(_id)

    def find_node_edge(
        self,
        node: Any,
        /,
        direction: Literal["both", "in", "out"] = "both",
    ) -> list[Edge]:
        if direction not in {"both", "in", "out"}:
            raise ValueError("The direction should be 'both', 'in', or 'out'.")

        _id = ID.get_id(node)
        if _id not in self.internal_nodes:
            raise RelationError(f"Node {node} not found in the graph nodes.")

        result = []

        if direction in {"in", "both"}:
            for edge_id in self.node_edge_mapping[_id]["in"].keys():
                result.append(self.internal_edges[edge_id])

        if direction in {"out", "both"}:
            for edge_id in self.node_edge_mapping[_id]["out"].keys():
                result.append(self.internal_edges[edge_id])

        return result

    def get_heads(self) -> list[Node]:
        """
        Get all head nodes in the graph.

        Head nodes are nodes with no incoming edges.

        Returns:
            Pile: A Pile containing all head nodes.
        """

        result = []
        for node_id in self.node_edge_mapping.keys():
            if self.node_edge_mapping[node_id]["in"] == {}:
                result.append(self.internal_nodes[node_id])
        return result

    def get_predecessors(self, node: Node, /) -> list[Node]:
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
        return result

    def get_successors(self, node: Node, /) -> list[Node]:
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
        return result

    def to_networkx(self, **kwargs) -> Any:
        """Convert the graph to a NetworkX graph object."""
        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node in self.internal_nodes:
            node_info = node.to_dict()
            node_info.pop("id")
            if hasattr(node, "name"):
                node_info.update({"name": node.name})
            g.add_node(str(node.id), **node_info)

        for _edge in self.internal_edges:
            edge_info = _edge.to_dict()
            edge_info.pop("id")
            if hasattr(_edge, "name"):
                edge_info.update({"name": _edge.name})
            source_node_id = edge_info.pop("head")
            target_node_id = edge_info.pop("tail")
            g.add_edge(str(source_node_id), target_node_id, **edge_info)

        return g

    def display(
        self,
        node_label="lion_class",
        edge_label="label",
        draw_kwargs={},
        **kwargs,
    ):
        """Display the graph using NetworkX and Matplotlib."""

        try:
            import matplotlib.pyplot as plt  # type: ignore
        except ImportError:
            raise ImportError(
                "Failed to import Matplotlib. Please install the package with `pip install matplotlib`"
            )

        import networkx as nx

        g = self.to_networkx(**kwargs)
        pos = nx.spring_layout(g)
        nx.draw(
            g,
            pos,
            edge_color="black",
            width=1,
            linewidths=1,
            node_size=500,
            node_color="orange",
            alpha=0.9,
            labels=nx.get_node_attributes(g, node_label),
            **draw_kwargs,
        )

        labels = nx.get_edge_attributes(g, edge_label)
        labels = {k: v for k, v in labels.items() if v}

        if labels:
            nx.draw_networkx_edge_labels(
                g, pos, edge_labels=labels, font_color="purple"
            )

        plt.axis("off")
        plt.show()

    def is_acyclic(self) -> bool:
        """Check if the graph is acyclic (contains no cycles)."""
        node_ids = list(self.internal_nodes.keys())
        check_deque = deque(node_ids)
        check_dict = {
            key: 0 for key in node_ids
        }  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            # Use node_edge_mapping instead of relations
            for edge_id in self.node_edge_mapping[key]["out"].keys():
                edge = self.internal_edges[edge_id]
                check = visit(edge.tail)
                if not check:
                    return False

            check_dict[key] = 2
            return True

        while check_deque:
            key = check_deque.pop()
            check = visit(key)
            if not check:
                return False
        return True

    def __contains__(self, item: object) -> bool:
        return item in self.internal_nodes or item in self.internal_edges
