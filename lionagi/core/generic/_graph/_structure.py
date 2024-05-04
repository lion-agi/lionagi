from typing import Any
from pydantic import Field

from lionagi.libs import convert
from ..abc import Condition, Actionable, LionTypeError, ItemNotFoundError, LionIDable
from .._edge._edge import Edge
from .._node._node import Node
from .._pile import Pile, pile


class Structure(Node):

    internal_nodes: Pile = Field(Pile())

    @property
    def internal_edges(self) -> dict[str, Edge]:
        return pile(
            {edge.ln_id: edge for node in self.internal_nodes for edge in node.edges},
            Edge,
        )

    def is_empty(self) -> bool:
        return self.internal_nodes.is_empty()

    def clear(self):
        self.internal_nodes.clear()

    def relate_nodes(
        self,
        head: Node,
        tail: Node,
        condition: Condition | None = None,
        bundle=False,
        label=None,
        **kwargs,
    ):
        """
        relate and include nodes in the structure
        """
        if isinstance(head, Actionable):
            raise LionTypeError(f"Actionable nodes cannot be related as head.")
        if isinstance(tail, Actionable):
            bundle = True

        self.internal_nodes += head
        self.internal_nodes += tail

        head.relate(
            tail,
            direction="out",
            condition=condition,
            label=label,
            bundle=bundle,
            **kwargs,
        )

    def remove_edge(self, edge: Any) -> bool:
        if all(self._remove_edge(i) for i in edge):
            return True
        return False

    def add_node(self, node: Any) -> None:
        self.internal_nodes.update(node)

    def get_node(self, item: LionIDable, default=...):
        return self.internal_nodes.get(item, default)

    def get_node_edges(
        self,
        node: Node | str,
        direction: str = "both",
        label: list | str = None,
    ) -> dict[str, list[Edge]]:

        node = self.internal_nodes[node]
        edges = None
        match direction:
            case "both":
                edges = node.edges
            case "head", "predecessor", "outgoing", "out", "predecessors":
                edges = node.relations["out"]
            case "tail", "successor", "incoming", "in", "successors":
                edges = node.relations["in_"]

        if label:
            return (
                pile(
                    [
                        edge
                        for edge in edges
                        if edge.label
                        in convert.to_list(label, dropna=True, flatten=True)
                    ]
                )
                if edges
                else None
            )
        return pile(edges) if edges else None

    def pop_node(self, item, default: ..., /):
        return self.internal_nodes.pop(item, default)

    def remove_node(self, item, /):
        return self.internal_nodes.remove(item)

    def _remove_edge(self, edge: Edge | str) -> bool:

        if edge not in self.internal_edges:
            raise ItemNotFoundError(f"Edge {edge} does not exist in structure.")

        edge = self.internal_edges[edge]
        head: Node = self.internal_nodes[edge.head]
        tail: Node = self.internal_nodes[edge.tail]

        head.unrelate(tail, edge=edge)
