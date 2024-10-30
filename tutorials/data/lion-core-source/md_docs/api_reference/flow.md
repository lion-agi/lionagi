# Flow API Documentation

## Overview

The `Flow` class is a flexible container for managing multiple progressions in the Lion framework. It provides a rich set of methods for manipulating and accessing ordered sequences, making it ideal for managing complex workflows or ordered data structures.

## Class Definition

```python
class Flow(Element):
    """A container for managing multiple progressions."""
```

## Attributes

- `progressions: Pile[Progression]` - A Pile containing the Progression objects.
- `registry: dict` - A dictionary mapping names to Progression IDs.
- `default_name: str | None` - The default name for unnamed progressions.

## Constructor

```python
def __init__(self, progressions=None, default_name=None):
```

Initialize a Flow instance with optional initial progressions and a default name.

## Methods

### Progression Management

#### `register`

```python
def register(self, prog_: Progression, name: str = None):
```

Register a new Progression in the Flow.

#### `include`

```python
def include(self, prog_=None, item=None, name=None):
```

Include a Progression or item in the Flow.

#### `exclude`

```python
def exclude(self, seq=None, item=None, name=None):
```

Exclude a Progression or item from the Flow.

#### `append`

```python
def append(self, item, prog_=None, /):
```

Append an item to a Progression in the Flow.

#### `popleft`

```python
def popleft(self, prog_=None, /):
```

Remove and return the leftmost item from a Progression.

### Data Access

#### `get`

```python
def get(self, prog_=None, default=LN_UNDEFINED) -> deque[str] | None:
```

Get a Progression by name or ID.

#### `__getitem__`

```python
def __getitem__(self, prog_=None, default=LN_UNDEFINED):
```

Get a Progression by name or ID (alias for `get`).

#### `__setitem__`

```python
def __setitem__(self, prog_, index=None, value=None, /):
```

Set a value in a Progression or replace an entire Progression.

#### `keys`

```python
def keys(self):
```

Yield the keys (names) of all Progressions.

#### `values`

```python
def values(self):
```

Yield the Progression objects.

#### `items`

```python
def items(self):
```

Yield (key, Progression) pairs.

### Information Retrieval

#### `all_orders`

```python
def all_orders(self) -> list[list[str]]:
```

Get all Progression orders as a list of lists.

#### `unique`

```python
def unique(self) -> list[str]:
```

Get a list of unique items across all Progressions.

#### `shape`

```python
def shape(self):
```

Get the shape of the Flow (number of Progressions and their lengths).

#### `size`

```python
def size(self):
```

Get the total number of items across all Progressions.

### Modification

#### `clear`

```python
def clear(self):
```

Clear all Progressions and the registry.

#### `remove`

```python
def remove(self, item, prog_="all"):
```

Remove an item from one or all Progressions.

### Conversion and Representation

#### `to_dict`

```python
def to_dict(self):
```

Convert the Flow to a dictionary representation.

#### `from_dict`

```python
@classmethod
def from_dict(cls, data):
```

Create a Flow instance from a dictionary.

### Container Operations

#### `__contains__`

```python
def __contains__(self, item):
```

Check if an item is in any Progression or in the registry.

#### `__len__`

```python
def __len__(self):
```

Return the number of Progressions in the Flow.

#### `__iter__`

```python
def __iter__(self):
```

Return an iterator over the Progressions.

#### `__next__`

```python
def __next__(self):
```

Return the next Progression in the Flow.

## Usage Examples

### Creating a Flow

```python
from lion_core.generic.flow import Flow, flow
from lion_core.generic.progression import Progression, prog

# Create a Flow instance
my_flow = Flow()

# Use the flow helper function
another_flow = flow(default_name="main_sequence")

# Create and add Progressions
prog1 = prog(["item1", "item2", "item3"], name="sequence1")
prog2 = prog(["itemA", "itemB", "itemC"], name="sequence2")

my_flow.register(prog1)
my_flow.register(prog2)
```

### Managing Progressions and Items

```python
# Include items
my_flow.include(item="new_item", name="sequence1")
my_flow.append("another_item", "sequence2")

# Exclude items
my_flow.exclude(item="item2", name="sequence1")

# Access Progressions
seq1 = my_flow.get("sequence1")
seq2 = my_flow["sequence2"]

# Modify Progressions
my_flow["sequence1", 0] = "modified_item"

# Remove items
removed_item = my_flow.popleft("sequence1")
```

### Iteration and Information Retrieval

```python
# Iterate over Progressions
for progression in my_flow:
    print(progression)

# Get all orders
all_orders = my_flow.all_orders()

# Get unique items
unique_items = my_flow.unique()

# Get Flow shape
flow_shape = my_flow.shape()

# Get total size
total_items = my_flow.size()
```

### Conversion and Serialization

```python
# Convert to dictionary
flow_dict = my_flow.to_dict()

# Create from dictionary
new_flow = Flow.from_dict(flow_dict)
```

## Best Practices

1. Use meaningful names for Progressions when registering them in the Flow.
2. Utilize the `default_name` parameter to simplify working with unnamed Progressions.
3. Use the `include` and `exclude` methods for safe item manipulation across Progressions.
4. When working with multiple Progressions, use the `all_orders()` and `unique()` methods to get a comprehensive view of the Flow's content.
5. Use type hints when working with Flows to improve code readability and catch potential type errors early.
6. When subclassing `Flow`, ensure to properly handle the `progressions` and `registry` attributes to maintain the class's functionality.

## Notes

- The `Flow` class is designed to manage multiple `Progression` objects, each representing an ordered sequence of items.
- The `registry` attribute maps names to Progression IDs, allowing for easy access to specific Progressions.
- When adding items without specifying a Progression, the `default_name` is used if set.
- The `shape()` method provides a quick overview of the Flow's structure, returning the number of Progressions and their individual lengths.
- The `LN_UNDEFINED` constant is used to distinguish between explicitly set `None` values and missing values in the `get` method.
