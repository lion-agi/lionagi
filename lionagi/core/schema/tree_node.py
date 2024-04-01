from enum import Enum
from lionagi.libs import convert, func_call
from .base_node import BaseNode
from .edge import Edge


class TREELABEL(str, Enum):
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

    _parent: BaseNode | None = None
    _children: list[str] = []

    @property
    def parent(self) -> BaseNode | None:
        """
        Get the parent node.

        Returns:
            BaseNode | None: The parent node.
        """
        return self._parent

    @property
    def children(self) -> list[str]:
        """
        Get the child nodes.

        Returns:
            list[str]: The list of child node IDs.
        """
        return self._children

    @parent.setter
    def parent(self, node: BaseNode):
        """
        Set the parent node.

        Args:
            node (BaseNode): The parent node to set.
        """
        relationship = self.get_edge(self.parent)
        self.pop_edge(relationship, self.parent)
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
            edge = Edge(
                source_node_id=parent.id_,
                target_node_id=self.id_,
                label=TREELABEL.CHILD,
            )
            parent.add_edge(self, edge, direction="out")

            edge = Edge(
                source_node_id=self.id_,
                target_node_id=parent.id_,
                label=TREELABEL.PARENT,
            )
            self.add_edge(parent, edge, direction="in")
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

            edge = Edge(
                source_node_id=self.id_,
                target_node_id=child_id,
                label=TREELABEL.PARENT,
            )
            self.parent.add_edge(child, edge, direction="out")

            edge = Edge(
                source_node_id=child_id,
                target_node_id=self.id_,
                label=TREELABEL.CHILD,
            )
            child.add_edge(self, edge, direction="in")

            self.children.append(child_id)
            return True

        except Exception:
            return False

    def remove_child(self, child: BaseNode, edge: Edge):
        """
        Remove a child node.

        Args:
            child (BaseNode): The child node to remove.
            relationship (Relationship): The edge between the child node and the parent node.

        Returns:
            Relationship: The removed edge.
        """
        self.children.remove(child.id_)
        return self.pop_edge(edge, child)

    def has_child(self, node: str | BaseNode) -> bool:
        """
        Check if a node is a child of the current node.

        Args:
            node (str | BaseNode): The node to check.

        Returns:
            bool: True if the node is a child of the current node, False otherwise.
        """
        relationship = self.get_edge(node)
        if node.id_ in self.out_relations and relationship.label == TREELABEL.PARENT:
            return True
        return False
