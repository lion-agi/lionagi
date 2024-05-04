from collections.abc import Generator, Mapping, Iterable
from typing import TypeVar, Type, Tuple, Any
import contextlib
from pydantic import Field, field_validator

from lionagi.libs.ln_convert import is_same_dtype
from ..abc import Record, Component, LionIDable, get_lion_id
from .._util import _to_list_type
from ..abc._exceptions import LionValueError, LionTypeError, ItemNotFoundError


T = TypeVar("T", bound=Component)


class Pile(Component, Record):

    pile: dict[str, T] = Field(default_factory=dict)
    item_type: set[Type[Component]] | None = Field(default=None)

    def keys(self) -> Generator[str, None, None]:
        yield from self.pile.keys()

    def values(self) -> Generator[T, None, None]:
        yield from self.pile.values()

    def items(self) -> Generator[Tuple[str, T], None, None]:
        yield from self.pile.items()

    def __getitem__(self, item: LionIDable) -> T:
        return self.pile.get(get_lion_id(item))

    def __setitem__(self, key: LionIDable, value: T) -> None:
        if "lionagi" not in str(type(value)):
            raise LionTypeError("Value must be part of lionagi system.")
        if self.item_type and type(value) not in self.item_type:
            raise LionTypeError(f"Invalid item type. Expected {self.item_type}")
        self.pile[get_lion_id(key)] = value

    def __contains__(self, item: LionIDable) -> bool:
        return get_lion_id(item) in self.pile

    def pop(self, item: LionIDable, default=..., /) -> T | None:
        with contextlib.suppress(KeyError):
            return self.pile.pop(get_lion_id(item))
        if default == ...:
            raise ItemNotFoundError(item)
        return default

    def get(self, item: LionIDable, default: Any = ..., /) -> T | None:
        with contextlib.suppress(LionTypeError):
            return self[item]
        if default == ...:
            raise ItemNotFoundError(item)
        return default

    def remove(self, item: LionIDable, /):
        """remove, raise error if not found"""
        try:
            self.pop(item)
            return True
        except Exception as e:
            raise e

    def update(self, other: any, /):
        self.pile.update(self._validate_pile(other))

    def clear(self):
        """Removes all items from the pile."""
        self.pile.clear()

    def include(self, item: T, /) -> bool:
        with contextlib.suppress(Exception):
            if item not in self:
                self[item] = item
        return item in self

    def exclude(self, item: LionIDable, /) -> bool:
        with contextlib.suppress(Exception):
            if item in self:
                self.pop(item)
        return item not in self

    def is_homogenous(self) -> bool:
        return len(self.pile) < 2 or all(is_same_dtype(self.pile.values()))

    def is_empty(self) -> bool:
        return not self.pile

    @field_validator("item_type", mode="before")
    def _validate_item_type(cls, value):
        if value is None:
            return None

        value = _to_list_type(value)

        for i in value:
            if not isinstance(i, type(Component)):
                raise LionTypeError(
                    "Invalid item type. Expected a subclass of Component."
                )

        if len(value) != len(set(value)):
            raise LionValueError("Detected duplicated item types in item_type.")

        if len(value) > 0:
            return set(value)

    @field_validator("pile", mode="before")
    def _validate_pile(cls, value, /):
        value = _to_list_type(value)
        if getattr(cls, "item_type", None) is not None:
            for i in value:
                if not type(i) in cls.item_type:
                    raise LionTypeError(
                        f"Invalid item type in pile. Expected {cls.item_type}"
                    )

        if isinstance(value, list):
            return {i.ln_id: i for i in value}

        raise LionValueError("Invalid pile value")

    def __iter__(self):
        return iter(self.values())

    def __len__(self) -> int:
        """Return the number of items in the pile."""
        return len(self.pile)

    def __iadd__(self, other: T) -> "Pile":
        """Add an lion item to the pile using the += operator."""
        self.include(other)
        return self

    def __isub__(self, other: LionIDable) -> "Pile":
        """
        Remove an item from the pile using the -= operator.
        raise ItemNotFoundError if item is not found.
        """
        self.remove(other)
        return self


def pile(
    items: Iterable[T] | None = None, item_type: set[Type] | None = None, /
) -> Pile:
    """Create a new Pile instance."""
    if not items:
        return Pile(item_type=item_type) if item_type else Pile()
    return Pile(pile=items, item_type=item_type)
