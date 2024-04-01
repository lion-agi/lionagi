from typing import List, Any

from pydantic import Field

from lionagi.core.schema import BaseNode, BaseNode, Edge
from lionagi.libs import func_call, SysUtil


class Graph(BaseNode):
    """
    Represents a graph structure, consisting of nodes and their relationships.

    Attributes:
        nodes (Dict[str, BaseNode]): A dictionary of nodes in the graph.
        relationships (Dict[str, lionagi.core.schema.Edge]): A dictionary of relationships between nodes in the graph.
        node_relationships (Dict[str, Dict[str, Dict[str, str]]]): A dictionary tracking the relationships of each node.

    Examples:
        >>> graph = Graph()
        >>> node = BaseNode(id_='node1')
        >>> graph.add_node(node)
        >>> graph.node_exists(node)
        True
        >>> relationship = Edge(id_='rel1', source_node_id='node1', target_node_id='node2')
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
        self.node_relationships[node.id_] = {"in": {}, "out": {}}

    def add_relationship(self, relationship: Edge) -> None:
        """
        Adds a relationship between nodes in the graph.

        Args:
            relationship (Edge): The relationship to add.

        Raises:
            KeyError: If either the source or target node of the relationship is not found in the graph.
        """
        if relationship.source_node_id not in self.node_relationships.keys():
            raise KeyError(f"node {relationship.source_node_id} is not found.")
        if relationship.target_node_id not in self.node_relationships.keys():
            raise KeyError(f"node {relationship.target_node_id} is not found.")

        self.relationships[relationship.id_] = relationship
        self.node_relationships[relationship.source_node_id]["out"][
            relationship.id_
        ] = relationship.target_node_id
        self.node_relationships[relationship.target_node_id]["in"][
            relationship.id_
        ] = relationship.source_node_id

    def get_node_relationships(
        self, node: BaseNode = None, out_edge=True
    ) -> List[Edge]:
        """
        Retrieves relationships of a specific node or all relationships in the graph.

        Args:
            node (Optional[BaseNode]): The node whose relationships to retrieve. If None, retrieves all relationships.
            out_edge (bool): Whether to retrieve outgoing relationships. If False, retrieves incoming relationships.

        Returns:
            List[Edge]: A list of relationships.

        Raises:
            KeyError: If the specified node is not found in the graph.
        """
        if node is None:
            return list(self.relationships.values())

        if node.id_ not in self.nodes.keys():
            raise KeyError(f"node {node.id_} is not found")

        if out_edge:
            relationship_ids = list(self.node_relationships[node.id_]["out"].keys())
            relationships = func_call.lcall(
                relationship_ids, lambda i: self.relationships[i]
            )
            return relationships
        else:
            relationship_ids = list(self.node_relationships[node.id_]["in"].keys())
            relationships = func_call.lcall(
                relationship_ids, lambda i: self.relationships[i]
            )
            return relationships

    def get_predecessors(self, node: BaseNode):
        """
        Retrieves the predecessor nodes of a given node.

        Args:
            node (BaseNode): The node whose predecessors to retrieve.

        Returns:
            list: A list of predecessor nodes.
        """
        node_ids = list(self.node_relationships[node.id_]["in"].values())
        nodes = func_call.lcall(node_ids, lambda i: self.nodes[i])
        return nodes

    def get_successors(self, node: BaseNode):
        """
        Retrieves the successor nodes of a given node.

        Args:
            node (BaseNode): The node whose successors to retrieve.

        Returns:
            list: A list of successor nodes.
        """
        node_ids = list(self.node_relationships[node.id_]["out"].values())
        nodes = func_call.lcall(node_ids, lambda i: self.nodes[i])
        return nodes

    def remove_node(self, node: BaseNode) -> BaseNode:
        """
        Removes a node and its associated relationship from the graph.

        Args:
                node (BaseNode): The node to remove.

        Returns:
                BaseNode: The removed node.

        Raises:
                KeyError: If the node is not found in the graph.
        """
        if node.id_ not in self.nodes.keys():
            raise KeyError(f"node {node.id_} is not found")

        out_relationship = self.node_relationships[node.id_]["out"]
        for relationship_id, node_id in out_relationship.items():
            self.node_relationships[node_id]["in"].pop(relationship_id)
            self.relationships.pop(relationship_id)

        in_relationship = self.node_relationships[node.id_]["in"]
        for relationship_id, node_id in in_relationship.items():
            self.node_relationships[node_id]["out"].pop(relationship_id)
            self.relationships.pop(relationship_id)

        self.node_relationships.pop(node.id_)
        return self.nodes.pop(node.id_)

    def remove_relationship(self, relationship: Edge) -> Edge:
        """
        Removes a relationship from the graph.

        Args:
                relationship (Edge): The relationship to remove.

        Returns:
                Edge: The removed relationship.

        Raises:
                KeyError: If the relationship is not found in the graph.
        """
        if relationship.id_ not in self.relationships.keys():
            raise KeyError(f"relationship {relationship.id_} is not found")

        self.node_relationships[relationship.source_node_id]["out"].pop(
            relationship.id_
        )
        self.node_relationships[relationship.target_node_id]["in"].pop(relationship.id_)

        return self.relationships.pop(relationship.id_)

    def node_exist(self, node: BaseNode) -> bool:
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

    def relationship_exist(self, relationship: Edge) -> bool:
        """
        Checks if a relationship exists in the graph.

        Args:
                relationship (Edge): The relationship to check.

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

    def clear(self) -> None:
        """Clears the graph of all nodes and relationship."""
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
