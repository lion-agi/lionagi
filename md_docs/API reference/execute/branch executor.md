# BranchExecutor API Reference

This API reference provides documentation for the `BranchExecutor` class, which is a combination of the `Branch` and `BaseExecutor` classes. It represents an executor that can process and execute various types of mails and nodes in the `lionagi` framework.

## BranchExecutor

The `BranchExecutor` class inherits from both `Branch` and `BaseExecutor` classes.

### Methods

#### forward

```python
async def forward(self) -> None
```

Processes the pending incoming mails in the `pending_ins` dictionary.

**Returns:** None

#### execute

```python
async def execute(self, refresh_time=1) -> None
```

Executes the executor by continuously processing incoming mails until the `execute_stop` flag is set to `True`.

**Parameters:**
- `refresh_time` (int): The time interval (in seconds) between each iteration of mail processing (default: 1).

**Returns:** None

#### _process_node

```python
async def _process_node(self, mail: BaseMail)
```

Processes a node mail based on the type of package it contains.

**Parameters:**
- `mail` (BaseMail): The node mail to process.

**Returns:** None

#### _process_node_list

```python
def _process_node_list(self, mail: BaseMail)
```

Processes a node list mail. Currently, multiple path selection is not supported and raises a `ValueError`.

**Parameters:**
- `mail` (BaseMail): The node list mail to process.

**Returns:** None

#### _process_condition

```python
def _process_condition(self, mail: BaseMail)
```

Processes a condition mail by evaluating the condition and sending the result back to the sender.

**Parameters:**
- `mail` (BaseMail): The condition mail to process.

**Returns:** None

#### _system_process

```python
def _system_process(self, system: System, verbose=True, context_verbose=False)
```

Processes a system package by displaying the system information and context (if available) and adding the system message to the branch.

**Parameters:**
- `system` (System): The system package to process.
- `verbose` (bool): A flag indicating whether to provide verbose output (default: True).
- `context_verbose` (bool): A flag indicating whether to display the context (default: False).

**Returns:** None

#### _instruction_process

```python
async def _instruction_process(self, instruction: Instruction, verbose=True, **kwargs)
```

Processes an instruction package by displaying the instruction, updating the context (if available), and executing the instruction using the `chat` method of the branch.

**Parameters:**
- `instruction` (Instruction): The instruction package to process.
- `verbose` (bool): A flag indicating whether to provide verbose output (default: True).
- `**kwargs`: Additional keyword arguments to pass to the `chat` method.

**Returns:** None

#### _action_process

```python
async def _action_process(self, action: ActionNode, verbose=True)
```

Processes an action package by displaying the instruction, registering tools (if available), and executing the action using the specified action function.

**Parameters:**
- `action` (ActionNode): The action package to process.
- `verbose` (bool): A flag indicating whether to provide verbose output (default: True).

**Returns:** None

#### _agent_process

```python
async def _agent_process(self, agent, verbose=True)
```

Processes an agent by executing the agent with the current context and updating the context with the result.

**Parameters:**
- `agent`: The agent to process.
- `verbose` (bool): A flag indicating whether to provide verbose output (default: True).

**Returns:** None

#### _process_start

```python
def _process_start(self, mail)
```

Processes a start mail by setting the context and sending a start response to the structure ID.

**Parameters:**
- `mail` (BaseMail): The start mail to process.

**Returns:** None

#### _process_end

```python
def _process_end(self, mail: BaseMail)
```

Processes an end mail by setting the `execute_stop` flag to `True` and sending an end response to the sender.

**Parameters:**
- `mail` (BaseMail): The end mail to process.

**Returns:** None

## Usage

The `BranchExecutor` class can be used to create an executor that processes and executes various types of mails and nodes in the `lionagi` framework. It combines the functionality of the `Branch` and `BaseExecutor` classes.

To use the `BranchExecutor`, you can create an instance of the class and call the `execute` method to start the execution process. The executor will continuously process incoming mails until the `execute_stop` flag is set to `True`.

```python
from lionagi.core.executor.branch_executor import BranchExecutor

executor = BranchExecutor()
await executor.execute()
```

During the execution process, the `BranchExecutor` will process different types of mails based on their categories:
- `start`: Processes a start mail by setting the context and sending a start response.
- `node`: Processes a node mail based on the type of package it contains (system, instruction, action, or agent).
- `node_list`: Processes a node list mail (currently not supported and raises a `ValueError`).
- `condition`: Processes a condition mail by evaluating the condition and sending the result back to the sender.
- `end`: Processes an end mail by setting the `execute_stop` flag to `True` and sending an end response.

The `BranchExecutor` also provides methods for processing specific types of packages:
- `_system_process`: Processes a system package by displaying the system information and context (if available) and adding the system message to the branch.
- `_instruction_process`: Processes an instruction package by displaying the instruction, updating the context (if available), and executing the instruction using the `chat` method of the branch.
- `_action_process`: Processes an action package by displaying the instruction, registering tools (if available), and executing the action using the specified action function.
- `_agent_process`: Processes an agent by executing the agent with the current context and updating the context with the result.
