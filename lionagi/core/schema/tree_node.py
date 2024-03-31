from typing import Any
from lionagi.libs import convert
from .base_node import BaseNode


class TreeNode(BaseNode):
    parent: str | None = None

    def __init__(self, parent_id, children_ids: list[str] = [], **kwargs):
        super().__init__(**kwargs)
        self.parent = parent_id
        node_ids = convert.to_list([parent_id, children_ids])
        for i in node_ids:
            self.add_related_node(i)

    @property
    def children(self):
        outs = []
        for i in self.related_nodes:
            if self.parent and i != self.parent:
                outs.append(i)
        return outs if len(outs) > 0 else None

    @children.setter
    def children(self, nodes: list[str | BaseNode]):
        node_ids = []
        for i in convert.to_list(nodes):
            if isinstance(i, BaseNode):
                node_ids.append(i.id_)
            elif isinstance(i, str):
                node_ids.append(i)

        self.related_nodes = [i for i in node_ids if i != self.parent]

    @property
    def parent_exist(self) -> bool:
        return self.parent is not None

    def child_exist(self, node: str | BaseNode) -> bool:
        k = node.id_ if isinstance(node, TreeNode) else node
        return k in self.children

    def add_child(self, node: str | BaseNode) -> bool:
        k = node.id_ if isinstance(node, TreeNode) else node
        if k != self.parent and not self.child_exist(node):
            return self.add_related_node(k)
        return False

    def remove_child(self, node: str | BaseNode) -> bool:
        k = node.id_ if isinstance(node, TreeNode) else node
        if k != self.parent and self.child_exist(node):
            return self.remove_related_node(k)
        return False

    def set_parent(self, node: str | BaseNode) -> bool:
        try:
            k = node.id_ if isinstance(node, TreeNode) else node
            if k not in self.related_nodes:
                self.add_related_node(k)
            self.parent = k
            return True
        except Exception:
            return False
