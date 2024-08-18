from lion_core.generic.node import Node as CoreNode


class Node(CoreNode):

    @classmethod
    def from_obj(cls, *args, **kwargs): ...


__all__ = ["Node"]
