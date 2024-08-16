from typing import TypeAliasType, Any
from lion_core.generic.pile import Pile as CorePile


class Pile(CorePile):
    """async-compatible, ordered collection of Observable elements."""

    pass


def _pile(
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


pile = TypeAliasType("pile", Pile)
pile.__call__ = _pile
pile.__doc__ = _pile.__doc__

__all__ = ["Pile", "pile"]
