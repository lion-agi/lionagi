
### Class: `Node`

**Description**:
`Node` represents a node in a graph structure, allowing connections to other nodes via edges. It extends `Component` by incorporating relational capabilities, enabling nodes to connect through directed edges representing incoming and outgoing relationships.

#### Attributes:
- `relations` (dict[str, Pile]): A dictionary holding `Pile` instances for incoming ('in') and outgoing ('out') edges.

### Method: `edges`

**Signature**:
```python
@property
def edges(self) -> Pile[Edge]:
```

**Return Values**:
- `Pile[Edge]`: A combined pile of all edges connected to this node.

**Description**:
Gets a unified view of all incoming and outgoing edges.

**Usage Examples**:
```python
edges = node.edges
print(edges)
```

### Method: `related_nodes`

**Signature**:
```python
@property
def related_nodes(self) -> list[str]:
```

**Return Values**:
- `list[str]`: A list of node IDs directly related to this node.

**Description**:
Gets a list of all unique node IDs directly related to this node.

**Usage Examples**:
```python
related_nodes = node.related_nodes
print(related_nodes)
```

### Method: `node_relations`

**Signature**:
```python
@property
def node_relations(self) -> dict:
```

**Return Values**:
- `dict`: A dictionary with keys 'in' and 'out', each containing a mapping of related node IDs to lists of edges representing relationships.

**Description**:
Gets a categorized view of direct relationships into groups.

**Usage Examples**:
```python
relations = node.node_relations
print(relations)
```

### Method: `predecessors`

**Signature**:
```python
@property
def predecessors(self) -> list[str]:
```

**Return Values**:
- `list[str]`: A list of node IDs that precede this node.

**Description**:
Gets a list of IDs of nodes with direct incoming relation to this node.

**Usage Examples**:
```python
predecessors = node.predecessors
print(predecessors)
```

### Method: `successors`

**Signature**:
```python
@property
def successors(self) -> list[str]:
```

**Return Values**:
- `list[str]`: A list of node IDs that succeed this node.

**Description**:
Gets a list of IDs of nodes with direct outgoing relation from this node.

**Usage Examples**:
```python
successors = node.successors
print(successors)
```

### Method: `relate`

**Signature**:
```python
def relate(
    self,
    node: "Node",
    direction: str = "out",
    condition: Condition | None = None,
    label: str | None = None,
    bundle: bool = False,
) -> None:
```

**Parameters**:
- `node` ("Node"): The target node to relate to.
- `direction` (str, optional): The direction of the edge ('in' or 'out'). Default is 'out'.
- `condition` (Condition, optional): An optional condition to associate with the edge. Default is `None`.
- `label` (str, optional): An optional label for the edge. Default is `None`.
- `bundle` (bool, optional): Whether to bundle the edge with others. Default is `False`.

**Description**:
Establishes a directed relationship from this node to another.

**Usage Examples**:
```python
node.relate(other_node, direction="out", condition=my_condition, label="my_label", bundle=True)
print("Nodes related")
```

### Method: `remove_edge`

**Signature**:
```python
def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
```

**Parameters**:
- `node` ("Node"): The other node involved in the edge.
- `edge` (Edge | str): The specific edge to remove or 'all' to remove all edges.

**Return Values**:
- `bool`: True if the edge(s) were successfully removed, False otherwise.

**Description**:
Removes the specified edge or all edges between this node and another node.

**Usage Examples**:
```python
success = node.remove_edge(other_node, edge)
print("Edge removed:", success)
```

### Method: `unrelate`

**Signature**:
```python
def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
```

**Parameters**:
- `node` ("Node"): The other node to unrelate from.
- `edge` (Edge | str, optional): The specific edge to remove or 'all' for all edges. Default is 'all'.

**Return Values**:
- `bool`: True if the relationships were successfully removed, False otherwise.

**Description**:
Removes all or specific relationships between this node and another node.

**Usage Examples**:
```python
success = node.unrelate(other_node, edge="all")
print("Nodes unrelated:", success)
```

### Method: `__str__`

**Signature**:
```python
def __str__(self) -> str:
```

**Return Values**:
- `str`: The string representation of the node.

**Description**:
Returns a string representation of the node, including the number of incoming and outgoing relations.

**Usage Examples**:
```python
print(node)
```

### Method: `__repr__`

**Signature**:
```python
def __repr__(self) -> str:
```

**Return Values**:
- `str`: The string representation of the node.

**Description**:
Returns a string representation of the node, including the number of incoming and outgoing relations.

**Usage Examples**:
```python
print(repr(node))
```
