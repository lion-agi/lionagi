from collections import deque
from typing import Any
from lionagi.core.structure.base_structure import BaseStructure


class Graph(BaseStructure):

    def get_heads(self):
        return [
            self.structure_nodes[key]
            for key in self.node_edges
            if not self.node_edges[key]["in"]
        ]

    def acyclic(self):
        """
        Check if the structure's graph is acyclic.

        Returns:
            bool: True if the graph is acyclic, False otherwise.
        """
        check_deque = deque(self.node_id_list)
        check_dict = {
            key: 0 for key in self.node_id_list
        }  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            out_edges = self.get_node_edges(self.structure_nodes[key])

            for edge in out_edges:
                check = visit(edge.target_node_id)
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
    