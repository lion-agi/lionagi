from typing import List, Any
from pydantic import Field

from ..utils.call_util import lcall
from ..schema.base_node import BaseNode
from .relationship import Relationship


class Graph(BaseNode):
    """
    Represents a graph structure, consisting of nodes and their relationships.
    
    Attributes:
        nodes (Dict[str, BaseNode]): A dictionary of nodes in the graph.
        relationships (Dict[str, Relationship]): A dictionary of relationships between nodes in the graph.
        node_relationships (Dict[str, Dict[str, Dict[str, str]]]): A dictionary tracking the relationships of each node.
    
    Examples:
        >>> graph = Graph()
        >>> node = BaseNode(id_='node1')
        >>> graph.add_node(node)
        >>> graph.node_exists(node)
        True
        >>> relationship = Relationship(id_='rel1', source_node_id='node1', target_node_id='node2')
        >>> graph.add_relationship(relationship)
        >>> graph.relationship_exists(relationship)
        True
    """
    nodes: dict = Field(default={})
    relationships: dict = Field(default={})
    node_relationships: dict = Field(default={})

    def add_node(self, node: BaseNode) -> None:
        """
        Adds a node to the graph.

        Args:
            node (BaseNode): The node to add to the graph.
        """

        self.nodes[node.id_] = node
        self.node_relationships[node.id_] = {'in': {}, 'out': {}}

    def add_relationship(self, relationships: Relationship) -> None:
        """
        Adds a relationship between nodes in the graph.

        Args:
            relationship (Relationship): The relationship to add.

        Raises:
            KeyError: If either the source or target node of the relationship is not found in the graph.
        """
        if relationships.source_node_id not in self.node_relationships.keys():
            raise KeyError(f'node {relationships.source_node_id} is not found.')
        if relationships.target_node_id not in self.node_relationships.keys():
            raise KeyError(f'node {relationships.target_node_id} is not found.')

        self.relationships[relationships.id_] = relationships
        self.node_relationships[relationships.source_node_id]['out'][relationships.id_] = relationships.target_node_id
        self.node_relationships[relationships.target_node_id]['in'][relationships.id_] = relationships.source_node_id

    def get_node_relationships(self, node: BaseNode = None, out_edge=True) -> List[Relationship]:
        """
        Retrieves relationships of a specific node or all relationships in the graph.

        Args:
            node (Optional[BaseNode]): The node whose relationships to retrieve. If None, retrieves all relationships.
            out_edge (bool): Whether to retrieve outgoing relationships. If False, retrieves incoming relationships.

        Returns:
            List[Relationship]: A list of relationships.

        Raises:
            KeyError: If the specified node is not found in the graph.
        """
        if node is None:
            return list(self.relationships.values())

        if node.id_ not in self.nodes.keys():
            raise KeyError(f'node {node.id_} is not found')

        if out_edge:
            relationship_ids = list(self.node_relationships[node.id_]['out'].keys())
            relationships = lcall(relationship_ids, lambda i: self.relationships[i])
            return relationships
        else:
            relationship_ids = list(self.node_relationships[node.id_]['in'].keys())
            relationships = lcall(relationship_ids, lambda i: self.relationships[i])
            return relationships

    def remove_node(self, node: BaseNode)-> BaseNode:
        """
        Removes a node and its associated relationships from the graph.

        Args:
            node (BaseNode): The node to remove.

        Returns:
            BaseNode: The removed node.

        Raises:
            KeyError: If the node is not found in the graph.
        """
        if node.id_ not in self.nodes.keys():
            raise KeyError(f'node {node.id_} is not found')

        out_relationship = self.node_relationships[node.id_]['out']
        for relationship_id, node_id in out_relationship.items():
            self.node_relationships[node_id]['in'].pop(relationship_id)
            self.relationships.pop(relationship_id)

        in_relationship = self.node_relationships[node.id_]['in']
        for relationship_id, node_id in in_relationship.items():
            self.node_relationships[node_id]['out'].pop(relationship_id)
            self.relationships.pop(relationship_id)

        self.node_relationships.pop(node.id_)
        return self.nodes.pop(node.id_)

    def remove_relationship(self, relationship: Relationship) -> Relationship:
        """
        Removes a relationship from the graph.

        Args:
            relationship (Relationship): The relationship to remove.

        Returns:
            Relationship: The removed relationship.

        Raises:
            KeyError: If the relationship is not found in the graph.
        """
        if relationship.id_ not in self.relationships.keys():
            raise KeyError(f'relationship {relationship.id_} is not found')

        self.node_relationships[relationship.source_node_id]['out'].pop(relationship.id_)
        self.node_relationships[relationship.target_node_id]['in'].pop(relationship.id_)

        return self.relationships.pop(relationship.id_)

    def node_exists(self, node: BaseNode) -> bool:
        """
        Checks if a node exists in the graph.

        Args:
            node (BaseNode): The node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        if node.id_ in self.nodes.keys():
            return True
        else:
            return False

    def relationship_exists(self, relationship: Relationship) -> bool:
        """
        Checks if a relationship exists in the graph.

        Args:
            relationship (Relationship): The relationship to check.

        Returns:
            bool: True if the relationship exists, False otherwise.
        """
        if relationship.id_ in self.relationships.keys():
            return True
        else:
            return False

    def is_empty(self) -> bool:
        """
        Determines if the graph is empty.

        Returns:
            bool: True if the graph has no nodes, False otherwise.
        """
        if self.nodes:
            return False
        else:
            return True

    def clear(self)-> None:
        """Clears the graph of all nodes and relationships."""
        self.nodes.clear()
        self.relationships.clear()
        self.node_relationships.clear()

    def to_networkx(self, **kwargs) -> Any:
        """
        Converts the graph to a NetworkX graph object.

        Args:
            **kwargs: Additional keyword arguments to pass to the NetworkX DiGraph constructor.

        Returns:
            Any: A NetworkX directed graph representing the graph.

        Examples:
            >>> graph = Graph()
            >>> nx_graph = graph.to_networkx()
        """
        import networkx as nx
        g = nx.DiGraph(**kwargs)
        for node_id, node in self.nodes.items():
            node_info = node.to_dict()
            node_info.pop('node_id')
            g.add_node(node_id, **node_info)

        for relationship_id, relationship in self.relationships.items():
            relationship_info = relationship.to_dict()
            relationship_info.pop('node_id')
            source_node_id = relationship_info.pop('source_node_id')
            target_node_id = relationship_info.pop('target_node_id')
            g.add_edge(source_node_id, target_node_id, **relationship_info)

        return g
