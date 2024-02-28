---
tags:
  - API
  - Graph
  - Relationship
created: 2024-02-26
completed: true
---

# Structure Module API Reference


## Relationship Class

> Child class of [[Base Nodes#^614ddc|BaseRelatableNode]]

Represents a relationship between two nodes in a graph, extending `BaseRelatableNode`. It models connections with additional conditions, suitable for complex graph structures.

### Attributes

- **source_node_id (str):** Identifier for the source node.
- **target_node_id (str):** Identifier for the target node.
- **condition (Dict[str, Any] = {}):** Conditions associated with the relationship.

### Methods

#### add_condition(condition: Dict[str, Any]) -> None

Adds a condition to the relationship. Conditions are additional metadata that define the relationship.

**Parameters:**
- `condition`: A dictionary representing the condition to add.

**Example:**

```python
relationship = Relationship(source_node_id="node1", target_node_id="node2")
relationship.add_condition({"status": "active"})
```

#### remove_condition(condition_key: str) -> Any

Removes a condition from the relationship by its key.

**Parameters:**
- `condition_key`: The key of the condition to remove.

**Returns:** The value of the removed condition.

**Example:**

```python
relationship.add_condition({"status": "active"})
print(relationship.remove_condition("status"))  # Output: "active"
```

#### condition_exists(condition_key: str) -> bool

Checks if a specific condition exists within the relationship.

**Parameters:**
- `condition_key`: The key of the condition to check.

**Returns:** True if the condition exists, False otherwise.

**Example:**

```python
print(relationship.condition_exists("status"))  # Output: False
```

#### get_condition(condition_key: str | None = None) -> Any

Retrieves a specific condition or all conditions if no key is provided.

**Parameters:**
- `condition_key`: Optional; the key of the condition to retrieve.

**Returns:** The requested condition or all conditions.

**Example:**

```python
relationship.add_condition({"priority": "high"})
print(relationship.get_condition("priority"))  # Output: "high"
print(relationship.get_condition())  # Output: {"priority": "high"}
```

### Usage

The `Relationship` class is vital for defining and manipulating the connections between nodes in graph-based data structures, allowing for the representation of complex network topologies.


## Graph Class

> Child class of [[Base Nodes#^614ddc|BaseRelatableNode]]

Models a graph structure, encapsulating nodes and their relationships, and provides functionalities for managing graph data.

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


## Structure Class

> Child class of [[Base Nodes#^614ddc|BaseRelatableNode]]

Represents the overall structure of a graph, facilitating interactions with the `Graph` class at a higher level of abstraction.

### Attributes

- **graph (Graph):** An instance of the `Graph` class that holds the graph structure, including nodes and relationships.

### Methods

#### add_node(node: BaseNode) -> None

Adds a node to the graph structure.

**Parameters:**
- `node`: The `BaseNode` instance to be added.

**Example:**

```python
node = BaseNode(id_="node3")
structure = Structure()
structure.add_node(node)
```

#### add_relationship(relationship: Relationship) -> None

Adds a relationship between nodes in the graph structure.

**Parameters:**
- `relationship`: The `Relationship` instance to be added.

**Example:**

```python
relationship = Relationship(source_node_id="node1", target_node_id="node3")
structure.add_relationship(relationship)
```

#### get_relationships() -> list[Relationship]

Retrieves all relationships in the graph structure.

**Example:**

```python
all_relationships = structure.get_relationships()
```

#### get_node_relationships(node: BaseNode, out_edge=True, labels=None) -> List[Relationship]

Gets relationships associated with a specific node, optionally filtered by direction and labels.

**Parameters:**
- `node`: The node whose relationships to retrieve.
- `out_edge`: Whether to retrieve outgoing relationships.
- `labels`: Optional; filter relationships by labels.

**Example:**

```python
node_relationships = structure.get_node_relationships(node, out_edge=True)
```

#### node_exist(node: BaseNode) -> bool

Checks if a node exists within the graph structure.

**Parameters:**
- `node`: The `BaseNode` instance to check.

**Example:**

```python
exists = structure.node_exist(node)
```

#### relationship_exist(relationship: Relationship) -> bool

Determines if a relationship exists within the graph structure.

**Parameters:**
- `relationship`: The `Relationship` instance to check.

**Example:**

```python
exists = structure.relationship_exist(relationship)
```

#### remove_node(node: BaseNode) -> BaseNode

Removes a node and its associated relationships from the graph structure.

**Parameters:**
- `node`: The `BaseNode` instance to be removed.

**Example:**

```python
removed_node = structure.remove_node(node)
```

#### remove_relationship(relationship: Relationship) -> Relationship

Removes a relationship from the graph structure.

**Parameters:**
- `relationship`: The `Relationship` instance to be removed.

**Example:**

```python
removed_relationship = structure.remove_relationship(relationship)
```

#### is_empty() -> bool

Checks if the graph structure is empty, containing no nodes or relationships.

**Example:**

```python
empty = structure.is_empty()
```

### Usage

The `Structure` class simplifies the management of graph structures, allowing for easy integration of graph functionality into larger applications.

