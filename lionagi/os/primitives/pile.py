from typing import Any, ClassVar, Type
from lion_core.generic.pile import Pile as CorePile

from lionagi.os.primitives.node import Node
from ._pile_loader import PileLoaderRegistry, PileLoader


class Pile(CorePile):
    """async-compatible, ordered collection of Observable elements."""

    _loader_registry: ClassVar = PileLoaderRegistry

    @classmethod
    def get_loader_registry(cls) -> PileLoaderRegistry:
        """Get the converter registry for the class."""
        if isinstance(cls._loader_registry, type):
            cls._loader_registry = cls._loader_registry()
        return cls._loader_registry

    @classmethod
    def load_from(cls, obj: Any, key: str | None = None) -> "Pile":
        data = cls.get_loader_registry().load_from(obj, key)
        return cls([Node.from_dict(d) for d in data])

    @classmethod
    def register_loader(
        cls,
        key: str,
        loader: Type[PileLoader],
    ) -> None:
        """Register a new converter. Can be used for both a class and/or an instance."""
        cls.get_loader_registry().register(key, loader)


def pile(
    items: Any = None,
    item_type=None,
    order: list[str] | None = None,
    strict: bool = False,
    **kwargs,
) -> Pile:
    """
    type alias type for Pile class. Create a new Pile instance.

    Args:
        items: A single or sequence/mapping of observable item(s)
        item_type: Allowed types for items in the pile.
        order: Initial order of items. Defaults to None.
        strict: If True, enforce strict type checking, otherwise
                will allow the subclasses as well.

    Raises:
        LionValueError, LionTypeError

    Returns:
        Pile: A new Pile instance.
    """

    return Pile(
        items=items,
        item_type=item_type,
        order=order,
        strict=strict,
        **kwargs,
    )


__all__ = ["Pile", "pile"]
