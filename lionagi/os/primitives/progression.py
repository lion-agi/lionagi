from typing import TypeAliasType, Any
from lion_core.generic.progression import Progression


def _prog(order: Any = None, name: str | None = None) -> Progression:
    """
    Create a new Progression instance.

    Args:
        order: The initial order of items in the progression.
        name: The name of the progression.

    Returns:
        A new Progression instance.
    """
    return Progression(order=order, name=name)


prog = TypeAliasType("prog", Progression)
prog.__call__ = _prog

__all__ = ["Progression", "prog"]
