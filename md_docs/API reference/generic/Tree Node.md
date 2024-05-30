
### Class: `TreeLabel`

**Parent Class:** `Enum`

**Description**:
`TreeLabel` is an enumeration representing tree relationships. It extends `str` and `Enum`.

#### Enum Values:
- `PARENT`: Represents a parent relationship in the tree.
- `CHILD`: Represents a child relationship in the tree.

### Class: `TreeNode`

^f078e8

**Description**:
`TreeNode` represents a node in a tree structure. It extends `Node` and manages parent-child relationships within the tree.

#### Attributes:
- `parent` (Node | None): The parent node, as an instance of `Node`.

### `children`

**Signature**:
```python
@property
def children() -> list[str]:
```

**Return Values**:
- `list[str]`: A list of child node IDs.

**Description**:
Returns a list of child node IDs. If the node has no parent, returns all related node IDs. Otherwise, returns related node IDs excluding the parent node.

**Usage Examples**:
```python
tree_node = TreeNode(...)
children_ids = tree_node.children
print(children_ids)
```

### `relate_child`

**Signature**:
```python
def relate_child(
    self,
    node: Node | list[Node],
    condition: Condition | None = None,
    bundle: bool = False,
) -> None:
```

**Parameters**:
- `node` (Node | list[Node]): The node or list of nodes to establish a parent-child relationship with.
- `condition` (Condition | None, optional): The condition associated with the relationship, if any. Default is `None`.
- `bundle` (bool, optional): Indicates whether to bundle the relations into a single transaction. Default is `False`.

**Description**:
Establishes a parent-child relationship with the given node(s). Updates the parent attribute of child nodes if they are instances of `TreeNode`.

**Usage Examples**:
```python
parent_node = TreeNode(...)
child_node = TreeNode(...)

parent_node.relate_child(child_node)
print(child_node.parent)  # Outputs the parent node
```

### `relate_parent`

**Signature**:
```python
def relate_parent(
    self,
    node: Node,
    condition: Condition | None = None,
    bundle: bool = False,
) -> None:
```

**Parameters**:
- `node` (Node): The parent node to establish a parent-child relationship with.
- `condition` (Condition | None, optional): The condition associated with the relationship, if any. Default is `None`.
- `bundle` (bool, optional): Indicates whether to bundle the relations into a single transaction. Default is `False`.

**Description**:
Establishes a parent-child relationship with the given parent node. Removes any existing parent-child relationship before establishing the new one.

**Usage Examples**:
```python
child_node = TreeNode(...)
parent_node = TreeNode(...)

child_node.relate_parent(parent_node)
print(child_node.parent)  # Outputs the parent node
```

### `unrelate_parent`

**Signature**:
```python
def unrelate_parent() -> None:
```

**Description**:
Removes the parent-child relationship with the parent node.

**Usage Examples**:
```python
child_node = TreeNode(...)
child_node.unrelate_parent()
print(child_node.parent)  # Outputs None
```

### `unrelate_child`

**Signature**:
```python
def unrelate_child(child: Node | list[Node]) -> None:
```

**Parameters**:
- `child` (Node | list[Node]): The child node or list of child nodes to remove the parent-child relationship with.

**Description**:
Removes the parent-child relationship with the given child node(s). Updates the parent attribute of child nodes if they are instances of `TreeNode`.

**Usage Examples**:
```python
parent_node = TreeNode(...)
child_node = TreeNode(...)

parent_node.unrelate_child(child_node)
print(child_node.parent)  # Outputs None
```
