from enum import Enum
from pydantic import Field

from ..abc import Condition
from .._node._node import Node
from .._util import _to_list_type


class TreeLabel(str, Enum):

    PARENT = "parent"
    CHILD = "child"


class TreeNode(Node):

    parent: Node | None = Field(
        default=None,
        description="The parent node, as an instance of Node.",
    )

    @property
    def children(self) -> list[str]:

        if not self.parent:
            return list(self.related_nodes)
        else:
            return [node for node in self.related_nodes if node != self.parent.ln_id]

    def relate_child(
        self,
        node: Node | list[Node],
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:

        children = _to_list_type(node)
        for _child in children:
            self.relate(
                _child,
                direction="out",
                label=TreeLabel.PARENT,
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
        if self.parent:
            self.unrelate(self.parent)
        self.relate(
            node,
            direction="in",
            label=TreeLabel.PARENT,
            condition=condition,
            bundle=bundle,
        )
        self.parent = node

    def unrelate_parent(self):
        self.unrelate(self.parent)
        self.parent = None

    def unrelate_child(self, child: Node | list[Node]):
        children: list[Node] = [child] if isinstance(child, Node) else child
        for _child in children:
            self.unrelate(_child)
            if isinstance(_child, TreeNode):
                _child.parent = None
