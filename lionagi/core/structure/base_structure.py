from functools import singledispatchmethod

from typing import Any
from pydantic import Field, AliasChoices

from lionagi.libs import convert, func_call
from lionagi.core.schema import BaseNode, Edge, Condition


class BaseStructure(BaseNode):
    """
    A base class representing a structure of nodes.

    Attributes:
        nodes (dict[str, BaseNode]): A dictionary of nodes in the structure, where the keys are node IDs.
    """

    structure_edges: dict[str, Edge] = Field(
        default_factory=dict,
        alias=AliasChoices("internal_edges", "structure_relationships", "internal_relationships"),
        description="a dictionary of all relationships in the graph, key is the edge id",
    )

    structure_nodes: dict[str, BaseNode] = Field(
        default_factory=dict,
        alias=AliasChoices("nodes", "graph_nodes", "tree_nodes"),
        description="a dictionary of all nodes in the graph, key is the node id",
    )


    @property
    def node_id_list(self):
        return list(self.structure_nodes.keys())
    
    @property
    def edge_id_list(self):
        return list(self.structure_edges.keys())
    
    @property
    def node_list(self):
        return list(self.structure_nodes.values())
    
    @property
    def edge_list(self):
        return list(self.structure_edges.values())


    def get_node_predecessors(self, node: BaseNode):
        """
        Get the predecessor nodes of a node.

        Args:
            node (BaseNode): The node to get predecessors for.

        Returns:
            List[BaseNode]: A list of predecessor nodes.
        """

        return self.get_structure_node(node.predecessors)

    def get_node_successors(self, node: BaseNode):
        """
        Get the successor nodes of a node.

        Args:
            node (BaseNode): The node to get successors for.

        Returns:
            List[BaseNode]: A list of successor nodes.
        """
        return self.get_structure_node(node.successors)

    @property
    def node_edges(self):
        _edges = {}
        for _node in self.structure_nodes.values():
            _edges[_node.id_] = {
                "in": _node.in_relations,
                "out": _node.out_relations,
            }
        return _edges

    def _get_node_edges(
        self, node: BaseNode | str = None, direction="out"
    ) -> list[Edge]:
        node = self.get_structure_node(node)

        if node is None:
            return list(self.structure_edges.values())

        if node.id_ not in self.structure_nodes:
            raise KeyError(f"node {node.id_} is not found")

        if direction == "out":
            return node.out_edges

        if direction == "in":
            return node.in_edges

        if direction == "all":
            return node.edges

    def get_node_edges(self, node: BaseNode, direction="out", labels=None):
        edges = self._get_node_edges(node, direction)
        if labels:
            if not isinstance(labels, list):
                labels = [labels]
            result = []
            for e in edges:
                if e.label in labels:
                    result.append(e)
            edges = result
        return edges


    def has_structure_edge(self, edge: Edge | str) -> bool:
        k = edge if isinstance(edge, str) else edge.id_
        return k in self.structure_edges

    def get_structure_edge(self, edge: Edge | str) -> bool:
        k = edge if isinstance(edge, str) else edge.id_
        return self.structure_edges.get(k, None)

    def add_structure_edge(self, edge: Edge) -> None:
        try:
            in_node: BaseNode = self.get_structure_node(edge.source_node_id)
            out_node: BaseNode = self.get_structure_node(edge.target_node_id)

            if self.has_structure_node([in_node.id_, out_node.id_]):
                in_node.add_edge(out_node, edge, direction="out")
                out_node.add_edge(in_node, edge, direction="in")

            self.structure_edges[edge.id_] = edge
        except Exception as e:
            raise ValueError(f"Error adding edge: {e}")

    def remove_structure_edge(self, edge: Edge | str) -> None:
        if isinstance(edge, str):
            edge = self.structure_edges.get(edge, None)

        source_node: BaseNode = self.get_structure_node(edge.source_node_id)
        target_node: BaseNode = self.get_structure_node(edge.target_node_id)

        source_node.pop_edge(node=target_node)
        self.structure_edges.pop(edge.id_)
        return edge

    def remove_structure_node(self, node: BaseNode | str) -> None:
        try:
            for i in node.edges:
                j = self.get_structure_edge(i)
                self.remove_structure_edge(j)

            self.pop_structure_node(node)
            return True
        except Exception as e:
            raise ValueError(f"Error removing node: {e}")

    @singledispatchmethod
    def add_structure_node(self, node: Any) -> None:
        """
        Add a node to the structure.

        Args:
            node (Any): The node to add. Can be a BaseNode instance, a list of BaseNode instances, or a dictionary of BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @add_structure_node.register(BaseNode)
    def _(self, node: BaseNode) -> None:
        """
        Add a BaseNode instance to the structure.

        Args:
            node (BaseNode): The BaseNode instance to add.
        """
        if node.id_ not in self.structure_nodes:
            self.structure_nodes[node.id_] = node

    @add_structure_node.register(list)
    def _(self, node: list[BaseNode]) -> None:
        """
        Add a list of BaseNode instances to the structure.

        Args:
            node (list[BaseNode]): The list of BaseNode instances to add.
        """
        for _node in node:
            self.add_structure_node(_node)

    @add_structure_node.register(dict)
    def _(self, node: dict[str, BaseNode]) -> None:
        """
        Add a dictionary of BaseNode instances to the structure.

        Args:
            node (dict[str, BaseNode]): The dictionary of BaseNode instances to add, where the keys are node IDs.
        """
        for _node in node.values():
            self.add_structure_node(_node)

    @singledispatchmethod
    def get_structure_node(self, node: Any, **kwargs):
        """
        Get a node from the structure.

        Args:
            node (Any): The node to get. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        return node

    @get_structure_node.register(str)
    def _(self, node: str, **kwargs):
        """
        Get a node from the structure by its ID.

        Args:
            node (str): The ID of the node to get.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseNode | None: The node with the given ID, or None if it doesn't exist.
        """
        return self.structure_nodes.get(node, None)

    @get_structure_node.register(BaseNode)
    def _(self, node: BaseNode, **kwargs):
        """
        Get a BaseNode instance from the structure.

        Args:
            node (BaseNode): The BaseNode instance to get.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseNode | None: The BaseNode instance, or None if it doesn't exist.
        """
        return node if node.id_ in self.structure_nodes else None


    @get_structure_node.register(list)
    def _(
        self,
        node: list[str | BaseNode],
        dropna=True,
        flatten=True,
        **kwargs,
    ):
        """
        Get a list of nodes from the structure.

        Args:
            node (list[str | BaseNode]): The list of node IDs or BaseNode instances to get.
            add_new (bool, optional): Whether to add the nodes to the structure if they don't exist. Defaults to False.
            dropna (bool, optional): Whether to drop missing nodes from the result. Defaults to True.
            flatten (bool, optional): Whether to flatten the result list. Defaults to True.
            **kwargs: Additional keyword arguments.

        Returns:
            list[BaseNode]: The list of nodes.
        """
        nodes = convert.to_list(node)
        return func_call.lcall(
            nodes,
            lambda x: self.get_structure_node(x),
            dropna=dropna,
            flatten=flatten,
        )

    @singledispatchmethod
    def pop_structure_node(self, node: Any) -> None:
        """
        Remove a node from the structure.

        Args:
            node (Any): The node to remove. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @pop_structure_node.register(str)
    def _(self, node: str) -> None:
        """
        Remove a node from the structure by its ID.

        Args:
            node (str): The ID of the node to remove.

        Raises:
            KeyError: If the node is not found in the structure.
        """
        if node in self.structure_nodes:
            return self.structure_nodes.pop(node)
        raise KeyError(f"Node {node} not found in structure.")

    @pop_structure_node.register(BaseNode)
    def _(self, node: BaseNode) -> None:
        """
        Remove a BaseNode instance from the structure.

        Args:
            node (BaseNode): The BaseNode instance to remove.

        Raises:
            KeyError: If the node is not found in the structure.
        """
        if node.id_ in self.structure_nodes:
            return self.structure_nodes.pop(node.id_)
        raise KeyError(f"Node {node.id_} not found in structure.")

    @pop_structure_node.register(list)
    def _(self, node: list[str | BaseNode]) -> None:
        """
        Remove a list of nodes from the structure.

        Args:
            node (list[str | BaseNode]): The list of node IDs or BaseNode instances to remove.

        Raises:
            Exception: If an error occurs during the removal process.
        """
        try:
            nodes = convert.to_list(node)
            _nodes = []
            for _node in nodes:
                _nodes.append(self.pop_structure_node(_node))
            return _nodes
        except Exception as e:
            raise e

    @singledispatchmethod
    def has_structure_node(self, node: Any) -> bool:
        """
        Check if a node exists in the structure.

        Args:
            node (Any): The node to check. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @has_structure_node.register(str)
    def _(self, node: str) -> bool:
        """
        Check if a node exists in the structure by its ID.

        Args:
            node (str): The ID of the node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return node in self.structure_nodes

    @has_structure_node.register(BaseNode)
    def _(self, node: BaseNode) -> bool:
        """
        Check if a BaseNode instance exists in the structure.

        Args:
            node (BaseNode): The BaseNode instance to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return node.id_ in self.structure_nodes

    @has_structure_node.register(list)
    def _(self, node: list[str | BaseNode]) -> bool:
        """
        Check if all nodes in a list exist in the structure.

        Args:
            node (list[str | BaseNode]): The list of node IDs or BaseNode instances to check.

        Returns:
            bool: True if all nodes exist, False otherwise.
        """
        nodes = convert.to_list(node)
        return all([self.has_structure_node(n) for n in nodes])

    @property
    def is_empty(self) -> bool:
        """
        Check if the structure is empty.

        Returns:
            bool: True if the structure is empty, False otherwise.
        """
        return len(self.structure_nodes) == 0

    def clear(self) -> None:
        """
        Clear all nodes from the structure.
        """
        self.structure_nodes.clear()
        self.structure_edges.clear()

    @staticmethod
    def _build_edge(from_node: BaseNode, to_node: BaseNode, condition: Condition | None=None, **kwargs):
        edge = Edge(source_node_id=from_node.id_, target_node_id=to_node.id_, **kwargs)
        if condition:
            edge.add_condition(condition)
        return edge
    