
### Class: `Branch`

**Description**:
`Branch` represents a branch in a messaging system, capable of handling messages, tools, and models. It provides functionalities for adding messages, managing tools, sending and receiving mails, and converting messages to different formats.

#### Attributes:
- `messages` (Pile): A pile of messages.
- `progress` (Progression): A progression of messages.
- `tool_manager` (ToolManager): A manager for handling tools.
- `system` (System): The system associated with the branch.
- `user` (str): The user associated with the branch.
- `mailbox` (Exchange): An exchange for managing mail.
- `imodel` (iModel): The model associated with the branch.

### Method: `__init__`

**Signature**:
```python
def __init__(
    self,
    system: System | None = None,
    system_sender: str | None = None,
    user: str | None = None,
    messages: Pile = None,
    progress: Progression = None,
    tool_manager: ToolManager = None,
    tools: Any = None,
    imodel=None,
)
```

**Parameters**:
- `system` (System, optional): The system associated with the branch.
- `system_sender` (str, optional): The sender of the system message.
- `user` (str, optional): The user associated with the branch.
- `messages` (Pile, optional): A pile of messages.
- `progress` (Progression, optional): A progression of messages.
- `tool_manager` (ToolManager, optional): A manager for handling tools.
- `tools` (Any, optional): Tools to be registered with the tool manager.
- `imodel` (iModel, optional): The model associated with the branch.

**Description**:
Initializes a new instance of the `Branch` class.

### Method: `set_system`

**Signature**:
```python
def set_system(self, system=None, sender=None) -> None
```

**Parameters**:
- `system` (System, optional): The system message to set.
- `sender` (str, optional): The sender of the system message.

**Description**:
Sets the system message for the branch.

### Method: `add_message`

**Signature**:
```python
def add_message(
    self,
    *,
    system=None,
    instruction=None,
    context=None,
    assistant_response=None,
    function=None,
    arguments=None,
    func_outputs=None,
    action_request=None,
    action_response=None,
    images=None,
    sender=None,
    recipient=None,
    requested_fields=None,
    metadata: dict | None = None,
    **kwargs,
) -> bool
```

**Parameters**:
- `system` (Any, optional): The system node (JSON serializable).
- `instruction` (Any, optional): The instruction node (JSON serializable).
- `context` (Any, optional): Additional context (JSON serializable).
- `assistant_response` (Any, optional): The assistant's response (JSON serializable).
- `function` (Any, optional): The function associated with the message.
- `arguments` (Any, optional): The arguments for the function.
- `func_outputs` (Any, optional): The outputs of the function.
- `action_request` (Any, optional): The action request node.
- `action_response` (Any, optional): The action response node.
- `sender` (str, optional): The sender of the message.
- `recipient` (str, optional): The recipient of the message.
- `requested_fields` (dict[str, str], optional): Requested fields for the message.
- `metadata` (dict, optional): Extra metadata for the message.
- `kwargs`: Additional context fields.

**Return Values**:
- `bool`: True if the message was successfully added, else False.

**Description**:
Adds a message to the branch.

### Method: `to_chat_messages`

**Signature**:
```python
def to_chat_messages(self) -> list[dict[str, Any]]
```

**Return Values**:
- `list[dict[str, Any]]`: A list of chat messages.

**Description**:
Converts the messages to chat message format.

### Method: `_remove_system`

**Signature**:
```python
def _remove_system(self) -> None
```

**Description**:
Removes the system message from the branch.

### Method: `clear`

**Signature**:
```python
def clear(self) -> None
```

**Description**:
Clears all messages and progression in the branch.

### Method: `has_tools`

**Signature**:
```python
@property
def has_tools(self) -> bool
```

**Return Values**:
- `bool`: True if the branch has tools, else False.

**Description**:
Checks if the branch has tools.

### Method: `register_tools`

**Signature**:
```python
def register_tools(self, tools) -> None
```

**Parameters**:
- `tools` (Any): The tools to register.

**Description**:
Registers tools with the tool manager.

### Method: `delete_tools`

**Signature**:
```python
def delete_tools(self, tools, verbose: bool = True) -> bool
```

**Parameters**:
- `tools` (Any): The tools to delete.
- `verbose` (bool, optional): Whether to print deletion status.

**Return Values**:
- `bool`: True if tools were successfully deleted, else False.

**Description**:
Deletes tools from the tool manager.

### Method: `update_last_instruction_meta`

**Signature**:
```python
def update_last_instruction_meta(self, meta)
```

**Parameters**:
- `meta` (dict): The metadata to update.

**Description**:
Updates metadata of the last instruction.

### Method: `to_df`

**Signature**:
```python
def to_df(self) -> Any
```

**Return Values**:
- `Any`: A DataFrame representation of the messages.

**Description**:
Converts the messages to a DataFrame.

### Method: `_is_invoked`

**Signature**:
```python
def _is_invoked(self) -> bool
```

**Return Values**:
- `bool`: True if the last message is an ActionResponse, else False.

**Description**:
Checks if the last message is an ActionResponse.

### Method: `send`

**Signature**:
```python
def send(self, recipient: str, category: str, package: Any, request_source: str = None) -> None
```

**Parameters**:
- `recipient` (str): The ID of the recipient.
- `category` (str): The category of the mail.
- `package` (Any): The package to send in the mail.
- `request_source` (str, optional): The source of the request.

**Description**:
Sends a mail to a recipient.

### Method: `receive`

**Signature**:
```python
def receive(self, sender: str, message: bool = True, tool: bool = True, imodel: bool = True) -> None
```

**Parameters**:
- `sender` (str): The ID of the sender.
- `message` (bool, optional): Whether to process message mails. Defaults to True.
- `tool` (bool, optional): Whether to process tool mails. Defaults to True.
- `imodel` (bool, optional): Whether to process imodel mails. Defaults to True.

**Description**:
Receives mail from a sender.

**Exceptions Raised**:
- `ValueError`: If the sender does not exist or the mail category is invalid.

### Method: `receive_all`

**Signature**:
```python
def receive_all(self) -> None
```

**Description**:
Receives mail from all senders.
