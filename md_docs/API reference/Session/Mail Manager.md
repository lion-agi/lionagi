

# MailManager API Reference

The `MailManager` class is designed to manage mail sources and the distribution of mail items between these sources. It provides a framework for creating, adding, and deleting mail sources, as well as collecting and sending mail items based on specified criteria.

## Constructor

### `MailManager(sources: Dict[str, Any])`

Initializes a new instance of the `MailManager` class.

- **Parameters:**
  - `sources`: A dictionary where keys are source identifiers (e.g., names) and values are any type, typically objects or instances that represent each source.

## Methods

### `create_mail(sender, recipient, category, package) -> BaseMail`

A static method that creates a new mail item.

- **Parameters:**
  - `sender`: The identifier of the sender.
  - `recipient`: The identifier of the recipient.
  - `category`: The category of the mail item.
  - `package`: The actual content or package of the mail.
- **Returns:** An instance of `BaseMail`.
- **Example:**
  ```python
  mail_item = MailManager.create_mail("Alice", "Bob", "Greetings", "Hello, Bob!")
  ```

### `add_source(sources: Dict[str, Any])`

Adds new sources to the mail manager.

- **Parameters:**
  - `sources`: A dictionary of new sources to be added, where keys are source identifiers and values are their respective details.
- **Raises:** `ValueError` if a source already exists with the same key.
- **Example:**
  ```python
  mail_manager.add_source({"source4": {}})
  ```

### `delete_source(source_name)`

Deletes a source from the mail manager.

- **Parameters:**
  - `source_name`: The identifier of the source to be deleted.
- **Raises:** `ValueError` if the specified source does not exist.
- **Example:**
  ```python
  mail_manager.delete_source("source4")
  ```

### `collect(sender)`

Collects pending outgoing mails from a specified sender and organizes them into the internal mail storage for future delivery.

- **Parameters:**
  - `sender`: The identifier of the sender whose outgoing mails should be collected.
- **Raises:** `ValueError` if the specified sender does not exist.
- **Example:**
  ```python
  mail_manager.collect("Alice")
  ```

### `send(to_name)`

Sends all mails targeted to a specified recipient.

- **Parameters:**
  - `to_name`: The identifier of the recipient to whom the mails should be sent.
- **Raises:** `ValueError` if the specified recipient does not exist.
- **Example:**
  ```python
  mail_manager.send("Bob")
  ```

## Exceptions

- `ValueError`: Raised when attempting to add a source that already exists, delete a non-existing source, collect from a non-existing sender, or send to a non-existing recipient.

## Usage Example

```python
# Initialize the mail manager with some sources
sources = {"source1": {}, "source2": {}}
mail_manager = MailManager(sources)

# Add a new source
mail_manager.add_source({"source3": {}})

# Create a mail input_
mail_item = MailManager.create_mail("source1", "source2", "category1", "package1")

# Collect and send mail items
mail_manager.collect("source1")
mail_manager.send("source2")
```

This API reference provides a concise overview of the `MailManager` class functionalities, aimed at facilitating the management and distribution of mail items within a system.
