from functools import singledispatchmethod
from typing import Any
from lionagi.libs import convert, func_call
from lionagi.integrations.bridge.pydantic_.pydantic_bridge import Field

from pydantic import Field

from lionagi.core.schema import BaseNode


class BaseStructure(BaseNode):
    """
    A base class representing a structure of nodes.

    Attributes:
        nodes (dict[str, BaseNode]): A dictionary of nodes in the structure, where the keys are node IDs.
    """

    nodes: dict[str, BaseNode] = Field(default_factory=dict)

    @singledispatchmethod
    def add_node(self, node: Any) -> None:
        """
        Add a node to the structure.

        Args:
            node (Any): The node to add. Can be a BaseNode instance, a list of BaseNode instances, or a dictionary of BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @add_node.register(BaseNode)
    def _(self, node: BaseNode) -> None:
        """
        Add a BaseNode instance to the structure.

        Args:
            node (BaseNode): The BaseNode instance to add.
        """

        self.nodes[node.id_] = node

    @add_node.register(list)
    def _(self, node: list[BaseNode]) -> None:
        """
        Add a list of BaseNode instances to the structure.

        Args:
            node (list[BaseNode]): The list of BaseNode instances to add.
        """
        for _node in node:
            self.add_node(_node)

    @add_node.register(dict)
    def _(self, node: dict[str, BaseNode]) -> None:
        """
        Add a dictionary of BaseNode instances to the structure.

        Args:
            node (dict[str, BaseNode]): The dictionary of BaseNode instances to add, where the keys are node IDs.
        """
        for _node in node.values():
            self.add_node(_node)

    @singledispatchmethod
    def get_node(self, node: Any, add_new=False):
        """
        Get a node from the structure.

        Args:
            node (Any): The node to get. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.

        Raises:
            NotImplementedError: If the node type is not supported.
        """

        raise NotImplementedError

    @get_node.register(str)
    def _(self, node: str, add_new=False, **kwargs):
        """
        Get a node from the structure by its ID.

        Args:
            node (str): The ID of the node to get.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseNode | None: The node with the given ID, or None if it doesn't exist.
        """
        return self.nodes.get(node, None)

    @get_node.register(BaseNode)
    def _(self, node: BaseNode, add_new=False, **kwargs):
        """
        Get a BaseNode instance from the structure.

        Args:
            node (BaseNode): The BaseNode instance to get.
            add_new (bool, optional): Whether to add the node to the structure if it doesn't exist. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            BaseNode | None: The BaseNode instance, or None if it doesn't exist.
        """
        if not add_new:
            return self.nodes.get(node.id_, None)
        if node.id_ not in self.nodes:
            self.add_node(node)
        return node

    @get_node.register(list)
    def _(
        self,
        node: list[str | BaseNode],
        add_new=False,
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
            lambda x: self.get_node(x, add_new=add_new),
            dropna=dropna,
            flatten=flatten,
        )

    @singledispatchmethod
    def pop_node(self, node: Any) -> None:
        """
        Remove a node from the structure.

        Args:
            node (Any): The node to remove. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @pop_node.register(str)
    def _(self, node: str) -> None:
        """
        Remove a node from the structure by its ID.

        Args:
            node (str): The ID of the node to remove.

        Raises:
            KeyError: If the node is not found in the structure.
        """
        if node in self.nodes:
            return self.nodes.pop(node)
        raise KeyError(f"Node {node} not found in structure.")

    @pop_node.register(BaseNode)
    def _(self, node: BaseNode) -> None:
        """
        Remove a BaseNode instance from the structure.

        Args:
            node (BaseNode): The BaseNode instance to remove.

        Raises:
            KeyError: If the node is not found in the structure.
        """
        if node.id_ in self.nodes:
            return self.nodes.pop(node.id_)
        raise KeyError(f"Node {node.id_} not found in structure.")

    @pop_node.register(list)
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
                _nodes.append(self.pop_node(_node))
            return _nodes
        except Exception as e:
            raise e

    @singledispatchmethod
    def has_node(self, node: Any) -> bool:
        """
        Check if a node exists in the structure.

        Args:
            node (Any): The node to check. Can be a node ID (str), a BaseNode instance, or a list of node IDs or BaseNode instances.

        Raises:
            NotImplementedError: If the node type is not supported.
        """
        raise NotImplementedError

    @has_node.register(str)
    def _(self, node: str) -> bool:
        """
        Check if a node exists in the structure by its ID.

        Args:
            node (str): The ID of the node to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return node in self.nodes

    @has_node.register(BaseNode)
    def _(self, node: BaseNode) -> bool:
        """
        Check if a BaseNode instance exists in the structure.

        Args:
            node (BaseNode): The BaseNode instance to check.

        Returns:
            bool: True if the node exists, False otherwise.
        """
        return node.id_ in self.nodes

    @has_node.register(list)
    def _(self, node: list[str | BaseNode]) -> bool:
        """
        Check if all nodes in a list exist in the structure.

        Args:
            node (list[str | BaseNode]): The list of node IDs or BaseNode instances to check.

        Returns:
            bool: True if all nodes exist, False otherwise.
        """
        nodes = convert.to_list(node)
        return all([self.has_node(n) for n in nodes])

    @property
    def is_empty(self) -> bool:
        """
        Check if the structure is empty.

        Returns:
            bool: True if the structure is empty, False otherwise.
        """
        return len(self.nodes) == 0

    def clear(self) -> None:
        """
        Clear all nodes from the structure.
        """
        self.nodes.clear()
