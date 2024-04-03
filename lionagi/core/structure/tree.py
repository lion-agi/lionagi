from pydantic import Field
from lionagi.core.schema import TreeNode
from lionagi.core.structure.graph import Graph

class Tree(Graph):
    root: TreeNode | None = Field(None, description="The root node of the tree.")
    
    def add_parent_to_child(self, child: TreeNode | str | list, parent: TreeNode | str, old_parent: TreeNode | None | str = None):
        children = [child] if isinstance(child, (TreeNode, str)) else child
        parent_node = self.get_structure_node(parent)

        if parent_node is None:
            raise ValueError("Parent node not found")

        for child_id_or_node in children:
            child_node = self.get_structure_node(child_id_or_node)
            if child_node is None:
                raise ValueError("Child node not found")

            if old_parent:
                old_parent_node = self.get_structure_node(old_parent)
                if old_parent_node and child_node in old_parent_node.children:
                    old_parent_node.children.remove(child_node)

                if self.root is None or self.root == old_parent_node:
                    self.root = parent_node

            parent_node.children.append(child_node)
            child_node.parent = parent_node

    def add_child_to_parent(self, child: TreeNode | str | list, parent: TreeNode | str, old_parent: TreeNode | None | str = None):
        # This method is essentially the same logic as add_parent_to_child
        # In a tree structure, the logic for adding a child to a parent and adding a parent to a child is symmetrical.
        self.add_parent_to_child(child, parent, old_parent)

    def find_parent(self, child: TreeNode | str) -> TreeNode | None:
        child_node = self.get_structure_node(child)
        if child_node is None:
            raise ValueError("Child node not found")
        return child_node.parent

    def find_child(self, parent: TreeNode | str) -> list[TreeNode | None]:
        parent_node = self.get_structure_node(parent)
        if parent_node is None:
            raise ValueError("Parent node not found")
        return parent_node.children
    