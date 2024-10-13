from typing import Any

from lion_core.graph import Graph as CoreGraph
from lionfuncs import check_import

from lionagi.core.generic.node import Node


class Graph(CoreGraph, Node):

    def to_networkx(self, **kwargs) -> Any:
        """Convert the graph to a NetworkX graph object."""

        DiGraph = check_import(
            package_name="networkx",
            import_name="DiGraph",
        )

        g = DiGraph(**kwargs)
        for node in self.internal_nodes:
            node_info = node.to_dict()
            node_info.pop("ln_id")
            node_info.update({"class_name": node.class_name()})
            if hasattr(node, "name"):
                node_info.update({"name": node.name})
            g.add_node(node.ln_id, **node_info)

        for _edge in self.internal_edges:
            edge_info = _edge.to_dict()
            edge_info.pop("ln_id")
            edge_info.update({"class_name": _edge.class_name()})
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

        nx = check_import("networkx")
        plt = check_import(
            package_name="matplotlib",
            module_name="pyplot",
        )

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


__all__ = ["Graph"]
