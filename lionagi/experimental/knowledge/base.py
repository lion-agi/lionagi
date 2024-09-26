from ..collections import Pile, pile
from ..collections.abc import Component, Field
from ..generic import Node


class Knowledge(Component):

    knowledge_base: Pile[Node] = Field(
        default_factory=pile,
    )
