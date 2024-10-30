from enum import Enum

from pydantic import Field

from lionagi.core.collections.abc import Condition
from lionagi.core.collections.util import to_list_type
from lionagi.core.generic.node import Node


class TreeLabel(str, Enum):
    """Enumeration representing tree relationships."""

    PARENT = "parent"
    CHILD = "child"


class TreeNode(Node):
    """Represents a node in a tree structure."""

    parent: Node | None = Field(
        default=None,
        description="The parent node, as an instance of Node.",
    )

    @property
    def children(self) -> list[str]:
        """Return a list of child node ids."""
        if not self.parent:
            return list(self.related_nodes)
        else:
            return [
                node
                for node in self.related_nodes
                if node != self.parent.ln_id
            ]

    def relate_child(
        self,
        node: Node | list[Node],
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """Establish a parent-child relationship with the given node(s)."""
        children = to_list_type(node)
        for _child in children:
            self.relate(
                _child,
                direction="out",
                # label=TreeLabel.PARENT,
                condition=condition,
                bundle=bundle,
            )
            if isinstance(_child, TreeNode):
                _child.parent = self

    def relate_parent(
        self,
        node: Node,
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """Establish a parent-child relationship with the given parent node."""
        if self.parent:
            self.unrelate(self.parent)
        self.relate(
            node,
            direction="in",
            # label=TreeLabel.PARENT,
            condition=condition,
            bundle=bundle,
        )
        self.parent = node

    def unrelate_parent(self):
        """Remove the parent-child relationship with the parent node."""
        self.unrelate(self.parent)
        self.parent = None

    def unrelate_child(self, child: Node | list[Node]):
        """Remove the parent-child relationship with the given child node(s)."""
        children: list[Node] = [child] if isinstance(child, Node) else child
        for _child in children:
            self.unrelate(_child)
            if isinstance(_child, TreeNode):
                _child.parent = None
