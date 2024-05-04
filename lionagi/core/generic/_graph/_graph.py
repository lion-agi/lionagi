from collections import deque
from typing import Any

from .._pile import pile
from ._structure import Structure


class Graph(Structure):

    def get_heads(self):
        return pile(
            [node for node in self.internal_nodes if node.relations["in_"].is_empty()]
        )

    @property
    def acyclic(self) -> bool:
        """
        Checks if the graph is acyclic.

        An acyclic graph contains no cycles and can be represented as a directed
        acyclic graph (DAG).

        Returns:
            bool: True if the graph is acyclic, False otherwise.
        """
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
        """
        Converts the graph into a NetworkX graph object.

        The NetworkX graph object can be used for further analysis or
        visualization.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX graph
                constructor.

        Returns:
            Any: A NetworkX graph object representing the current graph
            structure.
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node_id, node in self.internal_nodes.items():
            node_info = node.to_dict()
            node_info.pop("id_")
            node_info.update({"class_name": node.class_name})
            g.add_node(node_id, **node_info)

        for _edge in list(self.internal_edges.values()):
            edge_info = _edge.to_dict()
            edge_info.pop("id_")
            edge_info.update({"class_name": _edge.__class__.__name__})
            source_node_id = edge_info.pop("head")
            target_node_id = edge_info.pop("tail")
            g.add_edge(source_node_id, target_node_id, **edge_info)

        return g

    def display(self, **kwargs):
        """
        Displays the graph using NetworkX's drawing capabilities.

        This method requires NetworkX and a compatible plotting library (like
        matplotlib) to be installed.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX graph
                constructor.
        """
        from lionagi.libs import SysUtil

        SysUtil.check_import("networkx")

        from networkx import draw

        g = self.to_networkx(**kwargs)
        draw(g)
