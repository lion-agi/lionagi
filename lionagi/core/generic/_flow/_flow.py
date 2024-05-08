"""flow as categorical sequences"""

from collections.abc import Mapping
from collections import deque
from typing import Tuple
from pydantic import Field, field_validator
import contextlib
from ..abc import Record, Component, LionTypeError, ItemNotFoundError, LionIDable
from .._pile._pile import Pile, pile

from ._progression import Progression, progression


class Flow(Component):

    sequences: Pile[Progression] = Field(default_factory=lambda: pile({}, Progression))
    registry: dict[str, str] = {}
    default_name: str = "main"

    @field_validator("sequences", mode="before")
    def _validate_sequences(cls, value):
        if not value:
            return pile({}, Progression)
        if isinstance(value, dict):
            return pile(value, Progression)
        if (
            isinstance(value, list)
            and len(value) > 0
            and isinstance(value[0], Progression)
        ):
            return pile({i.ln_id: i for i in value}, Progression)
        return pile({}, Progression)

    def all_orders(self) -> list[list[str]]:
        return [list(seq) for seq in self.sequences]

    def all_unique_items(self) -> Tuple[str]:
        return tuple({item for seq in self.sequences for item in seq})

    def keys(self):
        yield from self.sequences.keys()

    def values(self):
        yield from self.sequences.values()

    def items(self):
        yield from self.sequences.pile()

    def get(self, seq=None, default=...):

        if seq is None:
            if self.default_name in self.registry:
                seq = self.registry[self.default_name]
                seq = self.sequences[seq]
            else:
                raise ItemNotFoundError("No sequence found.")

        elif seq is not None and seq in self:
            if not isinstance(seq, (str, Progression)):
                raise LionTypeError("Sequence must be of type Progression.")

            if isinstance(seq, str):
                seq = self.registry[seq]

        return (
            self.sequences[seq] if default == ... else self.sequences.get(seq, default)
        )

    def __getitem__(self, seq=None, /):
        return self.get(seq)

    def __setitem__(self, seq: LionIDable | str, index=None, value=None, /):
        if seq not in self:
            raise ItemNotFoundError(f"Sequence {seq}")

        if index:
            self.sequences[seq][index] = value
            return

        self.sequences[seq] = value

    def __contains__(self, item):
        return (
            item in self.registry
            or item in self.sequences
            or item in self.all_unique_items()
        )

    def shape(self):
        return (len(self.all_orders()), [len(i) for i in self.all_orders()])

    def size(self):
        return sum(len(seq) for seq in self.all_orders())

    def clear(self):
        self.sequences.clear()
        self.registry.clear()

    def include(self, seq=None, item=None, name=None):
        _sequence = self._find_sequence(seq, None) or self._find_sequence(name, None)
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
                if isinstance(seq, Progression):
                    if item and seq.include(item):
                        self.register(seq, name)
                    return seq in self

                return False

    def exclude(self, seq: LionIDable = None, item=None, name=None):

        # if sequence is not None, we will not check the name
        if seq is not None:

            with contextlib.suppress(ItemNotFoundError):
                if item:
                    # if there is item, we exclude it from the sequence
                    return self.sequences[seq].exclude(item)
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(seq.name or seq.ln_id, None)
                    return a is not None and self.sequences.exclude(seq)
            return False

        elif name is not None:

            with contextlib.suppress(ItemNotFoundError):
                if item:
                    # if there is item, we exclude it from the sequence
                    return self.sequences[self.registry[name]].exclude(item)
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(name, None)
                    return a is not None and self.sequences.exclude(a)
            return False

    def register(self, sequence: Progression, name: str = None):
        if not isinstance(sequence, Progression):
            raise LionTypeError(f"Sequence must be of type Progression.")

        if name is None and sequence.name is None:
            if self.default_name in self.registry:
                name = sequence.ln_id
            else:
                name = self.default_name

        if name in self.registry:
            raise ValueError(f"Sequence '{name}' already exists.")

        self.sequences.include(sequence)
        self.registry[name] = sequence.ln_id

    def append(self, item, sequence=None, /):
        if not sequence:
            if self.default_name in self.registry:
                sequence = self.registry[self.default_name]
                self.sequences[sequence].include(item)
                return

            p = progression(item, self.default_name)
            self.register(p)
            return

        if sequence in self.sequences:
            self.sequences[sequence] += item
            return

        if sequence in self.registry:
            self.sequences[self.registry[sequence]] += item
            return

        p = progression(item, sequence if isinstance(sequence, str) else None)
        self.register(p)

    def popleft(self, sequence=None, /):
        sequence = self._find_sequence(sequence)
        return self.sequences[sequence].popleft()

    def shape(self):
        return {sequence: len(seq) for sequence, seq in self.items()}

    def get(self, sequence: str, /, default=False) -> deque[str] | None:
        try:
            return self.sequences[sequence]
        except KeyError as e:
            if default == False:
                raise e
            return default

    def remove(self, item, sequence="all"):
        """if sequence is 'all', will attempt to remove the item from all sequencees."""
        if sequence == "all":
            for seq in self.sequences:
                seq.remove(item)

        sequence = self._find_sequence(sequence)
        self.sequences[sequence].remove(item)

    def __len__(self):
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)

    def __next__(self):
        return next(self.__iter__())

    def _find_sequence(self, sequence=None, default=...):
        """find the sequence id in the registry or sequencees. can be name, progression obj or id"""

        if not sequence:
            if self.default_name in self.registry:
                return self.registry[self.default_name]
            if default != ...:
                return default
            raise ItemNotFoundError("No sequence found.")

        if sequence in self.sequences:
            return sequence.ln_id if isinstance(sequence, Progression) else sequence

        if sequence in self.registry:
            return self.registry[sequence]

    def to_df(self):
        return self.sequences.to_df()


def flow(sequences=None, default_name=None, /):
    if sequences is None:
        return Flow()

    flow = Flow()
    if default_name:
        flow.default_name = default_name

    # if mapping we assume a dictionary of in {name: data} format
    if isinstance(sequences, (Mapping, Record)):
        for name, seq in sequences.items():
            if not isinstance(seq, Progression):
                try:
                    seq = progression(seq, name)
                except Exception as e:
                    raise e
            if (a := name or seq.name) is not None:
                flow.register(seq, a)
            else:
                flow.register(seq, seq.ln_id)
        return flow

    for seq in sequences:
        if not isinstance(seq, Progression):
            try:
                seq = progression(seq)
            except Exception as e:
                raise e
        flow.register(seq)
    return flow
