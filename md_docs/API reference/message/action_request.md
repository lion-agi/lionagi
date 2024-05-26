
### Class: `ActionRequest`

**Description**:
`ActionRequest` represents a request for an action with a function and its arguments. It inherits from `RoledMessage` and provides attributes specific to action requests.

#### Attributes:
- `function` (str): The name of the function to be called.
- `arguments` (dict): The keyword arguments to be passed to the function.
- `action_response` (str): The ID of the action response that this request corresponds to.

### Method: `__init__`

**Signature**:
```python
def __init__(
    self,
    function=None,
    arguments=None,
    sender=None,
    recipient=None,
    **kwargs,
)
```

**Parameters**:
- `function` (str or function, optional): The function to be called.
- `arguments` (dict, optional): The keyword arguments for the function.
- `sender` (str, optional): The sender of the request.
- `recipient` (str, optional): The recipient of the request.

**Description**:
Initializes an `ActionRequest` instance with the specified function, arguments, sender, and recipient. Converts the function to its name if it is a function object and prepares the arguments.

**Usage Examples**:
```python
action_request = ActionRequest(
    function="example_function",
    arguments={"param1": 10, "param2": "value"},
    sender="assistant_1",
    recipient="component_1"
)
print(action_request.function)  # Output: example_function
print(action_request.arguments)  # Output: {'param1': 10, 'param2': 'value'}
```

### Method: `is_responded`

**Signature**:
```python
def is_responded() -> bool:
```

**Return Values**:
- `bool`: True if the action request has a response, otherwise False.

**Description**:
Checks if the action request has been responded to by verifying if `action_response` is not `None`.

**Usage Examples**:
```python
if action_request.is_responded():
    print("The action request has been responded to.")
else:
    print("The action request has not been responded to.")
```

### Method: `clone`

**Signature**:
```python
def clone(**kwargs) -> ActionRequest:
```

**Parameters**:
- `**kwargs`: Optional keyword arguments to be included in the cloned object.

**Return Values**:
- `ActionRequest`: A new instance of the object with the same function, arguments, and additional keyword arguments.

**Description**:
Creates a copy of the current `ActionRequest` object with optional additional arguments. The method clones the current object, preserving its function and arguments, and retains the original `action_response` and metadata.

**Usage Examples**:
```python
new_request = action_request.clone(sender="assistant_2")
print(new_request.sender)  # Output: assistant_2
```

### Function: `_prepare_arguments`

**Signature**:
```python
def _prepare_arguments(arguments) -> dict:
```

**Parameters**:
- `arguments` (Any): The arguments to be prepared.

**Return Values**:
- `dict`: The prepared arguments.

**Description**:
Prepares the arguments for the action request. Converts the arguments to a dictionary if necessary.

**Usage Examples**:
```python
args = _prepare_arguments('{"param1": 10, "param2": "value"}')
print(args)  # Output: {'param1': 10, 'param2': 'value'}
```

**Exceptions Raised**:
- `ValueError`: If the arguments are invalid.
