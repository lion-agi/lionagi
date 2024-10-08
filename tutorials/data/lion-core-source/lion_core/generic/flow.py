import contextlib
from collections.abc import Iterator
from typing import Any

from lionabc import Collective
from lionabc.exceptions import ItemNotFoundError, LionTypeError, LionValueError
from lionfuncs import LN_UNDEFINED
from pydantic import Field
from pydantic_core import PydanticUndefined
from typing_extensions import Self

from lion_core.generic.element import Element
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, progression


class Flow(Element):
    progressions: Pile[Progression] = Field(
        default_factory=lambda: pile({}, item_type={Progression})
    )

    registry: dict = Field(default_factory=dict)
    default_name: str = Field(None)

    def __init__(
        self,
        progressions: Pile[Progression] | None = None,
        default_name: str | None = None,
    ) -> None:
        """
        Initializes a Flow instance.

        Args:
            sequences (optional): Initial sequences to include in the flow.
            default_name (optional): Default name for the flow.
        """
        super().__init__()
        self.progressions = self._validate_progressions(progressions)

        if default_name:
            self.default_name = default_name

        for prog_ in self.progressions:
            a = prog_.name or prog_.ln_id
            self.register(prog_, a)

    def _validate_progressions(self, value: Any) -> Pile[Progression]:
        try:
            if isinstance(value, Collective):
                if Progression in getattr(value, "item_type", []):
                    return value
                else:
                    value = list(value)
            return pile(value, item_type={Progression})

        except Exception as e:
            raise LionValueError(f"Invalid progressions: {e}")

    def all_orders(self) -> list[list[str]]:
        """Get all progression orders as a list of lists."""
        return [list(seq) for seq in self.progressions]

    def unique(self) -> list[str]:
        """Get a list of unique items across all progressions."""
        return list({item for seq in self.progressions for item in seq})

    def keys(self) -> Iterator[str]:
        """Yield the keys (IDs) of all progressions."""
        yield from self.progressions.keys()

    def values(self) -> Iterator[Progression]:
        """Yield the values (Progression objects) of all progressions."""
        yield from self.progressions.values()

    def items(self) -> Iterator[tuple[str, Progression]]:
        """Yield the (key, value) pairs of all progressions."""
        yield from self.progressions.items()

    def __getitem__(
        self,
        prog_: str | Progression = None,
        default: Any = LN_UNDEFINED,
    ) -> Progression | Any:
        """Get a progression by its ID or name."""
        return self.get(prog_, default)

    def __setitem__(
        self,
        prog_: Progression | str,
        index: int | slice | None = None,
        value: Any = None,
        /,
    ) -> None:
        """Set a progression or an item within a progression."""
        if prog_ not in self:
            raise ItemNotFoundError(f"Sequence {prog_}")

        if index:
            self.progressions[prog_][index] = value
            return

        self.progressions[prog_] = value

    def __contains__(self, item: Any) -> bool:
        """Check if an item is in any progression or in the registry."""
        check = item in self.registry
        if check is False:
            check = item in self.progressions
        if check is False:
            check = item in self.unique()
        return check

    def shape(self) -> tuple[int, list[int]]:
        """
        Get the shape of the Flow.

        Returns:
            A tuple containing the number of progressions and a list of
            their lengths.
        """
        ao = self.all_orders()
        return (len(ao), [len(i) for i in ao])

    def size(self) -> int:
        """
        Get the total number of items across all progressions.

        Returns:
            The total number of items in the Flow.
        """

        return sum(len(seq) for seq in self.all_orders())

    def clear(self) -> None:
        """Clear all progressions and the registry."""
        self.progressions.clear()
        self.registry.clear()

    def include(
        self,
        prog_: str | Progression | None = None,
        /,
        item: Any = None,
        name: str | None = None,
    ) -> bool | None:
        """
        Include a progression or an item in a progression.

        Args:
            prog_: The progression to include or modify.
            item: The item to include in the progression.
            name: The name for the progression.

        Returns:
            True if the inclusion was successful, False otherwise.
        """
        _sequence = self._find_prog(prog_, None)
        if _sequence is None:
            _sequence = self._find_prog(name, None)

        if not _sequence:
            if not item and not name:
                """None is not in the registry or sequencees."""
                return False
            if item:
                self.append(item, name)
                return item in self

        else:
            if _sequence in self:
                if not item and not name:
                    return True
                if item:
                    self.append(item, _sequence)
                    return item in self
                return True  # will ignore name if sequence is already found

            else:
                if isinstance(prog_, Progression):
                    if item and prog_.include(item):
                        self.register(prog_, name)
                    return prog_ in self

                return False

    def exclude(
        self,
        prog_: Progression | str | None = None,
        /,
        item: Any = None,
        name: str | None = None,
    ) -> bool | Any | None:
        """
        Exclude a progression or an item from a progression.

        Args:
            seq: The progression to exclude or modify.
            item: The item to exclude from the progression.
            name: The name of the progression to exclude.

        Returns:
            True if the exclusion was successful, False otherwise.
        """
        # if sequence is not None, we will not check the name
        if prog_ is not None:
            with contextlib.suppress(ItemNotFoundError, AttributeError):
                if item:
                    # if there is item, we exclude it from the sequence
                    self.progressions[self.registry[prog_]].exclude(item)
                    return item not in self.progressions[self.registry[prog_]]
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(prog_.name or prog_.ln_id, None)
                    return a is not None and self.progressions.exclude(prog_)
            return False

        if name is not None:
            with contextlib.suppress(ItemNotFoundError):
                if item:
                    # if there is item, we exclude it from the sequence
                    return self.progressions[self.registry[name]].exclude(item)
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(name, None)
                    return a is not None and self.progressions.exclude(a)
            return False

    def register(self, prog_: Progression, /, name: str | None = None) -> None:
        """
        Register a new progression.

        Args:
            prog_: The Progression object to register.
            name: The name for the progression.

        Raises:
            LionTypeError: If prog_ is not a Progression.
            ValueError: If the name already exists in the registry.
        """
        if not isinstance(prog_, Progression):
            raise LionTypeError("Sequence must be of type Progression.")

        name = name or prog_.name
        if not name:
            if self.default_name in self.registry:
                name = prog_.ln_id
            else:
                name = self.default_name

        if name in self.registry:
            raise ValueError(f"Sequence '{name}' already exists.")

        self.progressions.include(prog_)
        self.registry[name] = prog_.ln_id

    def append(
        self, item: Any, prog_: str | Progression | None = None, /
    ) -> None:
        """
        Append an item to a progression.

        Args:
            item: The item to append.
            prog_: The progression to append to (optional).
        """
        if not prog_:
            if self.default_name in self.registry:
                prog_ = self.registry[self.default_name]
                self.progressions[prog_].include(item)
                return

            p = progression(item, self.default_name)
            self.register(p)
            return

        if prog_ in self.progressions:
            self.progressions[prog_].include(item)
            return

        if prog_ in self.registry:
            self.progressions[self.registry[prog_]].include(item)
            return

        p = progression(item, prog_ if isinstance(prog_, str) else None)
        self.register(p)

    def popleft(self, prog_: str | Progression | None = None, /) -> str | Any:
        """
        Remove and return the leftmost item from a progression.

        Args:
            prog_: The progression to pop from (optional).

        Returns:
            The leftmost item from the specified progression.
        """
        prog_ = self._find_prog(prog_)
        return self.progressions[prog_].popleft()

    def get(
        self,
        prog_: Progression | str | None = None,
        /,
        default: Any = LN_UNDEFINED,
    ) -> Progression | Any:
        """
        Get a progression by its ID or name.

        Args:
            prog_: The progression ID or name.
            default: Default value if progression is not found.

        Returns:
            The requested Progression or the default value.

        Raises:
            ItemNotFoundError: If no progression is found and no default
                is provided.
        """
        prog_ = getattr(prog_, "ln_id", None) or prog_

        if prog_ is None:
            if self.default_name in self.registry:
                return self.progressions[self.registry[self.default_name]]
            if default in [LN_UNDEFINED, PydanticUndefined]:
                raise ItemNotFoundError("No progression found.")

        if prog_ in self.registry:
            return self.progressions[self.registry[prog_]]

        try:
            return self.progressions[prog_]
        except KeyError as e:
            if default in [LN_UNDEFINED, PydanticUndefined]:
                raise e
            return default

    def remove(
        self, item: Any, prog_: str | Progression | None = None, /
    ) -> None:
        """
        Remove an item from one or all progressions.

        Args:
            item: The item to remove.
            prog_: The progression to remove from, or "all" for all
                    progressions.
        """
        if prog_ == "all":
            for seq in self.progressions:
                seq.remove(item)
            return

        prog_ = self._find_prog(prog_)
        self.progressions[prog_].remove(item)

    def __len__(self) -> int:
        return len(self.progressions)

    def __iter__(self) -> Iterator[Progression]:
        return iter(self.progressions)

    def __next__(self) -> Progression:
        return next(self.__iter__())

    def _find_prog(
        self,
        prog_: str | Progression | None = None,
        default: Any = LN_UNDEFINED,
    ):
        if not prog_:
            if self.default_name in self.registry:
                return self.registry[self.default_name]
            if default not in [LN_UNDEFINED, PydanticUndefined]:
                return default
            raise ItemNotFoundError("No progression found.")

        if prog_ in self.progressions:
            return prog_.ln_id if isinstance(prog_, Progression) else prog_

        if prog_ in self.registry:
            return self.registry[prog_]

    def to_dict(self) -> dict[str, Any]:
        return {
            "progressions": self.progressions.to_dict(),
            "default_name": self.default_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        progressions = Pile.from_dict(data["progressions"])
        return cls(progressions, data["default_name"])


def flow(
    progressions: Pile[Progression] | None = None,
    default_name: str | None = None,
):
    return Flow(progressions, default_name)


__all__ = ["Flow", "flow"]

# Flow: lion_core/generic/flow.py
