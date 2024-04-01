from enum import Enum
from pydantic import Field
from lionagi.libs import convert, func_call
from lionagi.core.schema.base_node import BaseNode
from lionagi.core.schema.edge import Edge


class TREE_LABEL(str, Enum):
    """
    Enumeration representing tree relationships.

    Attributes:
        PARENT (str): Represents the parent edge.
        CHILD (str): Represents the child edge.
    """

    PARENT = "parent"
    CHILD = "child"


class TreeNode(BaseNode):
    """
    A node in a tree structure.

    Attributes:
        parent (BaseNode): The parent node.
        children (list[str]): The list of child node IDs.
    """

    parent: BaseNode | None = Field(None, description="The parent node", alias="_parent")
    children: list[str] = Field(default_factory=list, description="The list of child node IDs.", alias="_children")

    def add_parent(self, parent: BaseNode):
        self._add_parent(parent)

    def remove_parent(self, parent: BaseNode):
        self._remove_parent(parent)

    def change_parent(self, old_parent: BaseNode, new_parent: BaseNode):
        self._remove_parent(old_parent)
        self._add_parent(new_parent)

    def add_child(self, child: BaseNode | list[BaseNode]):
        children = [child] if isinstance(child, BaseNode) else child
        for _child in children:
            self._add_child(_child)

    def remove_child(self, child: BaseNode | list[BaseNode]):
        children = [child] if isinstance(child, BaseNode) else child
        for _child in children:
            self._remove_child(_child)

    def has_child(self, child: BaseNode) -> bool:
        return self._has_child(child)

    def _has_child(self, child: BaseNode) -> bool:
        relationship = self.get_edge(child)
        if child.id_ in self.out_relations and relationship and relationship.label == TREE_LABEL.PARENT:
            return True
        return False

    def _add_parent(self, parent: BaseNode):
        self.add_edge(parent, label=TREE_LABEL.CHILD)
        self.parent = parent

    def _add_child(self, child: BaseNode):
        self.add_edge(child, label=TREE_LABEL.PARENT)
        self.children.append(child.id_)

    def _remove_parent(self, parent: BaseNode):
        self.pop_edge(parent)
        self.parent = None

    def _remove_child(self, child: BaseNode):
        self.pop_edge(child)
        self.children.remove(child.id_)


