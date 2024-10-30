
### Class: `ActionResponse`

**Parent Class:** [[Roled Message#^f41a31|RoledMessage]]

**Description**:
`ActionResponse` represents a response to a specific action request. It inherits from `RoledMessage` and provides attributes specific to action responses.

#### Attributes:
- `action_request` (str): The ID of the action request that this response corresponds to.
- `function` (str): The name of the function called.
- `arguments` (dict): The keyword arguments provided.
- `func_outputs` (Any): The output of the function call.

### `__init__`

**Signature**:
```python
def __init__(
    self,
    action_request: ActionRequest,
    sender: str | None = None,
    func_outputs=None,
    **kwargs,
)
```

**Parameters**:
- `action_request` (ActionRequest): The action request that this response corresponds to.
- `sender` (str, optional): The sender of the action request.
- `func_outputs` (Any, optional): The output of the function call.

**Raises**:
- `ValueError`: If the action request has already been responded to.

**Description**:
Initializes an `ActionResponse` instance with the specified action request, sender, and function outputs. Updates the action request to indicate it has been responded to.

**Usage Examples**:
```python
action_request = ActionRequest(
    function="example_function",
    arguments={"param1": 10, "param2": "value"},
    sender="assistant_1",
    recipient="component_1"
)

action_response = ActionResponse(
    action_request=action_request,
    sender="component_1",
    func_outputs="result"
)
print(action_response.function)  # Output: example_function
print(action_response.arguments)  # Output: {'param1': 10, 'param2': 'value'}
print(action_response.func_outputs)  # Output: result
```

### `update_request`

**Signature**:
```python
def update_request(action_request: ActionRequest):
```

**Parameters**:
- `action_request` (ActionRequest): The action request to update from.

**Description**:
Updates the action request details in the action response, including the function, arguments, and action request ID.

**Usage Examples**:
```python
action_response.update_request(action_request)
print(action_response.function)  # Output: example_function
```

### `_to_dict`

**Signature**:
```python
def _to_dict() -> dict:
```

**Return Values**:
- `dict`: A dictionary representation of the action response.

**Description**:
Converts the action response to a dictionary format.

**Usage Examples**:
```python
response_dict = action_response._to_dict()
print(response_dict)
# Output: {'function': 'example_function', 'arguments': {'param1': 10, 'param2': 'value'}, 'output': 'result'}
```

### `clone`

**Signature**:
```python
def clone(**kwargs) -> ActionResponse:
```

**Parameters**:
- `**kwargs`: Optional keyword arguments to be included in the cloned object.

**Return Values**:
- `ActionResponse`: A new instance of the object with the same function, arguments, and additional keyword arguments.

**Description**:
Creates a copy of the current object with optional additional arguments. The method clones the current object, preserving its function and arguments, and retains the original `action_request`, `func_outputs`, and metadata.

**Usage Examples**:
```python
new_response = action_response.clone(sender="new_sender")
print(new_response.sender)  # Output: new_sender
```
