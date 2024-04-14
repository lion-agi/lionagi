## BaseStructure Class

Extends the Node class, representing a node with internal edges and nodes, including methods for managing them.

### Attributes
- `internal_nodes (dict[str, Node])`: A dictionary of all nodes within the structure, keyed by node ID.

### Properties
- `internal_edges`: Retrieves all internal edges indexed by their ID.
- `is_empty`: Checks if the structure is empty (contains no nodes).

### Methods
- `clear()`: Clears all nodes and edges from the structure.
- `get_node_edges(node, node_as, label)`: Retrieves edges associated with a specific node.
- `relate_nodes(head, tail, condition, bundle, label)`: Relates two nodes within the structure with an edge.
- `remove_edge(edge)`: Removes one or more edges from the structure.
- `add_node(node)`: Adds a node to the internal structure.
- `remove_node(node)`: Removes a node from the internal structure.
- `get_node(node, default)`: Retrieves one or more nodes by ID or node instance.
- `pop_node(node, default)`: Retrieves and removes a node from the structure.

### Description
Provides functionality for adding, removing, and querying nodes and edges within the structure, as well as checking if the structure is empty. It handles complex scenarios involving multiple node and edge types, offering robust tools for dynamic structure management.
