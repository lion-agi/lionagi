# AssistantResponse API Documentation

The `AssistantResponse` class represents a response from an assistant in the Lion framework. It contains the content of the assistant's response.

## Class: AssistantResponse

Inherits from: `RoledMessage`

### Attributes

- `content: Note` - The content of the assistant's response.

### Methods

#### `__init__(assistant_response: dict | MessageFlag, sender: Any | MessageFlag, recipient: Any | MessageFlag, protected_init_params: dict | None = None)`

Initializes an AssistantResponse instance.

- **Parameters:**
  - `assistant_response: dict | MessageFlag` - The content of the assistant's response.
  - `sender: Any | MessageFlag` - The sender of the response, typically the assistant.
  - `recipient: Any | MessageFlag` - The recipient of the response.
  - `protected_init_params: dict | None` - Optional parameters for protected init.

### Properties

#### `response: Any`

Return the assistant response content.

- **Returns:**
  - `Any` - The content of the assistant's response.

### Usage Example

```python
response = AssistantResponse(
    assistant_response={"content": "The sum of 5 and 3 is 8."},
    sender="math_assistant",
    recipient="user_1"
)

print(response.response)  # Output: The sum of 5 and 3 is 8.
```

This example demonstrates how to create an AssistantResponse and access its content.
