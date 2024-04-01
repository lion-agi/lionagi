# TODO: finish implementing tree traversal methods

from lionagi.libs import convert

from ..schema import TreeNode
from .graph import Graph


class Tree(Graph):
    root: TreeNode | None = None

    def add_parent_to_child(self, child: str | TreeNode, parent: str | TreeNode):
        try:
            child = self.get_structure_node(child, add_new=True)
            parent = self.get_structure_node(parent, add_new=True)
            child.add_parent(parent)
        except Exception as e:
            raise ValueError(f"Error adding parent to node: {e}")

    def add_child_to_parent(self, parent: str | TreeNode, child: list | str | TreeNode):
        for i in convert.to_list(child):
            self._add_child_to_parent(parent, i)

    def find_parent(self, child: str | TreeNode) -> TreeNode | None:
        try:
            node: TreeNode = self.get_structure_node(child)
            return self.get_structure_node(node.parent)
        except Exception as e:
            raise ValueError(f"Error finding parent node: {e}")

    def find_children(self, node: str | TreeNode) -> list[TreeNode]:
        node: TreeNode = self.get_structure_node(node)
        if node.children is not None:
            return [self.get_structure_node(i) for i in node.children]

    def _add_child_to_parent(self, parent: str | TreeNode, child: str | TreeNode):
        try:
            parent = self.get_structure_node(parent, add_new=True)
            child = self.get_structure_node(child, add_new=True)
            parent.add_child(child)
        except Exception as e:
            raise ValueError(f"Error adding child to node: {e}")

    # TODO: Implement tree traversal methods
    # def traverse(self, node: TreeNode | str, search_type="depth") -> list[TreeNode]:
    #     node = self.get_node(node)
    #     if search_type == "depth":
    #         return self._depth_first_search(node)
    #     elif search_type == "breadth":
    #         return self._breadth_first_search(node)
    #     else:
    #         raise ValueError(f"Search type {search_type} not supported.")
