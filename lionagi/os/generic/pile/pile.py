from lion_core.generic.pile import Pile as CorePile


class Pile(CorePile):
    pass


def pile(*args, **kwargs):
    return Pile(*args, **kwargs)


__all__ = ["Pile", "pile"]
