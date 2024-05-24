
### Class: `Exchange`

**Description**:
`Exchange` is an item exchange system designed to handle incoming and outgoing flows of items. It extends the `Element` class and uses generics to allow for type-specific item management.

#### Attributes:
- `pile` (Pile[T]): The pile of items in the exchange.
- `pending_ins` (dict[str, Progression]): The pending incoming items to the exchange.
- `pending_outs` (Progression): The progression of pending outgoing items.

### Method: `__contains__`

**Signature**:
```python
def __contains__(self, item) -> bool:
```

**Parameters**:
- `item`: The item to check.

**Return Values**:
- `bool`: True if the item is in the pile, False otherwise.

**Description**:
Checks if an item is in the pile.

**Usage Examples**:
```python
if item in exchange:
    print("Item is in the exchange")
```

### Method: `senders`

**Signature**:
```python
@property
def senders() -> list[str]:
```

**Return Values**:
- `list[str]`: The list of sender IDs.

**Description**:
Gets the list of senders for the pending incoming items.

**Usage Examples**:
```python
senders = exchange.senders
print(senders)
```

### Method: `exclude`

**Signature**:
```python
def exclude(self, item) -> bool:
```

**Parameters**:
- `item`: The item to exclude.

**Return Values**:
- `bool`: True if the item was successfully excluded, False otherwise.

**Description**:
Excludes an item from the exchange.

**Usage Examples**:
```python
success = exchange.exclude(item)
print("Item excluded:", success)
```

### Method: `include`

**Signature**:
```python
def include(self, item, direction: str) -> bool:
```

**Parameters**:
- `item`: The item to include.
- `direction` (str): The direction to include the item ('in' or 'out').

**Return Values**:
- `bool`: True if the item was successfully included, False otherwise.

**Description**:
Includes an item in the exchange in a specified direction.

**Usage Examples**:
```python
success = exchange.include(item, "in")
print("Item included in:", success)

success = exchange.include(item, "out")
print("Item included out:", success)
```

### Method: `_include`

**Signature**:
```python
def _include(self, item: Sendable, direction: str) -> bool:
```

**Parameters**:
- `item` (Sendable): The item to include.
- `direction` (str): The direction to include the item ('in' or 'out').

**Return Values**:
- `bool`: True if the item was successfully included, False otherwise.

**Description**:
Helper method to include an item in the exchange in a specified direction.

**Usage Examples**:
```python
success = exchange._include(item, "in")
print("Item included in:", success)

success = exchange._include(item, "out")
print("Item included out:", success)
```

### Method: `to_dict`

**Signature**:
```python
def to_dict() -> dict:
```

**Return Values**:
- `dict`: The dictionary representation of the exchange.

**Description**:
Converts the exchange to a dictionary.

**Usage Examples**:
```python
exchange_dict = exchange.to_dict()
print(exchange_dict)
```

### Method: `__bool__`

**Signature**:
```python
def __bool__() -> bool:
```

**Return Values**:
- `bool`: Always returns `True`.

**Description**:
Returns `True` when the exchange instance is evaluated as a boolean.

**Usage Examples**:
```python
if exchange:
    print("Exchange is valid")
```
