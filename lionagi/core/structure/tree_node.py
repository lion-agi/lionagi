from enum import Enum
from lionagi.libs import convert, func_call
from ..schema.base_node import BaseNode
from ..relations import Relationship


class TreeRelation(Enum | str):
    """
    Enumeration representing tree relationships.

    Attributes:
        PARENT (str): Represents the parent relationship.
        CHILD (str): Represents the child relationship.
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

    parent: BaseNode
    children: list[str] = []

    @parent.setter
    def parent(self, node: BaseNode):
        """
        Set the parent node.

        Args:
            node (BaseNode): The parent node to set.
        """
        relationship = self.get_relation(self.parent)
        self.pop_relation(relationship, self.parent)
        self.add_parent(node)
        self.parent = node

    @children.setter
    def children(self, node: BaseNode | list[BaseNode]):
        """
        Set the child nodes.

        Args:
            node (BaseNode | list[BaseNode]): The child node(s) to set.
        """
        func_call.lcall(self.children, self.remove_child)
        func_call.lcall(convert.to_list(node), self.add_child)
        self.children = [i.id_ for i in convert.to_list(node)]

    def add_parent(self, parent: BaseNode):
        """
        Add a parent node.

        Args:
            parent (BaseNode): The parent node to add.

        Returns:
            bool: True if the parent node is added successfully, False otherwise.
        """
        try:
            relationship = Relationship(
                source_node_id=parent.id_,
                target_node_id=self.id_,
                label=TreeRelation.CHILD,
            )
            parent.add_relation(self, relationship, direction="out")

            relationship = Relationship(
                source_node_id=self.id_,
                target_node_id=parent.id_,
                label=TreeRelation.PARENT,
            )
            self.add_relation(parent, relationship, direction="in")
            return True

        except Exception:
            return False

    def add_child(self, child: BaseNode):
        """
        Add a child node.

        Args:
            child (BaseNode): The child node to add.

        Returns:
            bool: True if the child node is added successfully, False otherwise.
        """
        try:
            child_id = child.id_ if isinstance(child, BaseNode) else child

            relationship = Relationship(
                source_node_id=self.id_,
                target_node_id=child_id,
                label=TreeRelation.PARENT,
            )
            self.parent.add_relation(child, relationship, direction="out")

            relationship = Relationship(
                source_node_id=child_id,
                target_node_id=self.id_,
                label=TreeRelation.CHILD,
            )
            child.add_relation(self, relationship, direction="in")

            self.children.append(child_id)
            return True

        except Exception:
            return False

    def remove_child(self, child: BaseNode, relationship: Relationship):
        """
        Remove a child node.

        Args:
            child (BaseNode): The child node to remove.
            relationship (Relationship): The relationship between the child node and the parent node.

        Returns:
            Relationship: The removed relationship.
        """
        self.children.remove(child.id_)
        return self.pop_relation(relationship, child)

    def has_child(self, node: str | BaseNode) -> bool:
        """
        Check if a node is a child of the current node.

        Args:
            node (str | BaseNode): The node to check.

        Returns:
            bool: True if the node is a child of the current node, False otherwise.
        """
        relationship = self.get_relation(node)
        if node.id_ in self.out_relations and relationship.label == TreeRelation.PARENT:
            return True
        return False
