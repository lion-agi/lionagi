
### Class: `MessageField`

**Description**:
`MessageField` is an enumeration used to store message fields for consistent referencing. 

### Enum Members:
- `LION_ID`: Represents the lion_id field.
- `TIMESTAMP`: Represents the timestamp field.
- `ROLE`: Represents the role field.
- `SENDER`: Represents the sender field.
- `RECIPIENT`: Represents the recipient field.
- `CONTENT`: Represents the content field.

---

### Class: `MessageRole`

**Description**:
`MessageRole` is an enumeration for possible roles a message can assume in a conversation.

### Enum Members:
- `SYSTEM`: Represents the system role.
- `USER`: Represents the user role.
- `ASSISTANT`: Represents the assistant role.

---

### Class: `RoledMessage`
^f41a31

**Parent Class:** [[Node#^c394ef|Node]], [[API reference/collections/abc/Concepts#^ef363b|Sendable]]

**Description**:
`RoledMessage` is a base class representing a message with validators and properties. It extends `Node` and `Sendable`.

#### Attributes:
- `role` (MessageRole | None): The role of the message in the conversation.

### `image_content`

**Signature**:
```python
@property
def image_content() -> list | None:
```

**Return Values**:
- `list | None`: A list of image content if available, otherwise `None`.

**Description**:
Returns the image content from the message if available.

**Usage Examples**:
```python
message = RoledMessage(role=MessageRole.ASSISTANT, content={"images": [{"type": "image_url", "url": "example.com/image1"}, {"type": "image_url", "url": "example.com/image2"}]})
print(message.image_content)  # Output: [{'type': 'image_url', 'url': 'example.com/image1'}, {'type': 'image_url', 'url': 'example.com/image2'}]
```

### `chat_msg`

**Signature**:
```python
@property
def chat_msg() -> dict | None:
```

**Return Values**:
- `dict | None`: The message in chat representation if valid, otherwise `None`.

**Description**:
Returns the message in chat representation.

**Usage Examples**:
```python
message = RoledMessage(role=MessageRole.USER, content={"text": "Hello"})
print(message.chat_msg)  # Output: {'role': 'user', 'content': 'Hello'}
```

### `_check_chat_msg`

**Signature**:
```python
def _check_chat_msg() -> dict:
```

**Return Values**:
- `dict`: The validated chat message.

**Description**:
Validates and returns the chat message.

**Usage Examples**:
```python
message = RoledMessage(role=MessageRole.SYSTEM, content={"text": "System update"})
print(message._check_chat_msg())  # Output: {'role': 'system', 'content': 'System update'}
```

### `__str__`

**Signature**:
```python
def __str__() -> str:
```

**Return Values**:
- `str`: A string representation of the message with a content preview.

**Description**:
Provides a string representation of the message with a preview of its content.

**Usage Examples**:
```python
message = RoledMessage(role=MessageRole.USER, sender="user1", content={"text": "This is a test message."})
print(str(message))  # Output: Message(role=user, sender=user1, content='{'text': 'This is a test message.'}')
```
