# BaseMail API Documentation

The `BaseMail` class serves as the foundation for mail-like communication in the LION system. It provides basic attributes for sender and recipient information.

## Class: BaseMail

Inherits from: `Element`

### Attributes

- `sender: str` - The ID of the sender node, or 'system', 'user', or 'assistant'.
- `recipient: str` - The ID of the recipient node, or 'system', 'user', or 'assistant'.

### Methods

#### `__init__(sender: str = "N/A", recipient: str = "N/A")`

Initializes a BaseMail instance.

- **Parameters:**
  - `sender: str` - The ID of the sender (default: "N/A").
  - `recipient: str` - The ID of the recipient (default: "N/A").

### Class Methods

#### `_validate_sender_recipient(cls, value: Any) -> str`

Validates the sender and recipient fields.

- **Parameters:**
  - `value: Any` - The value to validate for the sender or recipient.
- **Returns:**
  - `str` - The validated sender or recipient ID.
- **Raises:**
  - `LionValueError` - If the value is not a valid sender or recipient.

### Usage Example

```python
base_mail = BaseMail(sender="user_1", recipient="system")
print(base_mail.sender)  # Output: user_1
print(base_mail.recipient)  # Output: system
```

This example demonstrates how to create a BaseMail instance and access its sender and recipient attributes.
