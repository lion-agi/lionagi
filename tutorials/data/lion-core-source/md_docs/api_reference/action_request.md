# ActionRequest API Documentation

The `ActionRequest` class represents a request for an action in the Lion framework. It encapsulates the function name and arguments for the action to be performed.

## Class: ActionRequest

Inherits from: `RoledMessage`

### Attributes

- `content: Note` - The content of the action request, containing function and arguments.

### Methods

#### `__init__(func: str | Callable | MessageFlag, arguments: dict | MessageFlag, sender: Any | MessageFlag, recipient: Any | MessageFlag, protected_init_params: dict | None = None)`

Initializes an ActionRequest instance.

- **Parameters:**
  - `func: str | Callable | MessageFlag` - The function to be invoked.
  - `arguments: dict | MessageFlag` - The arguments for the function.
  - `sender: Any | MessageFlag` - The sender of the request.
  - `recipient: Any | MessageFlag` - The recipient of the request.
  - `protected_init_params: dict | None` - Protected initialization parameters.

### Properties

#### `action_response_id: str | None`

Get the ID of the corresponding action response, if any.

- **Returns:**
  - `str | None` - The ID of the action response, or None if not responded.

#### `is_responded: bool`

Check if the action request has been responded to.

- **Returns:**
  - `bool` - True if the action request has been responded to, else False.

#### `request_dict: dict[str, Any]`

Get the action request content as a dictionary.

- **Returns:**
  - `dict[str, Any]` - The action request content.

#### `arguments: dict[str, Any]`

Get the arguments for the action request.

- **Returns:**
  - `dict[str, Any]` - The arguments for the action request.

#### `function: str`

Get the function name for the action request.

- **Returns:**
  - `str` - The function name for the action request.

### Usage Example

```python
request = ActionRequest(
    func="calculate_sum",
    arguments={"a": 5, "b": 3},
    sender="user_1",
    recipient="math_service"
)

print(request.function)  # Output: calculate_sum
print(request.arguments)  # Output: {"a": 5, "b": 3}
print(request.is_responded)  # Output: False
```

This example demonstrates how to create an ActionRequest and access its properties.
