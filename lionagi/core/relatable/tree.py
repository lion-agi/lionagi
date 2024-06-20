"""This module provides tree structure."""

from pydantic import Field
from ..abc import Condition
from ..util import to_list_type
from .tree_node import TreeNode
from .graph import Graph


class Tree(Graph):
    """
    Represents a tree structure, extending the graph with tree-specific functionalities.

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
        children,
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """
        Establishes parent-child relationships between the given parent and child node(s).

        Args:
            parent (TreeNode): The parent node.
            children (list[TreeNode]): A list of child nodes.
            condition (Condition | None): The condition associated with the relationships, if any.
            bundle (bool): Indicates whether to bundle the relations into a single
                           transaction. Defaults to False.
        """

        for i in to_list_type(children):
            i.relate_parent(parent, condition=condition, bundle=bundle)

        if self.root is None:
            self.root = parent

        self.add_node([parent, *children])
