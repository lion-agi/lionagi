# from lionagi.libs import convert
# from functools import singledispatchmethod
# from typing import Any
# from pydantic import Field

# from lionagi.core.schema import BaseNode


# class BaseRelatableNode(BaseNode):

#     label: str | None = None
#     relations: dict[str, str | Any | None] = Field(default={})
#     default_label: str | Any | None = None

#     @property
#     def has_relations(self) -> bool:
#         return True if len(self.relations)>0 else False


#     @singledispatchmethod
#     def add_relation(self, node: Any, label=None) -> None:
#         raise NotImplementedError


#     @add_relation.register(BaseNode)
#     def _(self, node: BaseNode, label=None) -> None:
#         self.relations[node.id_] = label or self.default_label


#     @add_relation.register(str)
#     def _(self, node: str, label=None) -> None:
#         self.relations[node] = label or self.default_label


#     @add_relation.register(list)
#     def _(self, node: list[BaseNode | str], label=None) -> None:
#         for _node in convert.to_list(node):
#             self.add_relation(_node, label=label)


#     @add_relation.register(dict)
#     def _(self, node: dict[str, str], label=None) -> None:
#         for _node, _label in node.items():
#             self.add_relation(_node, label=label or _label)

#     @singledispatchmethod
#     def pop_relation(self, node: Any, default=None) -> None:
#         raise NotImplementedError

#     @pop_relation.register(BaseNode)
#     def _(self, node: BaseNode, default=None) -> None:
#         return self.relations.pop(node.id_, default)

#     @pop_relation.register(str)
#     def _(self, node: str, default=None) -> None:
#         return self.relations.pop(node, default)

#     @pop_relation.register(list)
#     def _(self, node: list[str | BaseNode], default=None) -> None:
#         outs = []
#         for _node in convert.to_list(node):
#             outs.append(self.pop_relation(_node))
#         return outs if any(outs) else default
