from typing import List, Any
from pydantic import Field
from lionagi.libs import SysUtil
from ..relations import Relationship
from ..schema import BaseNode
from .base_structure import BaseStructure


class Graph(BaseStructure):
    """
    A class representing a graph structure.

    Attributes:
        relationships (dict): A dictionary storing the relationships between nodes.
    """

    relationships: dict = Field(default={})

    @property
    def node_relationships(self):
        """
        Get the node relationships in the graph.

        Returns:
            dict: A dictionary containing the incoming and outgoing relationships for each node.
        """
        _output = {}
        for _node in self.nodes.values():
            _output[_node.id_] = {
                "in": _node.in_relations,
                "out": _node.out_relations,
            }
        return _output

    def has_relationship(self, relationship: Relationship | str) -> bool:
        """
        Check if a relationship exists in the graph.

        Args:
            relationship (Relationship | str): The relationship object or its ID.

        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        return (
            True
            if self.relationships.get(
                (
                    relationship.id_
                    if isinstance(relationship, BaseNode)
                    else relationship
                ),
                None,
            )
            else False
        )

    def add_relationship(self, relationship: Relationship) -> None:
        """
        Add a relationship to the graph.

        Args:
            relationship (Relationship): The relationship object to add.

        Raises:
            ValueError: If there is an error adding the relationship.
        """
        try:
            in_node: BaseNode = self.get_node(relationship.source_node_id)
            out_node: BaseNode = self.get_node(relationship.target_node_id)

            if self.has_node(in_node.id_) and self.has_node(out_node.id_):
                in_node.add_relation(out_node, relationship, direction="out")
                out_node.add_relation(in_node, relationship, direction="in")

            self.relationships[relationship.id_] = relationship
        except Exception as e:
            raise ValueError(f"Error adding relationship: {e}")

    def get_node_relationships(
        self, node: BaseNode = None, out_edge=True
    ) -> List[Relationship]:
        """
        Get the relationships of a node.

        Args:
            node (BaseNode, optional): The node to get relationships for. If None, all relationships are returned.
            out_edge (bool, optional): If True, get outgoing relationships. If False, get incoming relationships.

        Returns:
            List[Relationship]: A list of relationships for the node.

        Raises:
            KeyError: If the node is not found in the graph.
        """
        if node is None:
            return list(self.relationships.values())

        if node.id_ not in self.nodes:
            raise KeyError(f"node {node.id_} is not found")

        if out_edge:
            return list(node.out_relations.values())

        return list(node.in_relations.values())

    def get_node_predecessors(self, node: BaseNode):
        """
        Get the predecessor nodes of a node.

        Args:
            node (BaseNode): The node to get predecessors for.

        Returns:
            List[BaseNode]: A list of predecessor nodes.
        """

        return self.get_node(node.predecessors)

    def get_node_successors(self, node: BaseNode):
        """
        Get the successor nodes of a node.

        Args:
            node (BaseNode): The node to get successors for.

        Returns:
            List[BaseNode]: A list of successor nodes.
        """
        return self.get_node(node.successors)

    def remove_relationship(
        self, relationship: Relationship | str = None
    ) -> Relationship:
        """
        Remove a relationship from the graph.

        Args:
            relationship (Relationship | str, optional): The relationship object or its ID to remove.

        Returns:
            Relationship: The removed relationship object.
        """
        if isinstance(relationship, str):
            relationship = self.relationships.get(relationship, None)

        source_node: BaseNode = self.get_node(relationship.source_node_id)
        target_node: BaseNode = self.get_node(relationship.target_node_id)

        source_node.pop_relation(relationship, target_node)
        self.relationships.pop(relationship.id_)
        return relationship

    def remove_node(self, node: BaseNode) -> bool:
        """
        Remove a node from the graph.

        Args:
            node (BaseNode): The node to remove.

        Returns:
            bool: True if the node is successfully removed, False otherwise.
        """
        for i in node.all_relationships:
            j = self.relationships[i]
            self.remove_relationship(j)

        self.pop_node(node)

    def clear(self) -> None:
        """Clears the graph of all nodes and relationship."""
        self.nodes.clear()
        self.relationships.clear()

    def to_networkx(self, **kwargs) -> Any:
        """
        Convert the graph to a NetworkX graph.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX graph constructor.

        Returns:
            Any: The NetworkX graph object.
        """
        SysUtil.check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node_id, node in self.nodes.items():
            node_info = node.to_dict()
            node_info.pop("node_id")
            node_info.update({"class_name": node.__class__.__name__})
            g.add_node(node_id, **node_info)

        for _, relationship in self.relationships.items():
            relationship_info = relationship.to_dict()
            relationship_info.pop("node_id")
            relationship_info.update({"class_name": relationship.__class__.__name__})
            source_node_id = relationship_info.pop("source_node_id")
            target_node_id = relationship_info.pop("target_node_id")
            g.add_edge(source_node_id, target_node_id, **relationship_info)

        return g
