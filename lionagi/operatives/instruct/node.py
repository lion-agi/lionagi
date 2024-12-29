from lionagi.protocols.generic.node import Node

from .instruct import INSTRUCT_FIELD, Instruct

__all__ = ("InstructNode",)


class InstructNode(Node):
    instruct: Instruct | None = INSTRUCT_FIELD.field_info
