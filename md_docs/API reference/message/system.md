
### Class: `System`

**Description**:
`System` is a class representing a system message with system-related information. It inherits from `RoledMessage` and provides methods to manage system-specific content.

#### Attributes:
- `system` (str | Any | None): The system information.

### Method: `__init__`

**Signature**:
```python
def __init__(system=None, sender=None, recipient=None, **kwargs):
```

**Parameters**:
- `system` (str or Any, optional): The system information.
- `sender` (str, optional): The sender of the message.
- `recipient` (str, optional): The recipient of the message.
- `**kwargs`: Additional fields to be added to the message content, must be JSON serializable.

**Description**:
Initializes the `System` message with the provided system information, sender, and recipient.

**Usage Examples**:
```python
system_message = System(system="System update", sender="system_admin", recipient="all_users")
print(system_message)
```

### Method: `system_info`

**Signature**:
```python
@property
def system_info() -> Any:
```

**Return Values**:
- `Any`: The system information stored in the message content.

**Description**:
Retrieves the system information stored in the message content.

**Usage Examples**:
```python
system_message = System(system={"version": "1.0.1", "status": "active"})
print(system_message.system_info)  # Output: {'version': '1.0.1', 'status': 'active'}
```

### Method: `clone`

**Signature**:
```python
def clone(**kwargs) -> System:
```

**Parameters**:
- `**kwargs`: Optional keyword arguments to be included in the cloned object.

**Return Values**:
- `System`: A new instance of the object with the same content and additional keyword arguments.

**Description**:
Creates a copy of the current `System` object with optional additional arguments. This method clones the current object, preserving its content. It also retains the original metadata, while allowing for the addition of new attributes through keyword arguments.

**Usage Examples**:
```python
system_message = System(system="System update")
cloned_message = system_message.clone(sender="new_system_admin")
print(cloned_message)
```
