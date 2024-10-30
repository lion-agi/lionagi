# Pile API Documentation

## Overview

The `Pile` class is a thread-safe, async-compatible, ordered collection of Observable elements in the Lion framework. It combines the characteristics of both lists and dictionaries, providing fast access by index or unique identifier while maintaining item order.

## Class Definition

```python
class Pile(Element, Collective, Generic[T]):
    """Thread-safe async-compatible, ordered collection of Observable elements."""
```

## Key Features

- Ordered storage with O(1) access by index or Lion ID
- Optional type enforcement
- Thread-safe write operations
- Asynchronous support for key operations
- Flexible synchronous and asynchronous iteration

## Attributes

- `pile: dict[str, T]` - Internal storage mapping Lion IDs to items
- `item_type: set[Type[Observable]] | None` - Set of allowed types for items
- `order: Progression` - Maintains the order of items
- `strict: bool` - Whether to enforce strict type checking

## Constructor

```python
def __init__(
    self,
    items: Any = None,
    item_type: set[Type[Observable]] | None = None,
    order: Progression | list | None = None,
    strict: bool = False,
    **kwargs,
)
```

Initialize a Pile instance.

## Methods

### Synchronous Methods

#### Item Access and Modification

- `__getitem__(self, key: int | str | slice) -> T | "Pile"`: Get item(s) by index, ID, or slice
- `__setitem__(self, key: int | str | slice, item: T | Sequence[T]) -> None`: Set item(s)
- `pop(self, key: int | str | slice, default: Any = LN_UNDEFINED) -> T | "Pile" | None`: Remove and return item(s)
- `get(self, key: int | str | slice, default: Any = LN_UNDEFINED) -> T | "Pile" | None`: Get item(s) with default
- `remove(self, item: T) -> None`: Remove a specific item
- `include(self, item: T | Iterable[T]) -> None`: Include item(s) if not present
- `exclude(self, item: T | Iterable[T]) -> None`: Exclude item(s) if present
- `update(self, other) -> None`: Update Pile with items from another iterable or Pile
- `insert(self, index: int, item: T) -> None`: Insert an item at a specific position
- `append(self, item: T) -> None`: Append an item to the end (alias for `include`)

#### Collection Operations

- `clear(self) -> None`: Remove all items
- `keys(self) -> Sequence[str]`: Return a sequence of all keys (Lion IDs)
- `values(self) -> Sequence[T]`: Return a sequence of all values
- `items(self) -> Sequence[tuple[str, T]]`: Return a sequence of all (key, value) pairs
- `is_empty(self) -> bool`: Check if the Pile is empty
- `size(self) -> int`: Get the number of items

#### Iteration and Conversion

- `__iter__(self) -> Iterator[T]`: Return an iterator over the items
- `__next__(self) -> T`: Return the next item
- `__list__(self) -> list[T]`: Convert the Pile to a list

#### Arithmetic Operations

- `__add__(self, other: T | Iterable[T]) -> "Pile"`: Create a new Pile with added items
- `__sub__(self, other: T | Iterable[T]) -> "Pile"`: Create a new Pile with items removed
- `__iadd__(self, other: T | Iterable[T]) -> "Pile"`: Add items in-place
- `__isub__(self, other: T | Iterable[T]) -> "Pile"`: Remove items in-place
- `__radd__(self, other: T | Iterable[T]) -> "Pile"`: Reverse addition

#### Serialization

- `to_dict(self, **kwargs) -> dict`: Convert the Pile to a dictionary representation
- `from_dict(cls, data: dict[str, Any]) -> "Pile"`: Create a Pile instance from a dictionary
- `dump(self, clear=True) -> dict`: Dump Pile contents to a dictionary and optionally clear
- `load(cls, data: dict) -> "Pile"`: Load a Pile from a dictionary

### Asynchronous Methods

