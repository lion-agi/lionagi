from pydantic import Field
from ..abc import Ordering, Component
from .._pile._categorical_pile import CategoricalPile


class HyperRelation(Component, Ordering): ...
