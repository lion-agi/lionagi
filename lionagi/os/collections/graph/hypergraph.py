# from collections import deque
# from typing import Any, List, Union
# import contextlib
# from lionagi.os.libs import to_list
# from ..abc import (
#     Condition,
#     Actionable,
#     LionTypeError,
#     ItemNotFoundError,
#     LionIDable,
# )
# from ..pile.pile import pile, Pile
# from ..node.node import Node
# from ..edge.hyperedge import HyperEdge
# from .graph import Graph


# class HyperGraph(Graph):
#     """Represents a hypergraph structure with nodes and hyperedges."""

#     @property
#     def internal_hyperedges(self) -> Pile[HyperEdge]:
#         """Return a pile of all hyperedges in the hypergraph."""
#         return pile(
#             {
#                 hyperedge.ln_id: hyperedge
#                 for node in self.internal_nodes
#                 for hyperedge in node.edges
#                 if isinstance(hyperedge, HyperEdge)
#             },
#             HyperEdge,
#         )

#     def add_hyperedge(
#         self,
#         nodes: List[Node],
#         condition: Condition | None = None,
#         bundle=False,
#         label=None,
#         **kwargs,
#     ):
#         """Add a hyperedge connecting multiple nodes in the hypergraph."""
#         if any(isinstance(node, Actionable) for node in nodes):
#             raise LionTypeError("Actionable nodes cannot be part of a hyperedge.")

#         self.internal_nodes.include(nodes)

#         hyperedge = HyperEdge(
#             nodes=[node.ln_id for node in nodes],
#             condition=condition,
#             label=label,
#             bundle=bundle,
#             **kwargs,
#         )

#         for node in nodes:
#             node.relations["out"].include(hyperedge)
#             for other_node in nodes:
#                 if other_node != node:
#                     other_node.relations["in"].include(hyperedge)

#     def remove_hyperedge(self, hyperedge: Any) -> bool:
#         """Remove a hyperedge from the hypergraph."""
#         hyperedge = hyperedge if isinstance(hyperedge, list) else [hyperedge]
#         for i in hyperedge:
#             if i not in self.internal_hyperedges:
#                 raise ItemNotFoundError(f"Hyperedge {i} does not exist in structure.")
#             with contextlib.suppress(ItemNotFoundError):
#                 self._remove_hyperedge(i)

#     def _remove_hyperedge(self, hyperedge: HyperEdge | str) -> bool:
#         """Remove a specific hyperedge from the hypergraph."""
#         if hyperedge not in self.internal_hyperedges:
#             raise ItemNotFoundError(
#                 f"Hyperedge {hyperedge} does not exist in structure."
#             )

#         hyperedge = self.internal_hyperedges[hyperedge]

#         for node_id in hyperedge.nodes:
#             node = self.internal_nodes[node_id]
#             node.relations["out"].exclude(hyperedge)
#             for other_node_id in hyperedge.nodes:
#                 if other_node_id != node_id:
#                     other_node = self.internal_nodes[other_node_id]
#                     other_node.relations["in"].exclude(hyperedge)

#         return True

#     def get_hyperedges(self, node: Node | str = None) -> Pile[HyperEdge]:
#         """Get all hyperedges or the hyperedges of a specific node."""
#         if node:
#             node = self.internal_nodes[node]
#             return pile([edge for edge in node.edges if isinstance(edge, HyperEdge)])
#         return pile(
#             [edge for edge in self.internal_hyperedges if isinstance(edge, HyperEdge)]
#         )

#     def display(self, **kwargs):
#         """Display the hypergraph using NetworkX and Matplotlib."""
#         from lionagi.os.libs.sys_util import check_import

#         check_import("networkx")
#         check_import("matplotlib", "pyplot")

#         import networkx as nx
#         import matplotlib.pyplot as plt

#         g = self.to_networkx(**kwargs)
#         pos = nx.spring_layout(g)
#         nx.draw(
#             g,
#             pos,
#             edge_color="black",
#             width=1,
#             linewidths=1,
#             node_size=500,
#             node_color="orange",
#             alpha=0.9,
#             labels=nx.get_node_attributes(g, "class_name"),
#         )

#         labels = nx.get_edge_attributes(g, "label")
#         labels = {k: v for k, v in labels.items() if v}

#         if labels:
#             nx.draw_networkx_edge_labels(
#                 g, pos, edge_labels=labels, font_color="purple"
#             )

#         plt.axis("off")
#         plt.show()

#     def size(self) -> int:
#         """Return the number of nodes in the hypergraph."""
#         return len(self.internal_nodes)

#     def relate(
#         self,
#         nodes: List[Node],
#         condition: Condition | None = None,
#         label: str | None = None,
#         bundle: bool = False,
#     ) -> None:
#         """
#         Establish directed relationship from this node to multiple other nodes.

#         Args:
#             nodes: Target nodes to relate to.
#             condition: Optional condition to associate with edge.
#             label: Optional label for edge.
#             bundle: Whether to bundle edge with others. Default False.
#         """
#         hyperedge = HyperEdge(
#             nodes=[self.ln_id] + [node.ln_id for node in nodes],
#             condition=condition,
#             bundle=bundle,
#             label=label,
#         )

#         self.relations["out"].include(hyperedge)
#         for node in nodes:
#             node.relations["in"].include(hyperedge)
