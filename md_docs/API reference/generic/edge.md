## Edge Class

Represents an edge between two nodes, potentially with a condition.

### Attributes
- `head (str)`: The identifier of the head node of the edge.
- `tail (str)`: The identifier of the tail node of the edge.
- `condition (Optional[Condition])`: An optional condition that must be met for the edge to be considered active.
- `label (Optional[str])`: An optional label for the edge.
- `bundle (bool)`: A flag indicating if the edge is bundled.

### Methods
- `_validate_head_tail()`: Validates the head and tail fields to ensure they are valid node identifiers.
- `check_condition(obj: dict[str, Any])`: Evaluates if the condition associated with the edge is met.
- `__str__()`: Returns a simple string representation of the edge.
- `__repr__()`: Returns a detailed string representation of the edge.
