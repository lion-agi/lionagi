import contextlib
from collections import deque
from collections.abc import Mapping

from pydantic import Field

from .abc import Element, ItemNotFoundError, LionIDable, LionTypeError, Record
from .pile import Pile, pile
from .progression import Progression, progression


class Flow(Element):
    """
    Represents a flow of categorical sequences.

    Attributes:
        sequences (Pile[Progression]): A collection of progression sequences.
        registry (dict[str, str]): A registry mapping sequence names to IDs.
        default_name (str): The default name for the flow.
    """

    sequences: Pile[Progression] = Field(
        default_factory=lambda: pile({}, Progression, use_obj=True)
    )

    registry: dict[str, str] = {}
    default_name: str = "main"

    def __init__(self, sequences=None, default_name=None):
        """
        Initializes a Flow instance.

        Args:
            sequences (optional): Initial sequences to include in the flow.
            default_name (optional): Default name for the flow.
        """
        super().__init__()
        self.sequences = self._validate_sequences(sequences)
        self.default_name = default_name or "main"

    def _validate_sequences(self, value):
        """
        Validates and initializes the sequences.

        Args:
            value: Sequences to validate and initialize.

        Returns:
            Pile[Progression]: A pile of progression sequences.
        """
        if not value:
            return pile({}, Progression, use_obj=True)
        if isinstance(value, dict):
            return pile(value, Progression, use_obj=True)
        if (
            isinstance(value, list)
            and len(value) > 0
            and isinstance(value[0], Progression)
        ):
            return pile({i.ln_id: i for i in value}, Progression, use_obj=True)
        return pile({}, Progression, use_obj=True)

    def all_orders(self) -> list[list[str]]:
        """
        Retrieves all orders in the flow.

        Returns:
            list[list[str]]: A list of lists containing sequence orders.
        """
        return [list(seq) for seq in self.sequences]

    def all_unique_items(self) -> tuple[str]:
        """
        Retrieves all unique items across sequences.

        Returns:
            Tuple[str]: A tuple of unique items.
        """
        return tuple({item for seq in self.sequences for item in seq})

    def keys(self):
        yield from self.sequences.keys()

    def values(self):
        yield from self.sequences.values()

    def items(self):
        yield from self.sequences.items()

    def get(self, seq=None, default=...):
        """
        Retrieves a sequence by name or returns the default sequence.

        Args:
            seq (optional): The name of the sequence.
            default (optional): Default value if sequence is not found.

        Returns:
            Progression: The requested sequence.
        """

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
            self.sequences[seq]
            if default == ...
            else self.sequences.get(seq, default)
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
        _sequence = self._find_sequence(seq, None) or self._find_sequence(
            name, None
        )
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
        """
        Excludes an item or sequence from the flow.

        Args:
            seq (LionIDable, optional): The sequence to exclude from.
            item (optional): The item to exclude.
            name (optional): The name of the sequence.

        Returns:
            bool: True if exclusion was successful, False otherwise.
        """
        # if sequence is not None, we will not check the name
        if seq is not None:

            with contextlib.suppress(ItemNotFoundError, AttributeError):
                if item:
                    # if there is item, we exclude it from the sequence
                    self.sequences[self.registry[seq]].exclude(item)
                    return item not in self.sequences[self.registry[seq]]
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
        """
        Registers a sequence with a name.

        Args:
            sequence (Progression): The sequence to register.
            name (str, optional): The name for the sequence.

        Raises:
            LionTypeError: If the sequence is not of type Progression.
            ValueError: If the sequence name already exists.
        """

        if not isinstance(sequence, Progression):
            raise LionTypeError(f"Sequence must be of type Progression.")

        name = name or sequence.name
        if not name:
            if self.default_name in self.registry:
                name = sequence.ln_id
            else:
                name = self.default_name

        if name in self.registry:
            raise ValueError(f"Sequence '{name}' already exists.")

        self.sequences.include(sequence)
        self.registry[name] = sequence.ln_id

    def append(self, item, sequence=None, /):
        """
        Appends an item to a sequence.

        Args:
            item: The item to append.
            sequence (optional): The sequence to append to.
        """
        if not sequence:
            if self.default_name in self.registry:
                sequence = self.registry[self.default_name]
                self.sequences[sequence].include(item)
                return

            p = progression(item, self.default_name)
            self.register(p)
            return

        if sequence in self.sequences:
            self.sequences[sequence].include(item)
            return

        if sequence in self.registry:
            self.sequences[self.registry[sequence]].include(item)
            return

        p = progression(item, sequence if isinstance(sequence, str) else None)
        self.register(p)

    def popleft(self, sequence=None, /):
        """
        Removes and returns an item from the left end of a sequence.

        Args:
            sequence (optional): The sequence to remove the item from.

        Returns:
            The removed item.
        """
        sequence = self._find_sequence(sequence)
        return self.sequences[sequence].popleft()

    def shape(self):
        return {
            key: len(self.sequences[value])
            for key, value in self.registry.items()
        }

    def get(self, sequence: str, /, default=...) -> deque[str] | None:
        sequence = getattr(sequence, "ln_id", None) or sequence

        if sequence in self.registry:
            return self.sequences[self.registry[sequence]]

        try:
            return self.sequences[sequence]
        except KeyError as e:
            if default == ...:
                raise e
            return default

    def remove(self, item, sequence="all"):
        """
        Removes an item from a sequence or all sequences.

        Args:
            item: The item to remove.
            sequence (str, optional): The sequence to remove the item from. Defaults to "all".
        """
        if sequence == "all":
            for seq in self.sequences:
                seq.remove(item)
            return

        sequence = self._find_sequence(sequence)
        self.sequences[sequence].remove(item)

    def __len__(self):
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)

    def __next__(self):
        return next(self.__iter__())

    def _find_sequence(self, sequence=None, default=...):
        """
        Finds the sequence ID in the registry or sequences.

        Args:
            sequence (optional): The sequence to find.
            default (optional): The default value if sequence is not found.

        Returns:
            The found sequence ID.

        Raises:
            ItemNotFoundError: If no sequence is found.
        """

        if not sequence:
            if self.default_name in self.registry:
                return self.registry[self.default_name]
            if default != ...:
                return default
            raise ItemNotFoundError("No sequence found.")

        if sequence in self.sequences:
            return (
                sequence.ln_id
                if isinstance(sequence, Progression)
                else sequence
            )

        if sequence in self.registry:
            return self.registry[sequence]

    def to_dict(self):
        return {
            "sequences": self.sequences.to_dict(),
            "registry": self.registry,
            "default_name": self.default_name,
        }

    def to_df(self):
        return self.sequences.to_df()


def flow(sequences=None, default_name=None, /):
    """
    Creates a new Flow instance.

    Args:
        sequences (optional): Initial sequences to include in the flow.
        default_name (optional): Default name for the flow.

    Returns:
        Flow: A new Flow instance.
    """
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
