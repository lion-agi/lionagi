from pydantic import Field

from ..node import Node
from .graph import Graph


class Tree(Graph):

    root: Node | None = Field(
        default=None, description="The root node of the tree graph."
    )


__all__ = ["Tree"]
