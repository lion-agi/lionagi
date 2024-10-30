# Session API Documentation

## Overview

The `Session` class in the Lion framework manages multiple conversation branches and handles mail transfer between components. It provides a high-level interface for creating, managing, and interacting with multiple `Branch` instances within a single session.

## Class Definition

```python
class Session(BaseSession):
    """Manages multiple conversation branches and mail transfer in a session."""
```

## Attributes

- `branches: Pile | None` - A collection of conversation branches.
- `default_branch: Branch | None` - The default conversation branch.
- `mail_transfer: Exchange | None` - Handles mail transfer between components.
- `mail_manager: MailManager | None` - Manages mail operations.
- `conversations: Flow | None` - Manages conversation flow across branches.
- `branch_type: Type[Branch]` - The type of Branch to be used (default is Branch).

## Methods

### Branch Management

#### `new_branch`

```python
async def new_branch(self, system: Any = None, system_sender: str | None = None, system_datetime: Any = None, user: str | None = None, name: str | None = None, imodel: iModel | None = None, messages: Pile | None = None, progress: Progression | None = None, tool_manager: ToolManager | None = None, tools: Any = None, **kwargs) -> Branch:
```

Create a new branch in the session.

#### `remove_branch`

```python
def remove_branch(self, branch: Branch | str, delete: bool = False):
```

Remove a branch from the session.

#### `split_branch`

```python
def split_branch(self, branch: Branch | str) -> Branch:
```

Create a new branch with the same messages and tools as an existing branch.

#### `change_default_branch`

```python
def change_default_branch(self, branch: Branch | str):
```

Change the default branch of the session.

### Communication

#### `collect`

```python
def collect(self, from_: Branch | str | Pile[Branch] | None = None):
```

Collect mail from specified branches.

#### `send`

```python
def send(self, to_: Branch | str | Pile[Branch] | None = None):
```

Send mail to specified branches.

#### `collect_send_all`

```python
def collect_send_all(self, receive_all: bool = False):
```

Collect and send mail for all branches, optionally receiving all mail.

## Usage Examples

### Creating a Session and Branches

```python
from lion_core.session.session import Session
from lion_core.communication.system import System

# Create a new session
session = Session()

# Create a new branch
main_branch = await session.new_branch(
    system=System("You are a helpful AI assistant."),
    name="main_conversation",
    user="user123"
)

# Create another branch
side_branch = await session.new_branch(
    system=System("You are a specialized coding assistant."),
    name="coding_help",
    user="user123"
)
```

### Managing Branches

```python
# Set the default branch
session.change_default_branch(main_branch)

# Split an existing branch
new_branch = session.split_branch(main_branch)

# Remove a branch
session.remove_branch(side_branch, delete=True)
```

### Communication Between Branches

```python
# Collect mail from a specific branch
session.collect(from_=main_branch)

# Send mail to a specific branch
session.send(to_=new_branch)

# Collect and send mail for all branches
session.collect_send_all(receive_all=True)
```

### Using Multiple Branches

```python
# Add a message to the main branch
main_branch.add_message(
    sender="user123",
    recipient=main_branch.ln_id,
    instruction="Tell me about AI."
)

# Add a message to the coding branch
coding_branch = session.branches["coding_help"]
coding_branch.add_message(
    sender="user123",
    recipient=coding_branch.ln_id,
    instruction="Explain Python decorators."
)

# Process messages in all branches
for branch in session.branches:
    # Process messages in each branch
    pass
```

## Best Practices

1. Use meaningful names for branches when creating them to easily identify their purpose.
2. Set a default branch for the session to streamline operations when working with a primary conversation flow.
3. Utilize the `split_branch` method when you need to create a new branch that continues from an existing conversation.
4. Regularly use `collect_send_all` to ensure all branches are up-to-date with the latest communications.
5. When removing branches, consider whether you need to delete them entirely or just remove them from the session.
6. Leverage the `mail_manager` for complex routing of messages between branches and external components.
7. Use type hints when working with Session methods to improve code readability and catch potential type errors early.
8. When working with multiple branches, consider using the `conversations` Flow to manage the overall conversation structure.

## Notes

- The `Session` class inherits from `BaseSession`, providing additional session-related functionality.
- The `branches` attribute is a `Pile` of `Branch` objects, allowing for efficient branch management.
- The `mail_transfer` and `mail_manager` attributes facilitate communication between branches and external components.
- The `conversations` attribute (a `Flow` object) can be used to manage complex conversation structures across multiple branches.
- The `branch_type` attribute allows for customization of the Branch class used in the session, enabling easy extension of branch functionality.
- When creating a new branch without specifying a system message, it will use a clone of the session's system message.
