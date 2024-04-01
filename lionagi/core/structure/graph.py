from typing import Any
from .base_structure import BaseStructure


class Graph(BaseStructure):

    def to_networkx(self, **kwargs) -> Any:
        """
        Convert the graph to a NetworkX graph.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX graph constructor.

        Returns:
            Any: The NetworkX graph object.
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node_id, node in self.structure_nodes.items():
            node_info = node.to_dict()
            node_info.pop("node_id")
            node_info.update({"class_name": node.__class__.__name__})
            g.add_node(node_id, **node_info)

        for _, edge in self.structure_edges.items():
            edge_info = edge.to_dict()
            edge_info.pop("node_id")
            edge_info.update({"class_name": edge.__class__.__name__})
            source_node_id = edge_info.pop("source_node_id")
            target_node_id = edge_info.pop("target_node_id")
            g.add_edge(source_node_id, target_node_id, **edge_info)

        return g
