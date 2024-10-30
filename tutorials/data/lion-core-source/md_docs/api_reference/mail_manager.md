# MailManager API Documentation

The `MailManager` class manages mail operations for multiple sources in the Lion framework. It handles the collection and distribution of mail between different components of the system.

## Class: MailManager

Inherits from: `BaseManager`

### Attributes

- `sources: Pile` - A collection of mail sources.
- `mails: dict[str, dict[str, deque]]` - A nested dictionary storing mails for each source.
- `execute_stop: bool` - Flag to stop execution.

### Methods

#### `__init__(sources: list[Any] = None)`

Initializes a MailManager instance.

- **Parameters:**
  - `sources: list[Any]` - Initial list of mail sources (optional).

#### `add_sources(sources: Any) -> None`

Add new sources to the MailManager.

- **Parameters:**
  - `sources: Any` - The sources to add.
- **Raises:**
  - `ValueError` - If failed to add source.

#### `delete_source(source_id: str) -> None`

Delete a source from the MailManager.

- **Parameters:**
  - `source_id: str` - The ID of the source to delete.
- **Raises:**
  - `ValueError` - If the source does not exist.

#### `collect(sender: str) -> None`

Collect mail from a specific sender.

- **Parameters:**
  - `sender: str` - The sender to collect mail from.
- **Raises:**
  - `ValueError` - If the sender source does not exist or if the recipient is invalid.

#### `send(recipient: str) -> None`

Send mail to a specific recipient.

- **Parameters:**
  - `recipient: str` - The recipient to send mail to.
- **Raises:**
  - `ValueError` - If the recipient source does not exist.

#### `collect_all() -> None`

Collect mail from all sources.

#### `send_all() -> None`

Send mail to all recipients.

#### `async execute(refresh_time: int = 1) -> None`

Asynchronously execute mail collection and sending process.

- **Parameters:**
  - `refresh_time: int` - Time interval between cycles (default: 1 second).

### Static Methods

#### `create_mail(sender: str, recipient: str, category: str, package: Any, request_source=None) -> Mail`

Create a new Mail object.

- **Parameters:**
  - `sender: str` - The sender of the mail.
  - `recipient: str` - The recipient of the mail.
  - `category: str` - The category of the mail.
  - `package: Any` - The content of the mail.
  - `request_source` - The source of the request (optional).
- **Returns:**
  - `Mail` - A new Mail object.

### Usage Example

```python
manager = MailManager()
manager.add_sources(["source1", "source2"])

# Create and send a mail
mail = MailManager.create_mail("source1", "source2", "message", "Hello, World!")
manager.sources["source1"].mailbox.include(mail, "out")

# Collect and send mails
manager.collect_all()
manager.send_all()

# Start asynchronous execution
import asyncio
asyncio.run(manager.execute())
```

This example demonstrates how to create a MailManager, add sources, create and send mails, and start the asynchronous execution of mail operations.
