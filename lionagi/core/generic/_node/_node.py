from pydantic import Field
from lionagi.libs.ln_convert import to_list
from ..abc import Component, Condition, ItemNotFoundError, Relatable
from .._pile import Pile, CategoricalPile, pile
from .._edge._edge import Edge


class Node(Component, Relatable):

    relations: CategoricalPile = Field(
        default_factory=lambda: CategoricalPile(
            categories={"in": pile(), "out": pile()}
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
        out_node_edges = {}

        if not self.relations["out"].is_empty():
            for edge in self.relations["out"]:
                for i in self.related_nodes:
                    if edge.tail == i:
                        if i in out_node_edges:
                            out_node_edges[i].append(edge)
                        else:
                            out_node_edges[i] = [edge]

        in_node_edges = {}

        if not self.relations["in"].is_empty():
            for edge in self.relations["in"]:
                for i in self.related_nodes:
                    if edge.head == i:
                        if i in in_node_edges:
                            in_node_edges[i].append(edge)
                        else:
                            in_node_edges[i] = [edge]

        return {"out": out_node_edges, "in": in_node_edges}

    @property
    def precedessors(self) -> list[str]:
        """return a list of nodes id that precede this node"""
        return [k for k, v in self.node_relations["in"].items() if len(v) > 0]

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
            node.relations["in"] += edge

        elif direction == "in":
            edge = Edge(
                head=node, tail=self, condition=condition, label=label, bundle=bundle
            )

            self.relations["in"] += edge
            node.relations["out"] += edge

        else:
            raise ValueError(
                f"Invalid value for direction: {direction}, must be 'in' or 'out'"
            )

    def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
        if node.ln_id not in self.related_nodes:
            raise ValueError(f"Node {self.ln_id} is not related to node {node.ln_id}.")

        if edge not in self.relations or edge not in node.relations:
            raise ItemNotFoundError(f"Edge {edge} does not exist between nodes.")

        if self.relations.exclude(edge) and node.relations.exclude(edge):
            return True

        return False

    def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
        if edge == "all":
            edge = self.node_relations["out"].get(node.ln_id, []) + self.node_relations[
                "in"
            ].get(node.ln_id, [])

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