- `asetitem(self, key: int | str | slice, item: T | Iterable[T]) -> None`: Asynchronously set item(s)
- `apop(self, key: int | str | slice, default: Any = LN_UNDEFINED) -> T | "Pile" | None`: Asynchronously remove and return item(s)
- `aremove(self, item: T) -> None`: Asynchronously remove a specific item
- `ainclude(self, item: T | Iterable[T]) -> None`: Asynchronously include item(s)
- `aexclude(self, item: T | Iterable[T]) -> None`: Asynchronously exclude item(s)
- `aclear(self) -> None`: Asynchronously clear all items
- `aupdate(self, other: Any) -> None`: Asynchronously update Pile
- `aget(self, key: Any, default=LN_UNDEFINED)`: Asynchronously get item(s)
- `__aiter__(self) -> AsyncIterator[T]`: Asynchronous iterator
- `__anext__(self) -> T`: Asynchronously get next item
- `adump(self, clear=True) -> dict`: Asynchronously dump Pile contents

## Usage Examples

### Creating a Pile

```python
from lion_core.generic.pile import Pile, pile
from lionabc import Observable

class MyItem(Observable):
    def __init__(self, value):
        super().__init__()
        self.value = value

# Create a Pile with type checking
my_pile = Pile(items=[MyItem(1), MyItem(2)], item_type={MyItem})

# Use the pile helper function
another_pile = pile(items=[MyItem(3), MyItem(4)], item_type={MyItem})
```

### Adding and Removing Items

```python
# Add items
my_pile.include(MyItem(5))
my_pile.append(MyItem(6))

# Remove items
removed_item = my_pile.pop(0)
my_pile.remove(MyItem(2))

# Update with multiple items
my_pile.update([MyItem(7), MyItem(8)])
```

### Accessing Items

```python
# By index
first_item = my_pile[0]

# By slice
slice_of_items = my_pile[1:3]

# By ID
item_by_id = my_pile[first_item.ln_id]

# With default value
item = my_pile.get("non_existent_id", default=MyItem(-1))
```

### Iteration

```python
# Synchronous iteration
for item in my_pile:
    print(item.value)

# Asynchronous iteration
async for item in my_pile:
    print(item.value)
```

### Arithmetic Operations

```python
# Combine piles
combined_pile = my_pile + another_pile

# Remove items
result_pile = my_pile - [MyItem(1), MyItem(2)]

# In-place operations
my_pile += [MyItem(9), MyItem(10)]
my_pile -= [MyItem(3)]
```

### Serialization

```python
# Convert to dictionary
pile_dict = my_pile.to_dict()

# Create from dictionary
new_pile = Pile.from_dict(pile_dict)

# Dump and load
dumped_data = my_pile.dump()
loaded_pile = Pile.load(dumped_data)
```

## Best Practices

1. Use type hints and the `item_type` parameter to ensure type safety within your Pile.
2. Prefer the `include` and `exclude` methods over direct list manipulation for better type checking and thread safety.
3. Use asynchronous methods (`ainclude`, `aexclude`, etc.) in async contexts for better performance and concurrency.
4. When iterating over a Pile in a multi-threaded or async environment, be aware that the Pile's state may change. Use the provided snapshot iteration to prevent issues.
5. Utilize the arithmetic operations (`+`, `-`, `+=`, `-=`) for efficient Pile manipulation.
6. When subclassing `Pile`, use the `@synchronized` and `@async_synchronized` decorators for methods that modify state to maintain thread-safety.

## Notes

- The `Pile` class is not safe for concurrent writes from multiple threads or asyncio tasks without external synchronization.
- Modifying the Pile during iteration may lead to unexpected behavior. Use the iteration snapshot for safe concurrent access.
- The `strict` parameter enforces exact type matching when set to `True`. When `False`, it allows subclasses of the specified `item_type`.
- The `Pile` class uses a `Progression` object internally to maintain item order, providing both list-like and dict-like access patterns.
