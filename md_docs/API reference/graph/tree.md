## TreeLabel Enumeration

Defines the types of relationships in a tree structure.

### Members
- `PARENT (str)`: Represents the parent relationship.
- `CHILD (str)`: Represents the child relationship.

## TreeNode Class

Extends the Node class to represent a node within a tree structure, including parent-child relationships.

### Attributes
- `parent (Node | None)`: The parent node, establishing the tree hierarchy.

### Methods
- `children()`: Retrieves the IDs of all child nodes.
- `relate_child(child, condition, bundle)`: Establishes a parent-child relationship.
- `relate_parent(parent, condition, bundle)`: Establishes a child to parent relationship, defining this node as the child.
- `unrelate_parent()`: Removes the parent relationship of this node.
- `unrelate_child(child)`: Removes the child relationship for specified child nodes.

## Tree Class

Represents a tree structure, extending from Graph, and incorporates tree-specific functionalities.

### Attributes
- `root (TreeNode | None)`: The root node of the tree.

### Methods
- `relate_parent_child(parent, children, condition, bundle)`: Establishes parent-child relationships between a given parent node and child nodes.

### Description
The Tree class provides methods to manage and query a tree structure effectively, handling complex scenarios involving parent-child dynamics.
