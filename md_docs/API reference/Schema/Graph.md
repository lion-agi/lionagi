
## Graph Class

> Child class of [[Base Component#^614ddc|BaseRelatableNode]]

Models a graph structure, encapsulating nodes and their [[Relationship]], and provides functionalities for managing graph data.

### Attributes

- **nodes (Dict[str, BaseNode]):** Maps node IDs to `BaseNode` instances.
- **relationships (Dict[str, Relationship]):** Maps relationship IDs to `Relationship` instances.
- **node_relationships (Dict[str, Dict[str, Dict[str, str]]]):** Tracks relationships for each node.

### Methods

#### add_node(node: BaseNode) -> None

Adds a node to the graph.

**Parameters:**
- `node`: The `BaseNode` instance to add.

**Example:**

```python
node = BaseNode(id_="node1")
graph = Graph()
graph.add_node(node)
```

#### add_relationship(relationship: Relationship) -> None

Introduces a relationship between nodes in the graph.

**Parameters:**
- `relationship`: The `Relationship` instance to add.

**Example:**

```python
relationship = Relationship(source_node_id="node1", target_node_id="node2")
graph.add_relationship(relationship)
```

#### get_node_relationships(node: BaseNode = None, out_edge=True) -> List[Relationship]

Retrieves relationships for a specific node or all relationships in the graph.

**Parameters:**
- `node`: Optional; the node whose relationships to retrieve.
- `out_edge`: Whether to retrieve outgoing relationships.

**Example:**

```python
relationships = graph.get_node_relationships(node)
```

#### remove_node(node: BaseNode) -> BaseNode

Removes a node and its associated relationships from the graph.

**Parameters:**
- `node`: The `BaseNode` instance to remove.

**Example:**

```python
removed_node = graph.remove_node(node)
```

#### remove_relationship(relationship: Relationship) -> Relationship

Eliminates a relationship from the graph.

**Parameters:**
- `relationship`: The `Relationship` instance to remove.

**Example:**

```python
removed_relationship = graph.remove_relationship(relationship)
```

#### node_exist(node: BaseNode) -> bool

Checks if a node exists within the graph.

**Parameters:**
- `node`: The `BaseNode` instance to check.

**Example:**

```python
exists = graph.node_exist(node)
```

#### relationship_exist(relationship: Relationship) -> bool

Determines if a relationship exists within the graph.

**Parameters:**
- `relationship`: The `Relationship` instance to check.

**Example:**

```python
exists = graph.relationship_exist(relationship)
```

#### is_empty() -> bool

Determines if the graph is empty.

**Example:**

```python
empty = graph.is_empty()
```

#### clear() -> None

Clears the graph of all nodes and relationships.

**Example:**

```python
graph.clear()
```

#### to_networkx(**kwargs) -> Any

Converts the graph into a NetworkX graph object.

**Example:**

```python
nx_graph = graph.to_networkx()
```

### Usage

The `Graph` class is essential for creating and managing graph-based data structures, enabling complex graph operations and analyses.

