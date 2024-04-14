## Relations Class

Represents the relationships of a node via its incoming and outgoing [[edge]], encapsulating the edge management within a graph structure.

### Attributes
- `points_to (dict[str, Edge])`: Outgoing edges from the node, representing edges leading from this node to other nodes.
- `pointed_by (dict[str, Edge])`: Incoming edges to the node, representing edges from other nodes leading to this node.

### Properties
- `all_edges`: Combines and returns all incoming and outgoing edges connected to the node.
- `all_nodes`: Extracts and returns a unique set of all node IDs connected to this node through its edges.

### Description
This class stores edges in two dictionaries — `points_to` for outgoing edges and `pointed_by` for incoming edges. It provides an organized way to access all edges together and to get a unique set of all connected node IDs.
