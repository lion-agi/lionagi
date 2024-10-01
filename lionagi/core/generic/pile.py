import warnings

from lion_core.generic.pile import Pile
from lionabc.exceptions import ItemNotFoundError, LionValueError


def _add(self: Pile, other) -> Pile:
    warnings.warn(
        "`Pile.__add__` is deprecated and will be removed in v1.0.0 "
        "Please use the `|` operator instead."
        "if you intend to do: `p2 = p1 + node`,  you should use `p2 = p1 | pile(node)`   "
        "if you intend to do: `p3 = p1 + p2`, you should use `p3 = p1 | p2` ",
        DeprecationWarning,
        stacklevel=2,
    )
    if not isinstance(other, Pile):
        try:
            other = Pile(other)
        except Exception as e:
            raise LionValueError(f"Cannot add {type(other)} to {type(self)}.") from e

    return self.__or__(other)


def _iadd(self: Pile, other) -> Pile:
    warnings.warn(
        "`Pile.__iadd__` is deprecated and will be removed in v1.0.0 "
        "Please use the `|=` operator instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if not isinstance(other, Pile):
        try:
            other = Pile(other)
        except Exception as e:
            raise LionValueError(f"Cannot add {type(other)} to {type(self)}.") from e

    return self.__ior__(other)


def _sub(self: Pile, other) -> Pile:
    warnings.warn(
        "`Pile.__sub__` is deprecated and will be removed in v1.0.0  "
        "if you intend to do: `p2 = p1 - node`,  you should use `if node in p1:  p2 = p1 ^ pile(node)`   "
        "if you intend to do: `p3 = p1 - p2`, you should use `if list(p2) in p1:  p3 = p1 ^ p2",
        DeprecationWarning,
        stacklevel=2,
    )

    _copy = Pile.from_dict(self.to_dict())
    if other not in self:
        raise ItemNotFoundError(other)

    length = len(_copy)

    try:
        _copy.exclude(other)
    except Exception as e:
        raise LionValueError("Item cannot be excluded from the pile.") from e

    if len(_copy) == length:
        raise LionValueError("Item cannot be excluded from the pile.")

    return _copy


def _isub(self: Pile, other) -> Pile:
    warnings.warn(
        "`Pile.__isub__` is deprecated and will be removed in v1.0.0 "
        "Please use <Pile.exclude> instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    self.exclude(other)
    return self


def _radd(self: Pile, other) -> Pile:
    return other + self


Pile.__add__ = _add
Pile.__iadd__ = _iadd
Pile.__sub__ = _sub
Pile.__isub__ = _isub
Pile.__radd__ = _radd
