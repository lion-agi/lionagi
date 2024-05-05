"""
This module provides classes for representing and working with tree structures.

The module includes the following classes:
- TreeLabel: An enumeration representing tree relationships (parent and child).
- TreeNode: A specialized node representing a node within a tree structure,
  extending the basic node functionality with parent-child relationships.
- Tree: Represents a tree structure, extending the graph with tree-specific
  functionalities like managing parent-child relationships.
"""

from enum import Enum
from pydantic import Field

from ._graph import Graph
from ..abc import Condition
from .._node._tree_node import TreeNode
from .._util import _to_list_type


class TreeLabel(str, Enum):
    """
    Enumeration representing tree relationships.

    Attributes:
        PARENT (str): Represents the parent edge.
        CHILD (str): Represents the child edge.
    """

    PARENT = "parent"
    CHILD = "child"


class Tree(Graph):
    """
    Represents a tree structure, extending the graph with tree-specific
    functionalities.

    Manages parent-child relationships within the tree.

    Attributes:
        root (TreeNode | None): The root node of the tree. Defaults to None.
    """

    root: TreeNode | None = Field(
        default=None, description="The root node of the tree graph."
    )

    def relate_parent_child(
        self,
        parent: TreeNode,
        children: list[TreeNode],
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """
        Establishes parent-child relationships between the given parent node and
        child node(s).

        Args:
            parent (TreeNode): The parent node.
            children (list[TreeNode]): A list of child nodes.
            condition (Condition | None): The condition associated with the
                relationships, if any.
            bundle (bool): Indicates whether to bundle the relations into a
                single transaction. Defaults to False.
        """

        for i in _to_list_type(children):

            self.add_edge(
                parent, i, condition=condition, bundle=bundle, label=TreeLabel.PARENT
            )

        if self.root is None:
            self.root = parent
