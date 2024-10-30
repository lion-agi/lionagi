# Progression API Documentation

## Overview

The `Progression` class is a flexible, ordered sequence container for Lion IDs in the Lion framework. It inherits from both `Element` and `Ordering` classes, providing a unique combination of identity management and ordered collection functionality.

## Class Definition

```python
class Progression(Element, Ordering):
    """A flexible, ordered sequence container for Lion IDs."""
```

## Attributes

- `name: str | None` - The name of the progression (optional)
- `order: list[str]` - The ordered list of Lion IDs

## Methods

### Core Functionality

#### `__init__`

```python
def __init__(self, order: Any = None, name: str | None = None):
```

Initializes a new Progression instance.

- `order`: Initial order of items (optional)
- `name`: Name for the progression (optional)

#### `__contains__`

```python
def __contains__(self, item: Any) -> bool:
```

Checks if item(s) are in the progression.

#### `size`

```python
def size(self) -> int:
```

Returns the number of items in the progression.

#### `clear`

```python
def clear(self) -> None:
```

Removes all items from the progression.

#### `is_empty`

```python
def is_empty(self) -> bool:
```

Checks if the progression is empty.

### Item Management

#### `append`

```python
def append(self, item: Any) -> None:
```

Appends an item to the end of the progression.

#### `pop`

```python
def pop(self, index: int | None = None) -> str:
```

Removes and returns an item from the progression.

#### `include`

```python
def include(self, item: Any):
```

Includes item(s) in the progression if not already present.

#### `exclude`

```python
def exclude(self, item: int | Any):
```

Excludes an item or items from the progression.

#### `remove`

```python
def remove(self, item: Any) -> None:
```

Removes the next occurrence of an item from the progression.

#### `popleft`

```python
def popleft(self) -> str:
```

Removes and returns the leftmost item from the progression.

#### `extend`

```python
def extend(self, item: Any) -> None:
```

Extends the progression from the right with another progression.

#### `insert`

```python
def insert(self, index: int, item: Any) -> None:
```

Inserts an item at the specified index.

### Information Retrieval

#### `index`

```python
def index(self, item: Any, start: int = 0, end: int | None = None) -> int:
```

Returns the index of an item in the progression.

#### `count`

```python
def count(self, item: Any) -> int:
```

Returns the number of occurrences of an item.

### Iteration and Access

#### `__iter__`

```python
def __iter__(self) -> Iterator[str]:
```

Returns an iterator over the items in the progression.

#### `__next__`

```python
def __next__(self) -> str:
```

Returns the next item in the progression.

#### `__getitem__`

```python
def __getitem__(self, key: int | slice):
```

Gets an item or slice of items from the progression.

#### `__setitem__`

```python
def __setitem__(self, key: int | slice, value: Any) -> None:
```

Sets an item or slice of items in the progression.

#### `__delitem__`

```python
def __delitem__(self, key: int | slice) -> None:
```

Deletes an item or slice of items from the progression.

### Comparison and Representation

#### `__eq__`

```python
def __eq__(self, other: object) -> bool:
```

Compares two Progression instances for equality.

#### `__repr__`

```python
def __repr__(self) -> str:
```

Returns a string representation of the progression for debugging.

#### `__str__`

```python
def __str__(self) -> str:
```

Returns a user-friendly string representation of the progression.

### Arithmetic Operations

#### `__add__`

```python
def __add__(self, other: Any) -> "Progression":
```

Returns a new progression with items added to the end.

#### `__radd__`

```python
def __radd__(self, other: Any) -> "Progression":
```

Supports right-side addition.

#### `__iadd__`

```python
def __iadd__(self, other: Any) -> "Progression":
```

Adds an item to the end of the progression in-place.

#### `__sub__`

```python
def __sub__(self, other: Any) -> "Progression":
```

Returns a new progression with specified items removed.

#### `__isub__`

```python
def __isub__(self, other: Any) -> "Progression":
```

Removes an item from the progression in-place.

### Utility Functions

#### `__reverse__`

```python
def __reverse__(self) -> Iterator[str]:
```

Returns a reversed progression.

#### `__bool__`

```python
def __bool__(self) -> bool:
```

Checks if the progression is not empty.

#### `__hash__`

```python
def __hash__(self) -> int:
```

Returns a hash value for the progression.

## Usage Examples

### Creating a Progression

```python
from lion_core.generic.progression import Progression, prog

# Create an empty progression
p1 = Progression()

# Create a progression with initial items
p2 = Progression(order=["item1", "item2", "item3"], name="MyProgression")

# Use the prog helper function
p3 = prog(["item4", "item5"], name="AnotherProgression")
```

### Managing Items

```python
# Add items
p1.append("new_item")
p1.include(["item1", "item2"])

# Remove items
removed_item = p1.pop()
p1.exclude("item1")
p1.remove("item2")

# Access items
first_item = p1[0]
slice_of_items = p1[1:3]

# Modify items
p1[0] = "modified_item"
```

### Iterating and Checking

```python
# Iterate over items
for item in p1:
    print(item)

# Check membership
if "item3" in p1:
    print("Item found!")

# Get information
print(f"Size: {p1.size()}")
print(f"Is empty: {p1.is_empty()}")
```

### Arithmetic Operations

```python
# Combine progressions
combined = p1 + p2

# Remove items
result = p1 - ["item1", "item2"]

# In-place operations
p1 += ["new_item1", "new_item2"]
p1 -= ["item_to_remove"]
```

## Best Practices

1. Use the `prog` helper function for quick Progression creation.
2. Prefer `include` and `exclude` methods over direct list manipulation for better type safety.
3. Use `validate_order` when working with external data to ensure valid Lion IDs.
4. Leverage the arithmetic operations for efficient Progression manipulation.
5. Use the `name` attribute to give semantic meaning to your Progressions.

## Notes

- The `Progression` class uses `validate_order` to ensure all items are valid Lion IDs.
- The class supports both integer indexing and slicing for flexible item access.
- Arithmetic operations create new Progression instances, while in-place operations (`+=`, `-=`) modify the existing instance.
- The `extend` method specifically requires another `Progression` instance, enforcing type safety.
