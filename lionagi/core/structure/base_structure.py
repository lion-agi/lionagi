from functools import singledispatchmethod
from typing import Any
from lionagi.libs import convert, func_call
from lionagi.integrations.bridge.pydantic_.pydantic_bridge import Field

from pydantic import Field

from lionagi.core.schema import BaseNode


class BaseStructure(BaseNode):
    nodes: dict[str, BaseNode] = Field(default_factory=dict)

    @singledispatchmethod
    def add_node(self, node: Any) -> None:
        raise NotImplementedError

    @add_node.register(BaseNode)
    def _(self, node: BaseNode) -> None:
        self.nodes[node.id_] = node

    @add_node.register(list)
    def _(self, node: list[BaseNode]) -> None:
        for _node in node:
            self.add_node(_node)

    @add_node.register(dict)
    def _(self, node: dict[str, BaseNode]) -> None:
        for _node in node.values():
            self.add_node(_node)

    @singledispatchmethod
    def get_node(self, node: Any, add_new=False):
        raise NotImplementedError

    @get_node.register(str)
    def _(self, node: str, add_new=False, **kwargs):
        return self.nodes.get(node, None)

    @get_node.register(BaseNode)
    def _(self, node: BaseNode, add_new=False, **kwargs):
        if not add_new:
            return self.nodes.get(node.id_, None)
        if node.id_ not in self.nodes:
            self.add_node(node)
        return node

    @get_node.register(list)
    def _(
        self,
        node: list[str | BaseNode],
        add_new=False,
        dropna=True,
        flatten=True,
        **kwargs,
    ):
        nodes = convert.to_list(node)
        return func_call.lcall(
            nodes,
            lambda x: self.get_node(x, add_new=add_new),
            dropna=dropna,
            flatten=flatten,
        )

    @singledispatchmethod
    def has_node(self, node: Any) -> bool:
        raise NotImplementedError

    @has_node.register(str)
    def _(self, node: str) -> bool:
        return node in self.nodes

    @has_node.register(BaseNode)
    def _(self, node: BaseNode) -> bool:
        return node.id_ in self.nodes

    @has_node.register(list)
    def _(self, node: list[str | BaseNode]) -> bool:
        nodes = convert.to_list(node)
        return all([self.has_node(n) for n in nodes])

    @property
    def is_empty(self) -> bool:
        return False if len(self.nodes) > 0 else True

    def clear(self) -> None:
        self.nodes.clear()
