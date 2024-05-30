
### Class: `BranchExecutor`

^209f34

**Description**:
`BranchExecutor` is a class designed to manage and execute various tasks within a branch context. It extends the [[branch#^958e6d|Branch]] and BaseExecutor classes, integrating functionalities for processing different types of nodes (e.g., start, node, node list, condition, end) and handling asynchronous operations. 

**Attributes**:
- `context`: The context for the execution.
- `verbose`: A flag indicating whether to provide verbose output.
- `execute_stop`: A flag to control the execution loop.
- `mailbox`: The mailbox holding pending incoming mails.

**Methods**:

#### `__init__`
Initializes the `BranchExecutor` with the provided parameters.

**Signature**:
```python
def __init__(
    self,
    context=None,
    verbose=True,
    system=None,
    user=None,
    messages=None,
    progress=None,
    tool_manager=None,
    tools=None,
    imodel=None,
    **kwargs,
)
```

**Parameters**:
- `context` (Any, optional): The execution context.
- `verbose` (bool, optional): A flag to enable verbose output. Default is `True`.
- `system`, `user`, `messages`, `progress`, `tool_manager`, `tools`, `imodel`: Various parameters inherited from the `Branch` and `BaseExecutor` classes.
- `**kwargs`: Additional keyword arguments.

#### `forward`
Processes all pending incoming mails in each branch. Depending on the category of the mail, it processes starts, nodes, node lists, conditions, or ends.

**Signature**:
```python
async def forward(self) -> None
```

**Returns**:
- `None`

#### `execute`
Executes the forward process repeatedly at specified time intervals until execution is instructed to stop.

**Signature**:
```python
async def execute(self, refresh_time=1) -> None
```

**Parameters**:
- `refresh_time` (int): The interval, in seconds, at which the `forward` method is called repeatedly. Default is `1`.

**Returns**:
- `None`

