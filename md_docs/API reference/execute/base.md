# BaseExecutor API Reference

This API reference provides documentation for the `BaseExecutor` class, which serves as a base class for implementing executors in the `lionagi` framework.

## BaseExecutor

The `BaseExecutor` class is an abstract base class that defines the common attributes and methods for executors. It inherits from `BaseComponent` and `ABC` (Abstract Base Class).

### Attributes

- `pending_ins` (`dict`): A dictionary representing the pending incoming mails (default: empty dict).
- `pending_outs` (`deque`): A `deque` representing the pending outgoing mails (default: empty `deque`).
- `execute_stop` (`bool`): A flag indicating whether to stop execution (default: False).
- `context` (`dict | str | None`): The context buffer for the next instruction (default: `None`).
- `execution_responses` (`list`): A list of execution responses (default: empty list).
- `context_log` (`list`): A list representing the context log (default: empty list).
- `verbose` (`bool`): A flag indicating whether to provide verbose output (default: True).
- `execute_stop` (`bool`): A flag indicating whether to stop execution (default: False).

### Methods

#### send

```python
def send(self, recipient_id: str, category: str, package: Any) -> None
```

Sends a mail to a recipient.

**Parameters:**
- `recipient_id` (str): The ID of the recipient.
- `category` (str): The category of the mail.
- `package` (Any): The package to send in the mail.

**Returns:** None

### Abstract Methods

The `BaseExecutor` class does not define any abstract methods, but subclasses are expected to implement their own specific methods for execution.

## Usage

To create a custom executor, you should subclass the `BaseExecutor` class and implement your own specific methods for execution. The `BaseExecutor` class provides a foundation for managing incoming and outgoing mails, execution control, context handling, and response logging.

Here's an example of how you can create a custom executor:

```python
from lionagi.core.executor.base import BaseExecutor

class MyExecutor(BaseExecutor):
    def execute(self, instruction: str) -> None:
        # Custom execution logic goes here
        pass

    def process_response(self, response: Any) -> None:
        # Custom response processing logic goes here
        pass
```

In the above example, `MyExecutor` inherits from `BaseExecutor` and defines its own `execute` and `process_response` methods to implement custom execution and response processing logic.

You can access and modify the attributes of the `BaseExecutor` class within your custom executor as needed. For example, you can add incoming mails to `pending_ins`, append outgoing mails to `pending_outs`, set the `execute_stop` flag to control execution flow, update the `context` buffer, and log responses and context.

Remember to call the `send` method to send mails to recipients as required by your execution logic.
