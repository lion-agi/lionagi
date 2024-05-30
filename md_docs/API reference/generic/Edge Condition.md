
### Class: `EdgeCondition`

**Parent Class:** [[API reference/collections/abc/Concepts#^d5e7b6|Condition]], `pydantic.BaseModel`

^c25416

**Description**:
`EdgeCondition` is a subclass of `Condition` and `BaseModel` that represents the condition associated with an edge in a graph. It includes a source attribute for the condition check and allows extra fields through the model configuration settings.

#### Attributes:
- `source` (Any): The source for the condition check.

### Configuration:
- **extra**: Set to `"allow"`, permitting extra fields to be included in the model.

### Usage Examples:
```python
# Example of creating an EdgeCondition instance
edge_condition = EdgeCondition(source=some_source)
print(edge_condition.source)
```
