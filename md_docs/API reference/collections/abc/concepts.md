
### Class: `Record`

**Description**:
`Record` is an abstract base class for managing a collection of unique LionAGI items. It accepts `LionIDable` for retrieval and requires `Component` instances for addition.

#### Methods:

### Method: `keys`

**Signature**:
```python
@abstractmethod
def keys() -> Generator[str, None, None]:
```

**Return Values**:
- `Generator[str, None, None]`: An iterator over the `ln_id` of items in the record.

**Description**:
Returns an iterator over the `ln_id` of items in the record.

**Usage Examples**:
```python
for key in record.keys():
    print(key)
```

### Method: `values`

**Signature**:
```python
@abstractmethod
def values() -> Generator[T, None, None]:
```

**Return Values**:
- `Generator[T, None, None]`: An iterator over items in the record.

**Description**:
Returns an iterator over items in the record.

**Usage Examples**:
```python
for value in record.values():
    print(value)
```

### Method: `get`

**Signature**:
```python
@abstractmethod
def get(item: LionIDable, /, default: Any = None) -> T:
```

**Parameters**:
- `item` (LionIDable): The identifier of the item to retrieve.
- `default` (Any, optional): The default value to return if the item is not found. Defaults to `None`.

**Return Values**:
- `T`: The retrieved item or the default value.

**Description**:
Retrieves an item by identifier. Accepts a `LionIDable` object. Returns the default if the item is not found.

**Usage Examples**:
```python
item = record.get(item_id, default=None)
```

### Method: `__getitem__`

**Signature**:
```python
@abstractmethod
def __getitem__(item: LionIDable) -> T:
```

**Parameters**:
- `item` (LionIDable): The identifier of the item to retrieve.

**Return Values**:
- `T`: The retrieved item.

**Exceptions Raised**:
- `KeyError`: If the item ID is not found.

**Description**:
Returns an item using a `LionIDable` identifier.

**Usage Examples**:
```python
item = record[item_id]
```

### Method: `__setitem__`

**Signature**:
```python
@abstractmethod
def __setitem__(item: LionIDable, value: T) -> None:
```

**Parameters**:
- `item` (LionIDable): The identifier of the item to add or update.
- `value` (T): The `Component` instance to add or update.

**Return Values**:
- `None`

**Description**:
Adds or updates an item in the record. The value must be a `Component` instance.

**Usage Examples**:
```python
record[item_id] = component_instance
```

### Method: `__contains__`

**Signature**:
```python
@abstractmethod
def __contains__(item: LionIDable) -> bool:
```

**Parameters**:
- `item` (LionIDable): The identifier or object to check.

**Return Values**:
- `bool`: True if the item is in the record, False otherwise.

**Description**:
Checks if an item is in the record, using either an ID or an object.

**Usage Examples**:
```python
if item_id in record:
    print("Item is in the record")
```

### Method: `__len__`

**Signature**:
```python
@abstractmethod
def __len__() -> int:
```

**Return Values**:
- `int`: The number of items in the record.

**Description**:
Returns the number of items in the record.

**Usage Examples**:
```python
print(len(record))
```

### Method: `__iter__`

**Signature**:
```python
@abstractmethod
def __iter__() -> Iterator[T]:
```

**Return Values**:
- `Iterator[T]`: The items in the record.

**Description**:
Iterates over items in the record.

**Usage Examples**:
```python
for item in record:
    print(item)
```

---

### Class: `Ordering`

**Description**:
`Ordering` represents the sequencing of certain orders.

#### Methods:

### Method: `__len__`

**Signature**:
```python
@abstractmethod
def __len__() -> int:
```

**Return Values**:
- `int`: The number of item ids in the ordering.

**Description**:
Returns the number of item ids in the ordering or the number of orderings in another ordering.

**Usage Examples**:
```python
print(len(ordering))
```

### Method: `__contains__`

**Signature**:
```python
@abstractmethod
def __contains__(item: Any) -> bool:
```

**Parameters**:
- `item` (Any): The item id to check.

**Return Values**:
- `bool`: True if the item id is in the ordering, False otherwise.

**Description**:
Checks if an item id is in the ordering.

**Usage Examples**:
```python
if item_id in ordering:
    print("Item is in the ordering")
```

---

### Class: `Condition`

**Description**:
`Condition` represents a condition in a given context.

#### Methods:

### Method: `applies`

