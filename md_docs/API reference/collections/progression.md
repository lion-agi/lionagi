
### Class: `Progression`

^166cef

**Parent Class: [[#^bb802e|Element]]

**Description**:
`Progression` is a class representing an ordered sequence of elements. It extends the `Element` and `Ordering` classes and provides functionalities for managing, manipulating, and querying sequences.

**Attributes**:
- `name` (str | None): The name of the progression.
- `order` (list): The order of the progression.

### `__contains__`

**Signature**:
```python
def __contains__(self, item) -> bool
```

**Parameters**:
- `item`: The item or items to check for in the progression. Can be a single item, list of items, or another `Progression`.

**Return Values**:
- `bool`: `True` if the item or items are in the progression, `False` otherwise.

**Description**:
Checks if an item or items are in the progression.

**Usage Examples**:
```python
# Example: Check if an item is in the progression
is_in = item in progression_instance
print("Item in progression:", is_in)
```

### `__len__`

**Signature**:
```python
def __len__() -> int
```

**Return Values**:
- `int`: The number of items in the progression.

**Description**:
Returns the number of items in the progression.

**Usage Examples**:
```python
# Example: Get the number of items in the progression
length = len(progression_instance)
print("Number of items:", length)
```

### `keys`

**Signature**:
```python
def keys() -> Iterator[int]
```

**Return Values**:
- `Iterator[int]`: An iterator over the indices of the progression.

**Description**:
Yields the keys (indices) of the items in the progression.

**Usage Examples**:
```python
# Example: Get the keys of the progression
keys = list(progression_instance.keys())
print("Keys:", keys)
```

### `values`

**Signature**:
```python
def values() -> Iterator[str]
```

**Return Values**:
- `Iterator[str]`: An iterator over the values of the progression.

**Description**:
Yields the values (item IDs) of the progression.

**Usage Examples**:
```python
# Example: Get the values of the progression
for value in progression_instance.values():
    print(value)
```

### `items`

**Signature**:
```python
def items() -> Iterator[tuple[int, str]]
```

**Return Values**:
- `Iterator[tuple[int, str]]`: An iterator over the items in the progression as (index, value) pairs.

**Description**:
Yields the items in the progression as (index, value) pairs.

**Usage Examples**:
```python
# Example: Get the items of the progression as (index, value) pairs
for index, value in progression_instance.items():
    print(index, value)
```

### `size`

**Signature**:
```python
def size() -> int
```

**Return Values**:
- `int`: The number of items in the progression.

**Description**:
Returns the number of items in the progression.

**Usage Examples**:
```python
# Example: Get the size of the progression
size = progression_instance.size()
print("Size of progression:", size)
```

### `copy`

**Signature**:
```python
def copy() -> "Progression"
```

**Return Values**:
- `Progression`: A deep copy of the progression.

**Description**:
Creates a deep copy of the progression.

**Usage Examples**:
```python
# Example: Create a copy of the progression
progression_copy = progression_instance.copy()
print("Copy of progression:", progression_copy)
```

### `append`

**Signature**:
```python
def append(self, item) -> None
```

**Parameters**:
- `item`: The item to append to the progression.

**Return Values**:
- `None`

**Description**:
Appends an item to the end of the progression.

**Usage Examples**:
```python
# Example: Append an item to the progression
progression_instance.append(new_item)
```

### `extend`

**Signature**:
```python
def extend(self, item) -> None
```

**Parameters**:
- `item`: The item or items to extend the progression with. Can be a single item, list of items, or another `Progression`.

**Return Values**:
- `None`

**Description**:
Extends the progression from the right with item(s).

**Usage Examples**:
```python
# Example: Extend the progression with multiple items
progression_instance.extend([item1, item2])
```

### `include`

**Signature**:
```python
def include(self, item) -> bool
```

**Parameters**:
- `item`: The item or items to include in the progression. Can be a single item, list of items, or another `Progression`.

**Return Values**:
- `bool`: `True` if the item or items are included, `False` otherwise.

**Description**:
Includes item(s) in the progression.

**Usage Examples**:
```python
# Example: Include an item in the progression
included = progression_instance.include(new_item)
print("Item included:", included)
```

### `__getitem__`

**Signature**:
```python
def __getitem__(self, key)
```

**Parameters**:
- `key`: The key to retrieve items. Can be an index or slice.

**Return Values**:
- The item(s) at the specified key.

**Exceptions Raised**:
- [[Exceptions#^ee9dbb|ItemNotFoundError]]: If the key is not found.

**Description**:
Retrieves items from the progression using a key.

**Usage Examples**:
```python
# Example: Get an item from the progression by index
item = progression_instance[0]
print("First item:", item)
```

### `remove`

**Signature**:
```python
def remove(self, item) -> None
```

**Parameters**:
- `item` (): The item to remove from the progression.

**Exceptions Raised**:
- [[Exceptions#^ee9dbb|ItemNotFoundError]]: If the item is not found.

**Description**:
Removes the next occurrence of an item from the progression.

**Usage Examples**:
```python
# Example: Remove an item from the progression
progression_instance.remove(item_to_remove)
```

### `__list__`

**Signature**:
```python
def __list__() -> list
```

**Return Values**:
- `list`: The items in the progression.

**Description**:
Returns a list of the items in the progression.

**Usage Examples**:
```python
# Example: Get a list of the items in the progression
items_list = progression_instance.__list__()
print(items_list)
```

### `popleft`

**Signature**:
```python
def popleft() -> Any
```

**Return Values**:
- The leftmost item from the progression.

**Exceptions Raised**:
- [[Exceptions#^ee9dbb|ItemNotFoundError]]: If the progression is empty.

**Description**:
Removes and returns the leftmost item from the progression.

**Usage Examples**:
```python
# Example: Remove and get the leftmost item from the progression
leftmost_item = progression_instance.popleft()
print("Leftmost item:", leftmost_item)
```

### `pop`

**Signature**:
```python
def pop(self, index=None) -> Any
```

**Parameters**:
- `index` (optional): The index of the item to pop. If not specified, pops the last item.

**Return Values**:
- The item at the specified index, or the last item if index is not specified.

**Exceptions Raised**:
- [[Exceptions#^ee9dbb|ItemNotFoundError]]: If the index is out of range.

**Description**:
Removes and returns an item from the progression.

**Usage Examples**:
```python
# Example: Pop an item from the progression
popped_item = progression_instance.pop()
print("Popped item:", popped_item)
```

### `exclude`

**Signature**:
```python
def exclude(self, item) -> bool
```

**Parameters**:
- `item`: The item or items to exclude from the progression. Can be a single item, list of items, or another `Progression`.

**Return Values**:
- `bool`: `True` if the item or items are excluded, `False` otherwise.

**Exceptions Raised**:
- `IndexError`: If the specified number of items to exclude is greater than the length of the progression.

**Description**:
Excludes an item or items from the progression.

**Usage Examples**:
```python
# Example: Exclude an item from the progression
excluded = progression_instance.exclude(item_to_exclude)
print("Item excluded:", excluded)
```

### `__add__`

**Signature**:
```python
def __add__(self, other) -> "Progression"
```

**Parameters**:
- `other`: The item or items to add to the end of the progression.

**Return Values**:
- `Progression`: A new `Progression` with the added item(s).

**Description**:
Adds an item or items to the end of the progression.

**Usage Examples**:
```python
# Example: Add items to the progression
new_progression = progression_instance + new_item
```

### `__radd__`

**Signature**:
```python
def __radd__(self, other) -> "Progression"
```

**Parameters**:
- `other`:

 The item or items to add to the beginning of the progression.

**Return Values**:
- `Progression`: A new `Progression` with the added item(s).

**Description**:
Adds an item or items to the beginning of the progression.

**Usage Examples**:
```python
# Example: Add items to the beginning of the progression
new_progression = new_item + progression_instance
```

### `__setitem__`

**Signature**:
```python
def __setitem__(self, key, value) -> None
```

**Parameters**:
- `key`: The key to set the value.
- `value`: The value to set at the specified key.

**Description**:
Sets new values in the progression using various key types.

**Usage Examples**:
```python
# Example: Set a new value at a specific index
progression_instance[0] = new_value
```

### `__iadd__`

**Signature**:
```python
def __iadd__(self, other) -> "Progression"
```

**Parameters**:
- `other`: The item or items to add to the end of the progression.

**Return Values**:
- `Progression`: The modified progression.

**Description**:
Adds an item or items to the end of the progression in place.

**Usage Examples**:
```python
# Example: Add items to the end of the progression in place
progression_instance += new_item
```

### `__isub__`

**Signature**:
```python
def __isub__(self, other) -> "Progression"
```

**Parameters**:
- `other`: The item or items to remove from the progression.

**Return Values**:
- `Progression`: The modified progression.

**Description**:
Removes an item or items from the progression in place.

**Usage Examples**:
```python
# Example: Remove items from the progression in place
progression_instance -= item_to_remove
```

### `__sub__`

**Signature**:
```python
def __sub__(self, other) -> "Progression"
```

**Parameters**:
- `other`: The item or items to remove from the progression.

**Return Values**:
- `Progression`: A new `Progression` with the removed item(s).

**Description**:
Removes an item or items from the progression.

**Usage Examples**:
```python
# Example: Remove items from the progression
new_progression = progression_instance - item_to_remove
```

### `__iter__`

**Signature**:
```python
def __iter__() -> Iterator
```

**Return Values**:
- `Iterator`: An iterator over the items in the progression.

**Description**:
Iterates over the items in the progression.

**Usage Examples**:
```python
# Example: Iterate over the items in the progression
for item in progression_instance:
    print(item)
```

### `__next__`

**Signature**:
```python
def __next__() -> Any
```

**Return Values**:
- The next item in the progression.

**Exceptions Raised**:
- `StopIteration`: If there are no more items.

**Description**:
Returns the next item in the progression.

**Usage Examples**:
```python
# Example: Get the next item in the progression
next_item = next(progression_instance)
print("Next item:", next_item)
```

### `__repr__`

**Signature**:
```python
def __repr__() -> str
```

**Return Values**:
- `str`: The string representation of the progression.

**Description**:
Returns a string representation of the progression.

**Usage Examples**:
```python
# Example: Get the string representation of the progression
print(repr(progression_instance))
```

### `__str__`

**Signature**:
```python
def __str__() -> str
```

**Return Values**:
- `str`: The string representation of the progression.

**Description**:
Returns a string representation of the progression.

**Usage Examples**:
```python
# Example: Get the string representation of the progression
print(str(progression_instance))
```

### `__reversed__`

**Signature**:
```python
def __reversed__() -> Iterator
```

**Return Values**:
- `Iterator`: An iterator over the reversed progression.

**Description**:
Returns a reversed iterator over the progression.

**Usage Examples**:
```python
# Example: Get a reversed iterator over the progression
for item in reversed(progression_instance):
    print(item)
```

### `clear`

**Signature**:
```python
def clear() -> None
```

**Return Values**:
- `None`

**Description**:
Clears the progression.

**Usage Examples**:
```python
# Example: Clear the progression
progression_instance.clear()
```

### `to_dict`

**Signature**:
```python
def to_dict() -> dict
```

**Return Values**:
- `dict`: A dictionary representation of the progression.

**Description**:
Returns a dictionary representation of the progression.

**Usage Examples**:
```python
# Example: Get a dictionary representation of the progression
progression_dict = progression_instance.to_dict()
print(progression_dict)
```

### `__bool__`

**Signature**:
```python
def __bool__() -> bool
```

**Return Values**:
- `bool`: `True`

**Description**:
Always returns `True` for `Progression` instances.

**Usage Examples**:
```python
# Example: Check if the progression is truthy
if progression_instance:
    print("Progression is truthy")
```

### Function: `progression`

**Signature**:
```python
def progression(order=None, name=None, /) -> Progression
```

**Parameters**:
- `order` (optional): The initial order of the progression.
- `name` (optional): The name of the progression.

**Return Values**:
- `Progression`: A new `Progression` instance.

**Description**:
Creates a new `Progression` instance.

**Usage Examples**:
```python
# Example: Create a new Progression instance
progression_instance = progression(order=[item1, item2], name="my_progression")
```
