from pydantic import Field
from lionagi.libs.ln_convert import to_list
from ..abc import Component, Condition, ItemNotFoundError, Relatable
from .._pile import Pile, CategoricalPile
from .._edge._edge import Edge


class Node(Component, Relatable):

    relations: CategoricalPile = Field(
        default_factory=lambda: CategoricalPile(
            categories={"in_": Pile(None, Edge), "out": Pile(None, Edge)}
        ),
        description="The relations of the node.",
    )

    @property
    def edges(self) -> Pile[Edge]:
        return self.relations.all_items()

    @property
    def related_nodes(self) -> list[str]:
        all_nodes = set(
            to_list([[i.head, i.tail] for i in self.edges], flatten=True, dropna=True)
        )

        all_nodes.discard(self.ln_id)
        return list(all_nodes)

    @property
    def node_relations(self) -> dict:
        """Categorizes preceding and succeeding relations to this node."""
        out_nodes = {}
        for edge in self.relations["out"]:
            for i in self.related_nodes:
                if edge.tail == i:
                    if i in out_nodes:
                        out_nodes[i].append(edge)
                    else:
                        out_nodes[i] = [edge]

        in_nodes = {}
        for edge in self.relations["in_"]:
            for i in self.related_nodes:
                if edge.head == i:
                    if i in in_nodes:
                        in_nodes[i].append(edge)
                    else:
                        in_nodes[i] = [edge]

        return {"out": out_nodes, "in_": in_nodes}

    @property
    def precedessors(self) -> list[str]:
        """return a list of nodes id that precede this node"""
        return [k for k, v in self.node_relations["in_"].items() if len(v) > 0]

    @property
    def successors(self) -> list[str]:
        """return a list of nodes id that succeed this node"""
        return [k for k, v in self.node_relations["out"].items() if len(v) > 0]

    def relate(
        self,
        node: "Node",
        direction: str = "out",
        condition: Condition | None = None,
        label: str | None = None,
        bundle=False,
    ) -> None:
        if direction == "out":
            edge = Edge(
                head=self, tail=node, condition=condition, bundle=bundle, label=label
            )
            self.relations["out"] += edge
            node.relations["in_"] += edge

        elif direction == "in_":
            edge = Edge(
                head=node, tail=self, condition=condition, label=label, bundle=bundle
            )
            self.relations["in_"] += edge
            node.relations["out"] += edge

        else:
            raise ValueError(
                f"Invalid value for direction: {direction}, must be 'in_' or 'out'"
            )

    def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
        if node.ln_id not in self.related_nodes:
            raise ValueError(f"Node {self.ln_id} is not related to node {node.id_}.")

        if edge not in self.relations or edge not in node.relations:
            raise ItemNotFoundError(f"Edge {edge} does not exist between nodes.")

        if self.relations.exclude(edge) and node.relations.exclude(edge):
            return True

        return False

    def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
        if edge == "all":
            edge = self.node_relations["out"].get(node.ln_id, []) + self.node_relations[
                "in_"
            ].get(node.id_, [])

        else:
            edge = [edge.ln_id] if isinstance(edge, Edge) else [edge]

        if len(edge) == 0:
            raise ItemNotFoundError(f"Node is not related to {node.ln_id}.")

        try:
            for edge_id in edge:
                self.remove_edge(node, edge_id)
            return True
        except Exception as e:
            raise ValueError(f"Failed to remove edge between nodes.") from e

    def __str__(self) -> str:
        """
        Provides a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        timestamp = f" ({self.timestamp})" if self.timestamp else ""
        if self.content:
            content_preview = (
                f"{self.content[:50]}..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ""
        meta_preview = (
            f"{str(self.metadata)[:50]}..."
            if len(str(self.metadata)) > 50
            else str(self.metadata)
        )
        return (
            f"{self.class_name()}({self.id_}, {content_preview}, {meta_preview},"
            f"{timestamp})"
        )
