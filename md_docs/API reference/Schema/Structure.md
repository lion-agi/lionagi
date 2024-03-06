---
tags:
  - API
  - Graph
  - Relationship
created: 2024-02-26
completed: true
---

# Structure Module API Reference

## Structure Class

> Child class of [[Base Component#^614ddc|BaseRelatableNode]]

Represents the overall structure of a graph, facilitating interactions with the [[Graph]] class at a higher level of abstraction.

### Attributes

- **graph (Graph):** An instance of the `Graph` class that holds the graph structure, including nodes and relationships.

### Methods

#### add_node(node: [[Base Nodes#^50e3bb|BaseNode]]) -> None

Adds a node to the graph structure.

**Parameters:**
- `node`: The `BaseNode` instance to be added.

**Example:**

```python
node = BaseNode(id_="node3")
structure = Structure()
structure.add_node(node)
```

#### add_relationship(relationship: [[Relationship]]) -> None

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

