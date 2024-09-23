
## Class: `Edge`

**Parent Class:** [[Component#^ce462d|Component]]

^a9ad22

**Description**:
`Edge` represents a directed edge between two nodes in a graph. It extends the `Component` class and includes attributes for the head and tail nodes, an optional condition, a label, and a bundle flag. The class also provides methods to check conditions and retrieve the source code of the condition class.

Attributes:

- `head` (str): The identifier of the head node of the edge.
- `tail` (str): The identifier of the tail node of the edge.
- `condition` ([[API reference/collections/abc/Concepts#^d5e7b6|Condition]] | [[Edge Condition#^c25416|EdgeCondition]] | None): Optional condition that must be met for the edge to be considered active.
- `label` (str | None): An optional label for the edge.
- `bundle` (bool): A flag indicating if the edge is bundled.

### `check_condition`

**Signature**:
```python
async def check_condition(self, obj: Any) -> bool:
```

**Parameters**:
- `obj` (Any): The object to check the condition against.

**Return Values**:
- `bool`: True if the condition is met, False otherwise.

**Exceptions Raised**:
- `ValueError`: If the condition for the edge is not set.

**Description**:
Checks if the edge condition is met for the given object.

**Usage Examples**:
```python
edge = Edge(head='node1', tail='node2', condition=my_condition)
result = await edge.check_condition(some_object)
print(result)  # Output: True or False based on the condition
```

### `string_condition`

**Signature**:
```python
def string_condition() -> str | None:
```

**Return Values**:
- `str | None`: The condition class source code if available. None if the condition is not set or the source code cannot be located.

**Exceptions Raised**:
- `TypeError`: If the condition class source code cannot be found due to the class being defined in a non-standard manner or in the interactive interpreter.

**Description**:
Retrieves the condition class source code as a string. This method is useful for serialization and debugging, allowing the condition logic to be inspected or stored in a human-readable format.

**Usage Examples**:
```python
source_code = edge.string_condition()
print(source_code)
```

### `__len__`

**Signature**:
```python
def __len__() -> int:
```

**Return Values**:
- `int`: Always returns 1.

**Description**:
Returns the length of the edge, which is always 1.

**Usage Examples**:
```python
length = len(edge)
print(length)  # Output: 1
```

### `__contains__`

**Signature**:
```python
def __contains__(self, item) -> bool:
```

**Parameters**:
- `item` (): The item to check.

**Return Values**:
- `bool`: True if the item is the head or tail of the edge, False otherwise.

**Description**:
Checks if the given item is the head or tail of the edge.

**Usage Examples**:
```python
item_in_edge = item in edge
print(item_in_edge)  # Output: True or False
```
