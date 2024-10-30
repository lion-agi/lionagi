# ActionResponse API Documentation

The `ActionResponse` class represents a response to an action request in the Lion framework. It contains the output of the function call and links back to the original request.

## Class: ActionResponse

Inherits from: `RoledMessage`

### Attributes

- `content: Note` - The content of the action response, containing the function output and request details.

### Methods

#### `__init__(action_request: ActionRequest | MessageFlag, sender: Any | MessageFlag, func_output: Any | MessageFlag, protected_init_params: dict | None = None)`

Initializes an ActionResponse instance.

- **Parameters:**
  - `action_request: ActionRequest | MessageFlag` - The original action request to respond to.
  - `sender: Any | MessageFlag` - The sender of the action response.
  - `func_output: Any | MessageFlag` - The output from the function in the request.
  - `protected_init_params: dict | None` - Protected initialization parameters.

#### `update_request(action_request: ActionRequest, func_output: Any) -> None`

Update the action response with new request and output.

- **Parameters:**
  - `action_request: ActionRequest` - The original action request being responded to.
  - `func_output: Any` - The output from the function in the request.

### Properties

#### `func_output: Any`

Get the function output from the action response.

- **Returns:**
  - `Any` - The function output.

#### `response_dict: dict[str, Any]`

Get the action response as a dictionary.

- **Returns:**
  - `dict[str, Any]` - The action response dictionary.

#### `action_request_id: str | None`

Get the ID of the corresponding action request.

- **Returns:**
  - `str | None` - The ID of the corresponding action request.

### Usage Example

```python
request = ActionRequest(func="calculate_sum", arguments={"a": 5, "b": 3}, sender="user_1", recipient="math_service")
response = ActionResponse(action_request=request, sender="math_service", func_output=8)

print(response.func_output)  # Output: 8
print(response.action_request_id)  # Output: [ID of the original request]
```

This example shows how to create an ActionResponse linked to an ActionRequest and access its properties.
