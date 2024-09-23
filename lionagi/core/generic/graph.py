from collections import deque
from typing import Any

from lion_core.graph.graph import Graph as CoreGraph
from lionagi.core.generic.node import Node


class Graph(CoreGraph, Node):
    """Represents a graph structure with nodes and edges."""

    def is_empty(self) -> bool:
        """Check if the graph is empty (has no nodes)."""
        return self.internal_nodes.is_empty()

    def is_acyclic(self) -> bool:
        """Check if the graph is acyclic (contains no cycles)."""
        node_ids = list(self.internal_nodes.keys())
        check_deque = deque(node_ids)
        check_dict = {key: 0 for key in node_ids}  # 0: not visited, 1: temp, 2: perm

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

        DiGraph = SysUtil.check_import("networkx", import_name="DiGraph")

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
        self, node_label="class_name", edge_label="label", draw_kwargs={}, **kwargs
    ):
        """Display the graph using NetworkX and Matplotlib."""
        from lionagi.libs import SysUtil

        nx = SysUtil.check_import("networkx")
        plt = SysUtil.check_import("matplotlib", "pyplot")

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
