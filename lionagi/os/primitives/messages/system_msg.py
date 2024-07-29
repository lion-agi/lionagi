from lion_core.communication import System as CoreSystem

from ..node import Node


class System(CoreSystem, Node):
    pass


__all__ = ["System"]
