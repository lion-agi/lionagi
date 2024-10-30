# Branch API Documentation

## Overview

The `Branch` class represents a branch in the conversation tree within the Lion framework. It manages messages, tools, and communication within the branch, providing a rich set of methods for handling various types of interactions and data.

## Class Definition

```python
class Branch(BaseSession):
    """Represents a branch in the conversation tree with tools and messages."""
```

## Attributes

- `messages: Pile | None` - A Pile containing RoledMessage objects.
- `tool_manager: ToolManager | None` - Manages the tools available in this branch.
- `mailbox: Exchange | None` - Handles incoming and outgoing mail for the branch.
- `progress: Progression | None` - Tracks the order of messages in the branch.
- `system: System | None` - The system message for this branch.
- `user: str | None` - The user associated with this branch.
- `imodel: iModel | None` - The intelligent model associated with this branch.
- `name: str | None` - The name of the branch.

## Methods

### Message Management

#### `add_message`

```python
def add_message(self, **kwargs) -> bool:
```

Add a new message to the branch. Supports various message types including system messages, instructions, assistant responses, and action requests/responses.

#### `clear_messages`

```python
def clear_messages(self) -> None:
```

Clear all messages except the system message.

#### `set_system`

```python
def set_system(self, system: System) -> None:
```

Set or update the system message for the branch.

### Communication

#### `send`

```python
def send(self, recipient: str, category: str, package: Any, request_source: str) -> None:
```

Send a mail to a recipient.

#### `receive`

```python
def receive(self, sender: str, message: bool = False, tool: bool = False, imodel: bool = False) -> None:
```

Receive mail from a sender.

#### `receive_all`

```python
def receive_all(self) -> None:
```

Receive mail from all senders.

### Tool Management

#### `register_tools`

```python
def register_tools(self, tools: Any) -> None:
```

Register new tools to the tool manager.

#### `delete_tools`

```python
def delete_tools(self, tools: Any, verbose: bool = True) -> bool:
```

Delete specified tools from the tool manager.

### Data Access and Conversion

#### `to_chat_messages`

```python
def to_chat_messages(self, progress=None) -> list[dict[str, Any]]:
```

Convert messages to a list of chat message dictionaries.

#### `convert_to`

```python
def convert_to(self, key: str, /, **kwargs: Any) -> Any:
```

Convert the branch to a specified type using the ConverterRegistry.

#### `convert_from`

```python
@classmethod
def convert_from(cls, obj: Any, key: str = "DataFrame", **kwargs) -> "Branch":
```

Convert data to create a new branch instance using the ConverterRegistry.

### Properties

- `last_response: AssistantResponse | None` - Get the last assistant response.
- `assistant_responses: Pile` - Get all assistant responses as a Pile.

## Usage Examples

### Creating a Branch

```python
from lion_core.session.branch import Branch
from lion_core.communication.system import System

# Create a new branch
branch = Branch(name="main_conversation")

# Set the system message
system_msg = System("You are a helpful AI assistant.")
branch.set_system(system_msg)
```

### Adding Messages

```python
# Add a user instruction
branch.add_message(
    sender="user",
    recipient=branch.ln_id,
    instruction="Tell me a joke about programming."
)

# Add an assistant response
branch.add_message(
    sender=branch.ln_id,
    recipient="user",
    assistant_response="Why do programmers prefer dark mode? Because light attracts bugs!"
)
```

### Managing Tools

```python
from lion_core.action import Tool

def simple_calculator(a: int, b: int) -> int:
    return a + b

calc_tool = Tool(function=simple_calculator, name="calculator")

# Register a tool
branch.register_tools(calc_tool)

# Use the tool
branch.add_message(
    sender=branch.ln_id,
    recipient="user",
    action_request=ActionRequest(func="calculator", arguments={"a": 5, "b": 3})
)
```

### Communication

```python
# Send a message to another component
branch.send(
    recipient="other_component_id",
    category="message",
    package="Hello from the branch!",
    request_source=branch.ln_id
)

# Receive messages
branch.receive_all()
```

### Data Conversion

```python
# Convert branch to a dictionary
branch_dict = branch.convert_to("dict")

# Create a new branch from a dictionary
new_branch = Branch.convert_from(branch_dict, key="dict")
```

## Best Practices

1. Always set a system message for the branch to provide context for the conversation.
2. Use the `add_message` method to ensure proper message handling and ordering.
3. Leverage the `tool_manager` for registering and managing tools specific to the branch.
4. Use the `mailbox` for inter-component communication within the Lion framework.
5. Regularly check `last_response` or `assistant_responses` to track the conversation flow.
6. Use type hints when working with Branch methods to improve code readability and catch potential type errors early.
7. When converting branches, use the appropriate keys in `convert_to` and `convert_from` methods to ensure proper data transformation.

## Notes

- The `Branch` class inherits from `BaseSession`, providing additional session-related functionality.
- The `messages` attribute is a `Pile` of `RoledMessage` objects, allowing for efficient message management.
- The `progress` attribute tracks the order of messages, which is crucial for maintaining conversation flow.
- The `mailbox` attribute facilitates asynchronous communication with other components in the Lion framework.
- The `tool_manager` allows for dynamic registration and management of tools within the branch.
- The `imodel` attribute can be used to associate an intelligent model with the branch for advanced processing capabilities.
