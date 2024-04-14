# StructureExecutor API Reference

This API reference provides documentation for the `StructureExecutor` class, which is a combination of the `BaseExecutor` and `Graph` classes. It represents an executor that can process and execute nodes and edges in a graph structure.

## StructureExecutor

The `StructureExecutor` class inherits from both `BaseExecutor` and `Graph` classes.

### Attributes

- `condition_check_result` (bool | None): The result of the condition check for an edge.

### Methods

#### check_edge_condition

```python
async def check_edge_condition(self, edge: Edge, executable_id, request_source)
```

Checks the condition of an edge based on the source type (structure or executable).

**Parameters:**
- `edge` (Edge): The edge to check the condition for.
- `executable_id`: The ID of the executable.
- `request_source`: The source of the request.

**Returns:** The result of the condition check.

#### _process_edge_condition

```python
def _process_edge_condition(self, edge_id)
```

Processes the condition of an edge by checking the pending incoming mails.

**Parameters:**
- `edge_id` (str): The ID of the edge.

**Returns:** None

#### _check_executable_condition

```python
async def _check_executable_condition(self, edge: Edge, executable_id, request_source)
```

Checks the condition of an edge for an executable by sending a condition mail and processing the result.

**Parameters:**
- `edge` (Edge): The edge to check the condition for.
- `executable_id`: The ID of the executable.
- `request_source`: The source of the request.

**Returns:** The result of the condition check.

#### _handle_node_id

```python
async def _handle_node_id(self, mail: BaseMail)
```

Handles a node ID mail by checking if the node exists in the structure and getting the next nodes.

**Parameters:**
- `mail` (BaseMail): The node ID mail to handle.

**Returns:** The next nodes.

#### _handle_node

```python
async def _handle_node(self, mail: BaseMail)
```

Handles a node mail by checking if the node exists in the structure and getting the next nodes.

**Parameters:**
- `mail` (BaseMail): The node mail to handle.

**Returns:** The next nodes.

#### _handle_mail

```python
async def _handle_mail(self, mail: BaseMail)
```

Handles a mail based on its category (start, end, node_id, or node).

**Parameters:**
- `mail` (BaseMail): The mail to handle.

**Returns:** The next nodes or None.

#### _next_node

```python
async def _next_node(self, current_node: BaseNode, executable_id, request_source)
```

Gets the next nodes based on the current node and the conditions of the outgoing edges.

**Parameters:**
- `current_node` (BaseNode): The current node.
- `executable_id`: The ID of the executable.
- `request_source`: The source of the request.

**Returns:** The next nodes.

#### _send_mail

```python
def _send_mail(self, next_nodes: list | None, mail: BaseMail)
```

Sends a mail based on the next nodes (end, node, or node_list).

**Parameters:**
- `next_nodes` (list | None): The next nodes.
- `mail` (BaseMail): The mail to send.

**Returns:** None

#### parse_bundled_to_action

```python
@staticmethod
def parse_bundled_to_action(instruction: Node, bundled_nodes: deque)
```

Parses bundled nodes into an action node.

**Parameters:**
- `instruction` (Node): The instruction node.
- `bundled_nodes` (deque): The bundled nodes.

**Returns:** The action node.

#### forward

```python
async def forward(self) -> None
```

Processes the pending incoming mails and performs the corresponding actions.

**Returns:** None

#### execute

```python
async def execute(self, refresh_time=1)
```

Executes the structure by continuously processing incoming mails until the `execute_stop` flag is set to `True` or the structure is not acyclic.

**Parameters:**
- `refresh_time` (int): The time interval (in seconds) between each iteration of mail processing (default: 1).

**Returns:** None

## Usage

The `StructureExecutor` class can be used to create an executor that processes and executes nodes and edges in a graph structure. It combines the functionality of the `BaseExecutor` and `Graph` classes.

To use the `StructureExecutor`, you can create an instance of the class and call the `execute` method to start the execution process. The executor will continuously process incoming mails until the `execute_stop` flag is set to `True` or the structure is not acyclic.

```python
from lionagi.core.executor.structure_executor import StructureExecutor

executor = StructureExecutor()
await executor.execute()
```

During the execution process, the `StructureExecutor` will handle different types of mails based on their categories:
- `start`: Gets the head nodes of the structure.
- `end`: Sets the `execute_stop` flag to `True`.
- `node_id`: Handles a node ID mail by checking if the node exists in the structure and getting the next nodes.
- `node`: Handles a node mail by checking if the node exists in the structure and getting the next nodes.

The `StructureExecutor` also provides methods for checking edge conditions, processing edge conditions, handling mails, getting the next nodes, sending mails, and parsing bundled nodes into action nodes.

That's it! You now have a comprehensive understanding of the `StructureExecutor` class and how to use it to execute a graph structure in the `lionagi` framework. Let me know if you have any further questions!