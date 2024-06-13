
### Class: `Tree`

**Parent Class:** [[Graph#^0ac258|Graph]]

**Description**:
`Tree` represents a tree structure extending the `Graph` class with tree-specific functionalities. It manages parent-child relationships within the tree.

#### Attributes:
- `root` (TreeNode | None): The root node of the tree. Defaults to `None`.

### `relate_parent_child`

**Signature**:
```python
def relate_parent_child(
    self,
    parent: TreeNode,
    children: list[TreeNode],
    condition: Condition | None = None,
    bundle: bool = False,
) -> None:
```

**Parameters**:
- `parent` (TreeNode): The parent node.
- `children` (list\[[[Tree Node#^f078e8|TreeNode]]\]): A list of child nodes.
- `condition` (Condition | None, optional): The condition associated with the relationships, if any. Default is `None`.
- `bundle` (bool, optional): Indicates whether to bundle the relations into a single transaction. Default is `False`.

**Description**:
Establishes parent-child relationships between the given parent and child node(s).

**Usage Examples**:
```python
# Assuming TreeNode and Condition are already defined
parent_node = TreeNode(...)
child_nodes = [TreeNode(...), TreeNode(...)]
tree = Tree()

tree.relate_parent_child(parent_node, child_nodes, condition=my_condition, bundle=True)
print("Parent-child relationships established")
```
