
### Class: `Graph`

**Description**:
`Graph` represents a graph structure with nodes and edges. It extends the `Node` class and provides various methods to manipulate and query the graph, including adding and removing nodes and edges, checking if the graph is empty or acyclic, and converting the graph to a NetworkX graph for visualization.

#### Attributes:
- `internal_nodes` (Pile): The pile of nodes in the graph.

### Method: `internal_edges`

**Signature**:
```python
@property
def internal_edges(self) -> Pile[Edge]:
```

**Return Values**:
- `Pile[Edge]`: The pile of all edges in the graph.

**Description**:
Returns a pile of all edges in the graph.

**Usage Examples**:
```python
edges = graph.internal_edges
print(edges)
```

### Method: `is_empty`

**Signature**:
```python
def is_empty(self) -> bool:
```

**Return Values**:
- `bool`: True if the graph is empty (has no nodes), False otherwise.

**Description**:
Checks if the graph is empty.

**Usage Examples**:
```python
if graph.is_empty():
    print("Graph is empty")
```

### Method: `clear`

**Signature**:
```python
def clear(self):
```

**Description**:
Clears all nodes and edges from the graph.

**Usage Examples**:
```python
graph.clear()
print("Graph cleared")
```

### Method: `add_edge`

**Signature**:
```python
def add_edge(
    self,
    head: Node,
    tail: Node,
    condition: Condition | None = None,
    bundle=False,
    label=None,
    **kwargs
)
```

**Parameters**:
- `head` (Node): The head node of the edge.
- `tail` (Node): The tail node of the edge.
- `condition` (Condition, optional): The condition that must be met for the edge to be considered active. Default is `None`.
- `bundle` (bool, optional): Flag indicating if the edge is bundled. Default is `False`.
- `label` (str, optional): An optional label for the edge. Default is `None`.

**Description**:
Adds an edge between two nodes in the graph.

**Usage Examples**:
```python
graph.add_edge(head_node, tail_node, condition=my_condition, bundle=True, label="my_label")
print("Edge added")
```

### Method: `remove_edge`

**Signature**:
```python
def remove_edge(self, edge: Any) -> bool:
```

**Parameters**:
- `edge` (Any): The edge to remove.

**Return Values**:
- `bool`: True if the edge was successfully removed, False otherwise.

**Description**:
Removes an edge from the graph.

**Usage Examples**:
```python
success = graph.remove_edge(edge)
print("Edge removed:", success)
```

### Method: `add_node`

**Signature**:
```python
def add_node(self, node: Any) -> None:
```

**Parameters**:
- `node` (Any): The node to add.

**Description**:
Adds a node to the graph.

**Usage Examples**:
```python
graph.add_node(node)
print("Node added")
```

### Method: `get_node`

**Signature**:
```python
def get_node(self, item: LionIDable, default=...) -> Node:
```

**Parameters**:
- `item` (LionIDable): The identifier of the node.
- `default` (optional): The default value if the node is not found. Default is `...`.

**Return Values**:
- `Node`: The node with the specified identifier, or the default value if not found.

**Description**:
Gets a node from the graph by its identifier.

**Usage Examples**:
```python
node = graph.get_node(node_id)
print(node)
```

### Method: `get_node_edges`

**Signature**:
```python
def get_node_edges(
    self,
    node: Node | str,
    direction: str = "both",
    label: list | str = None,
) -> Pile[Edge] | None:
```

**Parameters**:
- `node` (Node | str): The node or its identifier.
- `direction` (str, optional): The direction of edges to retrieve ('both', 'head', 'tail'). Default is `both`.
- `label` (list | str, optional): The label(s) of the edges to retrieve. Default is `None`.

**Return Values**:
- `Pile[Edge] | None`: The pile of edges matching the criteria, or `None` if no edges match.

**Description**:
Gets the edges of a node in the specified direction and with the given label.

**Usage Examples**:
```python
edges = graph.get_node_edges(node, direction="out", label="my_label")
print(edges)
```

### Method: `pop_node`

**Signature**:
```python
def pop_node(self, item, default=...) -> Node:
```

**Parameters**:
- `item` (Any): The identifier of the node to remove and return.
- `default` (optional): The default value if the node is not found. Default is `...`.

**Return Values**:
- `Node`: The removed node, or the default value if not found.

**Description**:
Removes and returns a node from the graph by its identifier.

**Usage Examples**:
```python
node = graph.pop_node(node_id)
print("Node removed:", node)
```

### Method: `remove_node`

**Signature**:
```python
def remove_node(self, item) -> bool:
```

**Parameters**:
- `item` (Any): The identifier of the node to remove.

**Return Values**:
- `bool`: True if the node was successfully removed, False otherwise.

**Description**:
Removes a node from the graph by its identifier.

**Usage Examples**:
```python
success = graph.remove_node(node_id)
print("Node removed:", success)
```

### Method: `get_heads`

**Signature**:
```python
def get_heads(self) -> Pile:
```

**Return Values**:
- `Pile`: A pile of all head nodes in the graph.

**Description**:
Gets all head nodes in the graph.

**Usage Examples**:
```python
heads = graph.get_heads()
print(heads)
```

### Method: `is_acyclic`

**Signature**:
```python
def is_acyclic(self) -> bool:
```

**Return Values**:
- `bool`: True if the graph is acyclic (contains no cycles), False otherwise.

**Description**:
Checks if the graph is acyclic.

**Usage Examples**:
```python
if graph.is_acyclic():
    print("Graph is acyclic")
else:
    print("Graph contains cycles")
```

### Method: `to_networkx`

**Signature**:
```python
def to_networkx(self, **kwargs) -> Any:
```

**Return Values**:
- `Any`: The NetworkX graph object representing the graph.

**Description**:
Converts the graph to a NetworkX graph object.

**Usage Examples**:
```python
nx_graph = graph.to_networkx()
print(nx_graph)
```

### Method: `display`

**Signature**:
```python
def display(self, **kwargs):
```

**Description**:
Displays the graph using NetworkX and Matplotlib.

**Usage Examples**:
```python
graph.display()
```

### Method: `size`

**Signature**:
```python
def size(self) -> int:
```

**Return Values**:
- `int`: The number of nodes in the graph.

**Description**:
Returns the number of nodes in the graph.

**Usage Examples**:
```python
num_nodes = graph.size()
print("Number of nodes in the graph:", num_nodes)
```
