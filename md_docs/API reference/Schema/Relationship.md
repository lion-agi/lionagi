## Relationship Class

> Child class of [[Base Component#^614ddc|BaseRelatableNode]]

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
