from ..collections.abc import Component, Field
from ..collections import Pile, pile
from ..generic import Node


class Knowledge(Component):

    knowledge_base: Pile[Node] = Field(
        default_factory=pile,
    )
