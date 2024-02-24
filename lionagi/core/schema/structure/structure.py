from typing import TypeVar

from lionagi.core.schema import BaseNode
from .graph import Graph

T = TypeVar('T', bound='BaseNode')
R = TypeVar('R', bound='Relationship')


class Structure(BaseNode):
    """
    Represents the structure of a graph consisting of nodes and relationship.
    """
    graph: Graph = Graph()

    def add_node(self, node: T) -> None:
        """
        Adds a node to the structure.
        
        Args:
            node (T): The node instance to be added.
        """
        self.graph.add_node(node)

    def add_relationship(self, relationship: R) -> None:
        """
        Adds a relationship to the structure.
        
        Args:
            relationship (R): The relationship instance to be added.
        """
        self.graph.add_relationship(relationship)

    def get_relationships(self) -> list[R]:
        return self.graph.get_node_relationships()

    def get_node_relationships(self, node: T, out_edge=True, labels=None) -> R:
        relationships = self.graph.get_node_relationships(node, out_edge)
        if labels:
            if not isinstance(labels, list):
                labels = [labels]
            result = []
            for r in relationships:
                if r.label in labels:
                    result.append(r)
            relationships = result
        return relationships

    def node_exist(self, node: T) -> bool:
        """
        Checks if a node exists in the structure.
        
        Args:
            node (T): The node instance or node ID to check for existence.
            
        Returns:
            bool: True if the node exists, False otherwise.
        """

        return self.graph.node_exist(node)
    
    def relationship_exist(self, relationship: R) -> bool:
        """
        Checks if a relationship exists in the structure.
        
        Args:
            relationship (R): The relationship instance to check for existence.
            
        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        return self.graph.relationship_exists(relationship)

    def remove_node(self, node: T) -> T:
        """
        Removes a node and its associated relationship from the structure.
        
        Args:
            node (T): The node instance or node ID to be removed.
        """
        return self.graph.remove_node(node)

    def remove_relationship(self, relationship: R) -> R:
        """
        Removes a relationship from the structure.
        
        Args:
            relationship (R): The relationship instance to be removed.
        """
        return self.graph.remove_relationship(relationship)

    def is_empty(self) -> bool:
        return self.graph.is_empty()
