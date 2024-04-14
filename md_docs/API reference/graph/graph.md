Extends the [[component#^f10cc7|BaseStructure]] class, representing a graph structure with additional graph-specific properties and methods.

### Methods
- `get_heads()`: Retrieves the head nodes of the graph, which are nodes with no incoming edges.
- `acyclic`: Checks if the graph is acyclic, i.e., it contains no cycles and can be represented as a **Directed Acyclic Graph (DAG).**
- `to_networkx(**kwargs)`: Converts the graph into a NetworkX graph object for further analysis or visualization.
- `display(**kwargs)`: Displays the graph using NetworkX's drawing capabilities, requiring NetworkX and a compatible plotting library (like matplotlib) to be installed.

### Description
The Graph class provides capabilities for managing and querying complex graph structures. It includes advanced functionalities like detecting head nodes, checking for acyclicity, and easy conversion to NetworkX for detailed analysis and visualization.
