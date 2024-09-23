
## Class: `Flow`

**Parent Class: [[#^bb802e|Element]]

**Description**:
`Flow` represents a flow of categorical sequences. It extends the `Element` class and provides methods to manage a collection of progression sequences.

Attributes:
- `sequences` ([[Pile#^0206c8|Pile]]): A collection of progression sequences.
- `registry` `(dict[str, str])`: A registry mapping sequence names to IDs.
- `default_name` (str): The default name for the flow.

### `__init__`

**Signature**:
```python
def __init__(self, sequences=None, default_name=None)
```

**Parameters**:
- `sequences` (optional): Initial sequences to include in the flow.
- `default_name` (optional): Default name for the flow.

**Usage Examples**:
```python
# Example 1: Create a Flow with default parameters
flow_instance = Flow()

# Example 2: Create a Flow with specified sequences and default name
flow_instance = Flow(sequences=my_sequences, default_name="custom_name")
```

### `all_orders`

**Signature**:
```python
def all_orders() -> list[list[str]]
```

**Return Values**:
- `list[list[str]]`: A list of lists containing sequence orders.

**Description**:
Retrieves all orders in the flow.

**Usage Examples**:
```python
# Example: Get all orders in the flow
orders = flow_instance.all_orders()
print(orders)
```

### `all_unique_items`

**Signature**:
```python
def all_unique_items() -> Tuple[str]
```

**Return Values**:
- `Tuple[str]`: A tuple of unique items.

**Description**:
Retrieves all unique items across sequences.

**Usage Examples**:
```python
# Example: Get all unique items across sequences
unique_items = flow_instance.all_unique_items()
print(unique_items)
```

### `keys`

**Signature**:
```python
def keys() -> Generator[str, None, None]
```

**Return Values**:
- `Generator[str, None, None]`: An iterator over the sequence keys.

**Description**:
Returns an iterator over the sequence keys.

**Usage Examples**:
```python
# Example: Iterate over sequence keys
for key in flow_instance.keys():
    print(key)
```

### `values`

**Signature**:
```python
def values() -> Generator[Progression, None, None]
```

**Return Values**:
- `Generator[Progression, None, None]`: An iterator over the sequence values.

**Description**:
Returns an iterator over the sequence values.

**Usage Examples**:
```python
# Example: Iterate over sequence values
for value in flow_instance.values():
    print(value)
```

### `items`

**Signature**:
```python
def items() -> Generator[Tuple[str, Progression], None, None]
```

**Return Values**:
- `Generator[Tuple[str, Progression], None, None]`: An iterator over the sequence items.

**Description**:
Returns an iterator over the sequence items.

**Usage Examples**:
```python
# Example: Iterate over sequence items
for item in flow_instance.items():
    print(item)
```

### `get`

**Signature**:
```python
def get(self, seq=None, default=...) -> Progression
```

**Parameters**:
- `seq` (optional): The name of the sequence.
- `default` (optional): Default value if sequence is not found.

**Return Values**:
- `Progression`: The requested sequence.

**Exceptions Raised**:
- `ItemNotFoundError`: If no sequence is found.
- `LionTypeError`: If the sequence is not of type Progression.

**Description**:
Retrieves a sequence by name or returns the default sequence.

**Usage Examples**:
```python
# Example: Get a sequence by name
sequence = flow_instance.get("sequence_name")

# Example: Get the default sequence
default_sequence = flow_instance.get()
```

### `__getitem__`

**Signature**:
```python
def __getitem__(self, seq=None) -> Progression
```

**Parameters**:
- `seq` (optional): The name of the sequence.

**Return Values**:
- `Progression`: The requested sequence.

**Description**:
Returns the sequence specified by `seq`.

**Usage Examples**:
```python
# Example: Get a sequence using indexing
sequence = flow_instance["sequence_name"]
```

### `__setitem__`

**Signature**:
```python
def __setitem__(self, seq, index=None, value=None)
```

**Parameters**:
- `seq` ( | str): The name of the sequence.
- `index` (optional): The index within the sequence.
- `value` (optional): The value to set at the specified index.

**Return Values**:
- `None`

**Exceptions Raised**:
- `ItemNotFoundError`: If the sequence is not found.

**Description**:
Adds or updates an item in the specified sequence.

**Usage Examples**:
```python
# Example: Set an item in a sequence
flow_instance["sequence_name"] = new_value
```

### `__contains__`

**Signature**:
```python
def __contains__(self, item) -> bool
```

**Parameters**:
- `item`: The item to check.

**Return Values**:
- `bool`: True if the item is in the flow, False otherwise.

**Description**:
Checks if an item is in the flow.

**Usage Examples**:
```python
# Example: Check if an item is in the flow
if "item_name" in flow_instance:
    print("Item is in the flow")
```

### `shape`

**Signature**:
```python
def shape() -> dict
```

**Return Values**:
- `dict`: A dictionary representing the shape of the flow.

**Description**:
Returns the shape of the flow, including the length of each sequence.

**Usage Examples**:
```python
# Example: Get the shape of the flow
shape = flow_instance.shape()
print(shape)
```

### `size`

**Signature**:
```python
def size() -> int
```

**Return Values**:
- `int`: The total number of items in all sequences.

**Description**:
Returns the total number of items in all sequences.

**Usage Examples**:
```python
# Example: Get the size of the flow
size = flow_instance.size()
print(size)
```

### `clear`

**Signature**:
```python
def clear() -> None
```

**Return Values**:
- `None`

**Description**:
Clears all sequences and the registry.

**Usage Examples**:
```python
# Example: Clear the flow
flow_instance.clear()
```

### `include`

**Signature**:
```python
def include(self, seq=None, item=None, name=None) -> bool
```

**Parameters**:
- `seq` (optional): The sequence to include.
- `item` (optional): The item to include.
- `name` (optional): The name of the sequence.

**Return Values**:
- `bool`: True if the inclusion was successful, False otherwise.

**Description**:
Includes a sequence or item in the flow.

**Usage Examples**:
```python
# Example: Include an item in the flow
success = flow_instance.include(seq="sequence_name", item="item_name")
print(success)
```

### `exclude`

**Signature**:
```python
def exclude(self, seq = None, item=None, name=None) -> bool
```

**Parameters**:
- `seq` (, optional): The sequence to exclude from.
- `item` (optional): The item to exclude.
- `name` (optional): The name of the sequence.

**Return Values**:
- `bool`: True if the exclusion was successful, False otherwise.

**Description**:
Excludes an item or sequence from the flow.

**Usage Examples**:
```python
# Example: Exclude an item from the flow
success = flow_instance.exclude(seq="sequence_name", item="item_name")
print(success)
```

### `register`

**Signature**:
```python
def register(self, sequence: Progression, name: str = None) -> None
```

**Parameters**:
- `sequence` (Progression): The sequence to register.
- `name` (str, optional): The name for the sequence.

**Return Values**:
- `None`

**Exceptions Raised**:
- `LionTypeError`: If the sequence is not of type Progression.
- `ValueError`: If the sequence name already exists.

**Description**:
Registers a sequence with a name.

**Usage Examples**:
```python
# Example: Register a sequence
flow_instance.register(my_sequence, "sequence_name")
```

### `append`

**Signature**:
```python
def append(self, item, sequence=None) -> None
```

**Parameters**:
- `item`: The item to append.
- `sequence` (optional): The sequence to append to.

**Return Values**: `None` 

**Description**:
Appends an item to a sequence.

**Usage Examples**:
```python
# Example: Append an item to a sequence
flow_instance.append("item_name", "sequence_name")
```

### `popleft`

**Signature**:
```python
def popleft(self, sequence=None)
```

**Parameters**:
- `sequence` (optional): The sequence to remove the item from.

**Return Values**:
- The removed item.

**Description**:
Removes and returns an item from the left end of a sequence.

**Usage Examples**:
```python
# Example: Remove an item from the left end of a sequence
item = flow_instance.popleft("sequence_name")
print(item)
```

### `remove`

**Signature**:
```python
def remove(self, item, sequence="all") -> None
```

**Parameters**:
- `item`: The item to remove.
- `sequence` (str, optional): The sequence to remove the item from. Defaults to "all".

**Return Values**:
- `None`

**Description**:
Removes an item from a sequence or all sequences.

**Usage Examples**:
```python
# Example: Remove an item from a specific sequence
flow_instance.remove("item_name", "sequence_name")

# Example: Remove an item from all sequences
flow_instance.remove("item_name")
```

### `__len__`

**Signature**:
```python
def __len__() -> int
```

**Return Values**:
- `int`: The number of sequences.

**Description**:
Returns the number of sequences.

**Usage Examples**:
```python
# Example: Get the number of sequences in the flow
length = len(flow_instance)
print(length)
```

### `__iter__`

**Signature**:
```python
def __iter__() -> Iterator[Progression]
```

**Return Values**:
- `Iterator[Progression]`: An iterator over the sequences.

**Description**:
Iterates over the sequences in the flow.

**Usage Examples**:
```python
# Example: Iterate over the sequences in the flow
for sequence in flow_instance:
    print(sequence)
```

### `__next__`

**Signature**:
```python
def __next__() -> Progression
```

**Return Values**:
- `Progression`: The next sequence.

**Description**:
Returns the next sequence in the flow.

**Usage Examples**:
```python
# Example: Get the next sequence in the flow
sequence = next(flow_instance)
print(sequence)
```

### `to_df`

**Signature**:
```python
def to_df() -> Any
```

**Return Values**:
- `Any`: A DataFrame representation of the sequences.

**Description**:
Converts the sequences to a DataFrame.

**Usage Examples**:
```python
# Example: Convert sequences to a DataFrame
df = flow_instance.to_df()
print(df)
```

## Function: `flow`

**Signature**:
```python
def flow(sequences=None, default_name=None) -> Flow
```

**Parameters**:
- `sequences` (optional): Initial sequences to include in the flow.
- `default_name` (optional): Default name for the flow.

**Return Values**:
- `Flow`: A new Flow instance.

**Description**:
Creates a new Flow instance.

**Usage Examples**:
```python
# Example: Create a new Flow instance with default parameters
new_flow = flow()

# Example: Create a new Flow instance with specified sequences and default name
new_flow = flow(sequences=my_sequences, default_name="custom_name")
```