**Signature**:
```python
@abstractmethod
async def applies(self, value: Any, /, *args: Any, **kwargs: Any) -> Any:
```

**Parameters**:
- `value` (Any): The value to check against the condition.
- `*args` (Any): Additional positional arguments.
- `**kwargs` (Any): Additional keyword arguments.

**Return Values**:
- `Any`: The result of applying the condition to the value.

**Description**:
Asynchronously determines if the condition applies to the given value.

**Usage Examples**:
```python
result = await condition.applies(value)
```

---

### Class: `Actionable`

**Description**:
`Actionable` represents an action that can be invoked with arguments.

#### Methods:

### Method: `invoke`

**Signature**:
```python
@abstractmethod
async def invoke(self, /, *args: Any, **kwargs: Any) -> Any:
```

**Parameters**:
- `*args` (Any): Positional arguments for invoking the action.
- `**kwargs` (Any): Keyword arguments for invoking the action.

**Return Values**:
- `Any`: The result of invoking the action.

**Description**:
Invokes the action asynchronously with the given arguments.

**Usage Examples**:
```python
result = await actionable.invoke(arg1, arg2, key=value)
```

---

### Class: `Progressable`

**Description**:
`Progressable` represents a process that can progress forward asynchronously.

#### Methods:

### Method: `forward`

**Signature**:
```python
@abstractmethod
async def forward(self, /, *args: Any, **kwargs: Any) -> None:
```

**Parameters**:
- `*args` (Any): Positional arguments for moving the process forward.
- `**kwargs` (Any): Keyword arguments for moving the process forward.

**Return Values**:
- `None`

**Description**:
Moves the process forward asynchronously.

**Usage Examples**:
```python
await progressable.forward()
```

---

### Class: `Relatable`

**Description**:
`Relatable` defines a relationship that can be established with arguments.

#### Methods:

### Method: `relate`

**Signature**:
```python
@abstractmethod
def relate(self, /, *args: Any, **kwargs: Any) -> None:
```

**Parameters**:
- `*args` (Any): Positional arguments for establishing the relationship.
- `**kwargs` (Any): Keyword arguments for establishing the relationship.

**Return Values**:
- `None`

**Description**:
Establishes a relationship based on the provided arguments.

**Usage Examples**:
```python
relatable.relate(arg1, arg2, key=value)
```

---

### Class: `Sendable`

**Description**:
`Sendable` represents an object that can be sent with a sender and recipient.

#### Attributes:
- `sender` (str): The ID of the sender node, or 'system', 'user', or 'assistant'.
- `recipient` (str): The ID of the recipient node, or 'system', 'user', or 'assistant'.

### Method: `_validate_sender_recipient`

**Signature**:
```python
@field_validator("sender", "recipient", mode="before")
def _validate_sender_recipient(cls, value):
```

**Parameters**:
- `value` (Any): The value to validate.

**Return Values**:
- `str`: The validated value.

**Exceptions Raised**:
- `LionTypeError`: If the value is invalid.

**Description**:
Validates the sender and recipient fields.

**Usage Examples**:
```python
# Example usage of Sendable class
sendable_instance = Sendable(sender="user", recipient="assistant")
```

---

### Class: `Executable`

**Description**:
`Executable` represents an object that can be executed with arguments.

#### Methods:

### Method: `execute`

**Signature**:
```python
@abstractmethod
async def execute(self, /, *args: Any, **kwargs: Any) -> Any:
```

**Parameters**:
- `*args` (Any): Positional arguments for executing the object.
- `**kwargs` (Any): Keyword arguments for executing

 the object.

**Return Values**:
- `Any`: The result of executing the object.

**Description**:
Executes the object with the given arguments asynchronously.

**Usage Examples**:
```python
result = await executable.execute(arg1, arg2, key=value)
```

---

### Class: `Directive`

**Description**:
`Directive` represents a directive that can be directed with arguments.

#### Methods:

### Method: `class_name`

**Signature**:
```python
@property
def class_name() -> str
```

**Return Values**:
- `str`: The class name of the directive.

**Description**:
Gets the class name of the directive.

**Usage Examples**:
```python
directive_class_name = directive.class_name
```

### Method: `_class_name`

**Signature**:
```python
@classmethod
def _class_name(cls) -> str
```

**Return Values**:
- `str`: The class name of the directive.

**Description**:
Gets the class name of the directive.

**Usage Examples**:
```python
class_name = Directive._class_name()
```
