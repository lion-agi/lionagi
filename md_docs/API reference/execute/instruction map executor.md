# InstructionMapExecutor API Reference

This API reference provides documentation for the `InstructionMapExecutor` class, which represents an executor that manages and executes branches based on instructions.

## InstructionMapExecutor

The `InstructionMapExecutor` class inherits from the `BaseExecutor` class.

### Attributes

- `branches` (dict[str, BranchExecutor]): A dictionary of branches, where the keys are branch IDs and the values are `BranchExecutor` instances.
- `structure_id` (str): The ID of the executable structure.
- `mail_transfer` (MailTransfer): The mail transfer object for handling mail communication between branches.
- `branch_kwargs` (dict): The keyword arguments for initializing the branches.
- `num_end_branches` (int): The number of branches that have reached the end state.
- `mail_manager` (MailManager): The mail manager object for managing mail communication.

### Methods

#### `__init__`

```python
def __init__(self, **kwargs)
```

Initializes a new instance of the `InstructionMapExecutor` class.

**Parameters:**
- `**kwargs`: Additional keyword arguments.

#### transfer_ins

```python
def transfer_ins(self)
```

Transfers the pending incoming mails to the appropriate branches or processes them based on their category.

**Returns:** None

#### transfer_outs

```python
def transfer_outs(self)
```

Transfers the pending outgoing mails from the branches to the structure or processes them based on their category.

**Returns:** None

#### _process_start

```python
def _process_start(self, start_mail: BaseMail)
```

Processes a start mail by creating a new branch, initializing its context, and sending a start mail to the structure.

**Parameters:**
- `start_mail` (BaseMail): The start mail to process.

**Returns:** None

#### _process_node_list

```python
def _process_node_list(self, nl_mail: BaseMail)
```

Processes a node list mail by creating new branches for each node in the list, initializing their context, and sending node mails to the branches.

**Parameters:**
- `nl_mail` (BaseMail): The node list mail to process.

**Returns:** None

#### forward

```python
async def forward(self)
```

Performs a forward pass by transferring incoming and outgoing mails, collecting and sending mails through the mail manager, and executing the forward pass for each branch.

**Returns:** None

#### execute

```python
async def execute(self, refresh_time=1)
```

Executes the instruction map by continuously performing forward passes until the `execute_stop` flag is set to `True`.

**Parameters:**
- `refresh_time` (int): The time interval (in seconds) between each forward pass (default: 1).

**Returns:** None

## Usage

The `InstructionMapExecutor` class can be used to manage and execute branches based on instructions. It handles the communication between branches and the executable structure using mails.

To use the `InstructionMapExecutor`, you can create an instance of the class and call the `execute` method to start the execution process. The executor will continuously perform forward passes until the `execute_stop` flag is set to `True`.

```python
from lionagi.core.executor.instruction_map_executor import InstructionMapExecutor

executor = InstructionMapExecutor()
await executor.execute()
```

During the execution process, the `InstructionMapExecutor` will handle different types of mails based on their categories:
- `start`: Processes a start mail by creating a new branch, initializing its context, and sending a start mail to the structure.
- `node_list`: Processes a node list mail by creating new branches for each node in the list, initializing their context, and sending node mails to the branches.
- `node`, `condition`, `end`: Transfers these mails from the branches to the structure.

The `InstructionMapExecutor` uses a `MailManager` to manage the communication between branches and the executable structure. It also keeps track of the number of branches that have reached the end state to determine when to stop the execution.

That's it! You now have a comprehensive understanding of the `InstructionMapExecutor` class and how to use it to manage and execute branches based on instructions. Let me know if you have any further questions!