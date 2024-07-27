from lion_core.abc import Relational
from lion_core.generic.component import Component


class Node(Component, Relational):
    pass


__all__ = ["Node"]
