from lion_core.communication import Instruction as CoreInstruction

from ..node import Node


class Instruction(CoreInstruction, Node):

    def xx(self, *args, **kwargs):
        out = super().xx(*args, **kwargs)
        out.process()
        return out

        ...

    pass


__all__ = ["Instruction"]
