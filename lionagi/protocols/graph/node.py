from abc import ABC

from ..generic.element import Element

__all__ = (
    "Relational",
    "Node",
)


class Relational(ABC):
    """Base class for all relational elements."""

    pass


class Node(Element, Relational):
    """Base class for all nodes."""

    pass
