
### Function: `to_llama_index_node`

**Description**:
Converts a Lion node to a Llama Index node of a specified type by transforming the node into a dictionary, modifying keys to match the expected Llama Index node schema, and creating a Llama Index node object of the specified type.

**Signature**:
```python
def to_llama_index_node(lion_node, node_type: Any = None, **kwargs: Any) -> Any
```

**Parameters**:
- `lion_node` (Any): The Lion node to convert. Must have a `to_dict` method.
- `node_type` (Any, optional): The type of Llama Index node to create. Can be a string name of a node class within the Llama Index schema or a class that inherits from `BaseNode`. Defaults to 'TextNode'.
- `**kwargs` (Any): Additional keyword arguments to be included in the Llama Index node's initialization.

**Returns**:
- `Any`: A new instance of the specified Llama Index node type populated with data from the Lion node.

**Raises**:
- `TypeError`: If `node_type` is neither a string nor a subclass of `BaseNode`.
- `AttributeError`: If an error occurs due to an invalid node type or during the creation of the node object.

**Usage Example**:
```python
class LionNode:
    def to_dict(self):
        return {"content": "Sample content", "node_id": "123"}

lion_node = LionNode()
llama_node = to_llama_index_node(lion_node)
print(llama_node)  # Output: Instance of TextNode with populated data
```

### Detailed Example

#### Example for `to_llama_index_node`

```python
# Assuming a LionNode class with a to_dict method
class LionNode:
    def to_dict(self):
        return {"content": "Sample content", "node_id": "123"}

# Convert LionNode to Llama Index TextNode
lion_node = LionNode()
llama_node = to_llama_index_node(lion_node)
print(llama_node)  # Output: Instance of TextNode with populated data
```
