import warnings
from collections.abc import Iterable
from typing import TypeVar

from lion_core.generic.base import RealElement
from lion_core.generic.pile import Pile
from lionabc.exceptions import ItemNotFoundError, LionValueError
from lionfuncs import LN_UNDEFINED

T = TypeVar("T", bound=RealElement)


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
            other = self.__class__(other)
        except Exception as e:
            raise LionValueError(
                f"Cannot add {type(other)} to {type(self)}."
            ) from e

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
            other = self.__class__(other)
        except Exception as e:
            raise LionValueError(
                f"Cannot add {type(other)} to {type(self)}."
            ) from e

    return self.__ior__(other)


def _sub(self: Pile, other) -> Pile:
    warnings.warn(
        "`Pile.__sub__` is deprecated and will be removed in v1.0.0  "
        "if you intend to do: `p2 = p1 - node`,  you should use `if node in p1:  p2 = p1 ^ pile(node)`   "
        "if you intend to do: `p3 = p1 - p2`, you should use `if list(p2) in p1:  p3 = p1 ^ p2",
        DeprecationWarning,
        stacklevel=2,
    )

    _copy = self.__class__.from_dict(self.to_dict())
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


def pile(
    items: Iterable[T] | None = None,
    item_type: set[type] | None = None,
    order=None,
    obj_key=None,
    csv_file=None,
    pd_df=None,
    strict_type: bool = False,
    df=LN_UNDEFINED,  # deprecated
    use_obj=LN_UNDEFINED,  # deprecated
    **kwargs,  # deprecated
) -> Pile[T]:
    """
    Create a new Pile instance.

    This function provides various ways to create a Pile instance:
    - Directly from items
    - From a CSV file
    - From a DataFrame

    Args:
        items (Iterable[T] | None): The items to include in the pile.
        item_type (set[Type] | None): The allowed types of items in the pile.
        order (list[str] | None): The order of items.
        use_obj (bool | None): Whether to treat Record and Ordering as objects.
        csv_file (str | None): The path to a CSV file to load items from.
        df (DataFrame | None): A DataFrame to load items from.
        **kwargs: Additional keyword arguments for loading from CSV or DataFrame.

    Returns:
        Pile[T]: A new Pile instance.

    Raises:
        ValueError: If invalid arguments are provided.
    """
    if df is not LN_UNDEFINED:
        pd_df = pd_df or df
        warnings.warn(
            "`df` is deprecated and will be removed in v1.0.0. "
            "Please use `pd_df` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    if use_obj is not LN_UNDEFINED:
        warnings.warn(
            "`use_obj` is deprecated and will be removed in v1.0.0. ",
            DeprecationWarning,
            stacklevel=2,
        )
    if kwargs:
        warnings.warn(
            "Additional keyword arguments are not supported and will be ignored. Support for additional keyword arguments will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )

    if csv_file and pd_df:
        raise LionValueError(
            "Cannot load items from both a CSV file and a DataFrame."
        )

    if csv_file:
        obj_key = "csv_file"
    elif pd_df:
        obj_key = "pd_df_data"

    if obj_key:
        try:
            return Pile.adapt_from(items, obj_key)
        except Exception as e:
            raise LionValueError(f"Cannot load items from {obj_key}.") from e

    return Pile(
        items=items,
        item_type=item_type,
        order=order,
        strict_type=strict_type,
    )


__all__ = ["Pile", "pile"]
