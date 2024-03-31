from pydantic import Field
from lionagi.libs import convert

from ..schema import TreeNode
from .graph import Graph


class Tree(Graph):
    root: TreeNode

    def _add_child_to_node(self, parent: str | TreeNode, child: str | TreeNode):
        try:
            parent = self.get_node(parent, add_new=True)
            child = self.get_node(child, add_new=True)
            parent.add_child(child)
            child.set_parent(parent)
        except Exception as e:
            raise ValueError(f"Error adding child to node: {e}")

    def add_child_to_node(self, parent: str | TreeNode, child: list | str | TreeNode):
        for i in convert.to_list(child):
            self._add_child_to_node(parent, i)

    def find_parent(self, node: str | TreeNode) -> TreeNode | None:
        node = self.get_node(node)
        if node.parent_exist:
            return self.get_node(node.parent)
        return None

    def find_children(self, node: str | TreeNode) -> list[TreeNode]:
        node = self.get_node(node)
        if node.children is not None:
            return [self.get_node(i) for i in node.children]
