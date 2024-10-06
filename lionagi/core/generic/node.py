from lion_core.generic.note import Note, note
from lionabc import Relational
from lionabc.exceptions import LionRelationError
from lionfuncs import to_list
from pydantic import Field

from lionagi.core.collections.pile import Pile
from lionagi.core.generic.component import Component
from lionagi.core.generic.edge import Edge
from lionagi.core.generic.edge_condition import EdgeCondition
from lionagi.core.sys_util import SysUtil


class Node(Component, Relational):

    relations: Note = Field(
        default_factory=lambda: note(
            **{"in": Pile(item_type={Relational}), "out": Pile(item_type={Relational})}
        ),
        description="The relations of the node.",
    )

    @property
    def edges(self) -> Pile[Edge]:
        return self.relations.get("in", []) + self.relations.get("out", [])

    @property
    def related_nodes(self) -> list[str]:
        """
        Get list of all unique node IDs directly related to this node.

        Returns:
            List of node IDs related to this node.
        """
        all_nodes = to_list(
            [[i.head, i.tail] for i in self.edges],
            flatten=True,
            dropna=True,
            unique=True,
        )
        all_nodes.remove(self.ln_id)
        return all_nodes

    @property
    def node_relations(self) -> dict[str, dict[str, list[Edge]]]:
        """
        Get categorized view of direct relationships into groups.

        Returns:
            Dict with keys 'in' and 'out', each containing a mapping of
            related node IDs to lists of edges representing relationships.
        """
        out_node_edges = {}
        if self.relations.get("out", None) is not None:
            for edge in self.relations["out"]:
                for node_id in self.related_nodes:
                    if edge.tail == node_id:
                        out_node_edges.setdefault(node_id, []).append(edge)

        in_node_edges = {}
        if self.relations.get("in", None) is not None:
            for edge in self.relations["in"]:
                for node_id in self.related_nodes:
                    if edge.head == node_id:
                        in_node_edges.setdefault(node_id, []).append(edge)

        return {"out": out_node_edges, "in": in_node_edges}

    @property
    def predecessors(self) -> list[str]:
        """
        Get list of IDs of nodes with direct incoming relation to this.

        Returns:
            List of node IDs that precede this node.
        """
        return to_list(
            [k for k, v in self.node_relations["in"].items() if v],
            flatten=True,
            dropna=True,
            unique=True,
        )

    @property
    def successors(self) -> list[str]:
        """
        Get list of IDs of nodes with direct outgoing relation from this.

        Returns:
            List of node IDs that succeed this node.
        """
        return to_list(
            [k for k, v in self.node_relations["out"].items() if v],
            flatten=True,
            dropna=True,
            unique=True,
        )

    def relate(
        self,
        node: "Node",
        direction: str = "out",
        condition: EdgeCondition | None = None,
        label: str | None = None,
        edge_class: type[Edge] = Edge,
        **kwargs,
    ) -> None:
        """
        Establish directed relationship from this node to another.

        Args:
            node: Target node to relate to.
            direction: Direction of edge ('in' or 'out'). Default 'out'.
            condition: Optional condition to associate with edge.
            label: Optional label for edge.
            bundle: Whether to bundle edge with others. Default False.

        Raises:
            ValueError: If direction is neither 'in' nor 'out'.
        """
        if direction not in ["in", "out"]:
            raise ValueError(
                f"Invalid value for direction: {direction}, must be 'in' or 'out'"
            )

        edge = edge_class(
            head=self if direction == "out" else node,
            tail=node if direction == "out" else self,
            condition=condition,
            label=label,
            **kwargs,
        )

        self.relations[direction].append(edge)
        node.relations["in" if direction == "out" else "out"].append(edge)

    def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
        """
        Remove specified edge or all edges between this and another node.

        Args:
            node: Other node involved in edge.
            edge: Specific edge to remove or 'all' to remove all edges.

        Returns:
            True if edge(s) successfully removed, False otherwise.

        Raises:
            RelationError: If removal fails or edge does not exist.
        """
        edge_list = [
            self.relations["in"],
            self.relations["out"],
            node.relations["in"],
            node.relations["out"],
        ]

        if not all([edge in i for i in edge_list]):
            raise LionRelationError(f"Failed to remove edge between nodes.")

        self.relations["in"].remove(edge)
        self.relations["out"].remove(edge)
        node.relations["in"].remove(edge)
        node.relations["out"].remove(edge)

    def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
        """
        Remove all or specific relationships between this and another node.

        Args:
            node: Other node to unrelate from.
            edge: Specific edge to remove or 'all' for all. Default 'all'.

        Returns:
            True if relationships successfully removed, False otherwise.

        Raises:
            RelationError: If operation fails to unrelate nodes.
        """
        edges = []
        if edge == "all":

            for i in self.node_relations["out"]:
                if i.ln_id == node.ln_id:
                    edges.append(i)
                    break
            for i in self.node_relations["in"]:
                if i.ln_id == node.ln_id:
                    edges.append(i)
                    break

        else:
            edges = [SysUtil.get_id(edge)]

        if not edges:
            raise LionRelationError(f"Node is not related to {node.ln_id}.")

        try:
            for edge_id in edges:
                self.remove_edge(node, edge_id)
        except LionRelationError as e:
            raise e
