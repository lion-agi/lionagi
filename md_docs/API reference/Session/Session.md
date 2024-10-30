
### Class: `Session`

**Description**:
`Session` is a class for managing branches, [[Mail#^c3b817|Mail]] transfer, and interactions with a model. It encapsulates the entire lifecycle of a session, including the creation and manipulation of branches, the collection and sending of mail, and handling chat and [[API reference/collections/abc/Concepts#^759d9f|Directive]] interactions.

### Attributes:

- `ln_id` (str): The unique identifier for the session.
- `timestamp` (str): The timestamp when the session was created.
- `system` ([[System Message#^2711f6|System]]): The default system message for the session.
- `system_sender` (str): The sender of the system message.
- `branches` ([[Pile#^0206c8|Pile]]): The pile of branches in the session.
- `mail_transfer` ([[Exchange#^2a685d|Exchange]]): The exchange for managing mail transfer.
- `mail_manager` (MailManager): The manager for handling mail.
- `imodel` (iModel): The model associated with the session.
- `user` (str): The user associated with the session.
- `default_branch` (Branch): The default branch of the session.

### Methods:

#### `__init__`

**Signature**:
```python
def __init__(
    self,
    system=None,  # the default system message for the session
    branches: Any | None = None,
    system_sender: str | None = None,
    user: str | None = None,
    imodel=None,
):
```

**Parameters**:
- `system` (System, optional): The default system message for the session.
- `branches` (Any | None, optional): The initial [[branch#^958e6d|branches]] for the session.
- `system_sender` (str | None, optional): The sender of the system message.
- `user` (str | None, optional): The user associated with the session.
- `imodel` (iModel, optional): The model associated with the session.

**Description**:
Initializes a new session with the given parameters, setting up branches, mail transfer, mail manager, and the default branch.


#### `new_branch`

**Signature**:
```python
def new_branch(
    self,
    system: System | None = None,
    system_sender: str | None = None,
    user: str | None = None,
    messages: Pile = None,
    progress: Progression = None,
    tool_manager: ToolManager = None,
    tools: Any = None,
    imodel=None,
):
```

**Parameters**:
- `system` (System, optional): The system message for the branch.
- `system_sender` (str, optional): The sender of the system message.
- `user` (str, optional): The user associated with the branch.
- `messages` (Pile, optional): The pile of messages for the branch.
- `progress` (Progression, optional): The progression of messages.
- `tool_manager` (ToolManager, optional): The tool manager for the branch.
- `tools` (Any, optional): The tools to register with the tool manager.
- `imodel` (iModel, optional): The model associated with the branch.

**Returns**:
- `Branch`: The created branch.

**Description**:
Creates a new branch and adds it to the session.

#### `delete_branch`

**Signature**:
```python
def delete_branch(self, branch):
```

**Parameters**:
- `branch` (Branch | str): The branch or its ID to delete.

**Description**:
Deletes a branch from the session.

#### `split_branch`

**Signature**:
```python
def split_branch(self, branch):
```

**Parameters**:
- `branch` (Branch | str): The branch or its ID to split.

**Returns**:
- `Branch`: The newly created branch.

**Description**:
Splits a branch, creating a new branch with the same messages and tools.

#### `change_default_branch`

**Signature**:
```python
def change_default_branch(self, branch):
```

**Parameters**:
- `branch` (Branch | str): The branch or its ID to set as the default.

**Description**:
Changes the default branch of the session.

#### `collect`

**Signature**:
```python
def collect(self, from_: Branch | str | Pile[Branch] | None = None):
```

**Parameters**:
- `from_` (Branch | str | Pile[Branch], optional): The branches to collect mail from. If `None`, collects mail from all branches.

**Description**:
Collects mail from specified branches.

#### `send`

**Signature**:
```python
def send(self, to_: Branch | str | Pile[Branch] | None = None):
```

**Parameters**:
- `to_` (Branch | str | Pile[Branch], optional): The branches to send mail to. If `None`, sends mail to all branches.

**Description**:
Sends mail to specified branches.

#### `collect_send_all`

**Signature**:
```python
def collect_send_all(self, receive_all=False):
```

**Parameters**:
- `receive_all` (bool, optional): Whether to receive all mail for all branches.

**Description**:
Collects and sends mail for all branches, optionally receiving all mail.

#### `chat`

**Signature**:
```python
async def chat(self, *args, branch=None, **kwargs):
```

**Parameters**:
- `branch` (Branch, optional): The branch to chat with. Defaults to the default branch.
- `*args`: Positional arguments to pass to the chat method.
- `**kwargs`: Keyword arguments to pass to the chat method.

**Returns**:
- `Any`: The result of the chat interaction.

**Raises**:
- `ValueError`: If the specified branch is not found in the session branches.

**Description**:
Initiates a chat interaction with a branch.

#### `direct`

**Signature**:
```python
async def direct(self, *args, branch=None, **kwargs):
```

**Parameters**:
- `branch` (Branch, optional): The branch to interact with. Defaults to the default branch.
- `*args`: Positional arguments to pass to the direct method.
- `**kwargs`: Keyword arguments to pass to the direct method.

**Returns**:
- `Any`: The result of the direct interaction.

**Raises**:
- `ValueError`: If the specified branch is not found in the session branches.

**Description**:
Initiates a direct interaction with a branch.
