import contextlib
from collections import deque
from typing import Any

from lionagi.core.collections import Pile, pile
from lionagi.core.collections.abc import (
    Actionable,
    Condition,
    ItemNotFoundError,
    LionIDable,
    LionTypeError,
)
from lionagi.core.generic.edge import Edge
from lionagi.core.generic.node import Node
from lionagi.libs.ln_convert import to_list


class Graph(Node):
    """Represents a graph structure with nodes and edges."""

    internal_nodes: Pile = pile()

    @property
    def internal_edges(self) -> Pile[Edge]:
        """Return a pile of all edges in the graph."""
        return pile(
            {
                edge.ln_id: edge
                for node in self.internal_nodes
                for edge in node.edges
            },
            Edge,
        )

    def is_empty(self) -> bool:
        """Check if the graph is empty (has no nodes)."""
        return self.internal_nodes.is_empty()

    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.internal_nodes.clear()

    def add_edge(
        self,
        head: Node,
        tail: Node,
        condition: Condition | None = None,
        bundle=False,
        label=None,
        edge_class=Edge,
        **kwargs,
    ):
        """Add an edge between two nodes in the graph."""
        if isinstance(head, Actionable):
            raise LionTypeError("Actionable nodes cannot be related as head.")
        if isinstance(tail, Actionable):
            bundle = True

        self.internal_nodes.include(head)
        self.internal_nodes.include(tail)

        head.relate(
            tail,
            direction="out",
            condition=condition,
            label=label,
            bundle=bundle,
            edge_class=edge_class,
            **kwargs,
        )

    def remove_edge(self, edge: Any) -> bool:
        """Remove an edge from the graph."""
        edge = edge if isinstance(edge, list) else [edge]
        for i in edge:
            if i not in self.internal_edges:
                raise ItemNotFoundError(
                    f"Edge {i} does not exist in structure."
                )
            with contextlib.suppress(ItemNotFoundError):
                self._remove_edge(i)

    def add_node(self, node: Any) -> None:
        """Add a node to the graph."""
        self.internal_nodes.update(node)

    def get_node(self, item: LionIDable, default=...):
        """Get a node from the graph by its identifier."""
        return self.internal_nodes.get(item, default)

    def get_node_edges(
        self,
        node: Node | str,
        direction: str = "both",
        label: list | str = None,
    ) -> Pile[Edge] | None:
        """Get the edges of a node in the specified direction and with the given label."""
        node = self.internal_nodes[node]
        edges = None
        match direction:
            case "both":
                edges = node.edges
            case "head" | "predecessor" | "outgoing" | "out" | "predecessors":
                edges = node.relations["out"]
            case "tail" | "successor" | "incoming" | "in" | "successors":
                edges = node.relations["in"]

        if label:
            return (
                pile(
                    [
                        edge
                        for edge in edges
                        if edge.label
                        in to_list(label, dropna=True, flatten=True)
                    ]
                )
                if edges
                else None
            )
        return pile(edges) if edges else None

    def pop_node(self, item, default=...):
        """Remove and return a node from the graph by its identifier."""
        return self.internal_nodes.pop(item, default)

    def remove_node(self, item):
        """Remove a node from the graph by its identifier."""
        return self.internal_nodes.remove(item)

    def _remove_edge(self, edge: Edge | str) -> bool:
        """Remove a specific edge from the graph."""
        if edge not in self.internal_edges:
            raise ItemNotFoundError(
                f"Edge {edge} does not exist in structure."
            )

        edge = self.internal_edges[edge]
        head: Node = self.internal_nodes[edge.head]
        tail: Node = self.internal_nodes[edge.tail]

        head.unrelate(tail, edge=edge)
        return True

    def get_heads(self) -> Pile:
        """Get all head nodes in the graph."""
        return pile(
            [
                node
                for node in self.internal_nodes
                if node.relations["in"].is_empty()
                and not isinstance(node, Actionable)
            ]
        )

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

            for edge in self.internal_nodes[key].relations["out"]:
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

    def to_networkx(self, **kwargs) -> Any:
        """Convert the graph to a NetworkX graph object."""
        from lionagi.libs import SysUtil

        SysUtil.check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node in self.internal_nodes:
            node_info = node.to_dict()
            node_info.pop("ln_id")
            node_info.update({"class_name": node.class_name})
            if hasattr(node, "name"):
                node_info.update({"name": node.name})
            g.add_node(node.ln_id, **node_info)

        for _edge in self.internal_edges:
            edge_info = _edge.to_dict()
            edge_info.pop("ln_id")
            edge_info.update({"class_name": _edge.class_name})
            if hasattr(_edge, "name"):
                edge_info.update({"name": _edge.name})
            source_node_id = edge_info.pop("head")
            target_node_id = edge_info.pop("tail")
            g.add_edge(source_node_id, target_node_id, **edge_info)

        return g

    def display(
        self,
        node_label="class_name",
        edge_label="label",
        draw_kwargs={},
        **kwargs,
    ):
        """Display the graph using NetworkX and Matplotlib."""
        from lionagi.libs import SysUtil

        SysUtil.check_import("networkx")
        SysUtil.check_import("matplotlib", "pyplot")

        import matplotlib.pyplot as plt
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

    def size(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self.internal_nodes)
