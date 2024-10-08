# Graph Class Documentation

## Overview

The `Graph` class is a fundamental component of the Lion framework, designed to represent and manipulate graph structures. Inheriting from the `Node` class, it provides a robust set of methods for managing nodes and edges within a graph, supporting complex network analysis and operations.

## Class Definition

```python
class Graph(Node):
    internal_nodes: Pile = Field(
        default_factory=lambda: pile({}, {Node}),
        description="The internal nodes of the graph.",
    )
    internal_edges: Pile = Field(
        default_factory=lambda: pile({}, {Edge}),
        description="The internal edges of the graph.",
    )
    ...
```

## Key Features

1. Management of internal nodes and edges using `Pile` containers
2. Addition and removal of nodes and edges
3. Edge finding functionality based on node and direction
4. Identification of head nodes in the graph
5. Integration with the Lion framework's Node and Edge classes

## Attributes

- `internal_nodes` (Pile): A Pile containing the internal nodes of the graph.
- `internal_edges` (Pile): A Pile containing the internal edges of the graph.

## Methods

### Node Management

#### add_node(node: Node) -> None

Adds a node to the graph.

```python
graph = Graph()
node = Node()
graph.add_node(node)
```

Raises:
- `LionRelationError`: If the node already exists in the graph.

Note: This method uses the `insert` method of the `Pile` class, which ensures uniqueness based on the node's Lion ID.

#### remove_node(node: Node | str, delete: bool = False) -> None

Removes a node from the graph and optionally deletes it. This method also removes all edges connected to the node.

```python
graph.remove_node(node, delete=True)
```

Raises:
- `LionRelationError`: If the node is not found in the graph.

Note: When `delete=True`, the method not only removes the node and its edges from the graph but also deletes the objects from memory.

### Edge Management

#### remove_edge(edge: Edge | str, delete=False) -> None

Removes an edge from the graph and optionally deletes it.

```python
graph.remove_edge(edge, delete=True)
```

Raises:
- `LionRelationError`: If the edge is not found in the graph.

Note: This method only removes the edge from the graph. It does not affect the nodes connected by the edge.

### Graph Analysis

#### find_node_edge(node: Any, direction: Literal["both", "head", "tail"] = "both") -> dict[str : Pile[Edge]]

Finds edges connected to a node in a specific direction. This method is crucial for analyzing the graph structure and navigating between nodes.

```python
node = Node()
graph.add_node(node)
# Assume we've added more nodes and edges to the graph
edges = graph.find_node_edge(node, direction="both")
incoming_edges = edges.get("head", pile())
outgoing_edges = edges.get("tail", pile())
```

Args:
- `node`: The node to find edges for. Can be a Node object or its Lion ID.
- `direction`: The direction to search ("both", "head", or "tail").
  - "head": Find edges where the given node is the tail (incoming edges)
  - "tail": Find edges where the given node is the head (outgoing edges)
  - "both": Find both incoming and outgoing edges

Returns:
- A dictionary with keys "head" and/or "tail", each containing a Pile of Edges.

Note: This method uses the `Note` class for intermediate data storage, showcasing the integration between different components of the Lion framework.

#### get_heads() -> Pile

Gets all head nodes in the graph. Head nodes are nodes with no incoming edges, except for nodes that are instances of the `Event` class.

```python
head_nodes = graph.get_heads()
for head in head_nodes:
    print(f"Head node: {head.ln_id}")
```

Returns:
- A Pile containing all head nodes.

Note: The `is_head` function used internally checks if a node is an instance of `Event`. If it is, it's not considered a head node regardless of its connections. This special handling of `Event` nodes allows for representation of specific graph structures where events are treated differently from regular nodes.

## Integration with Lion Framework

The Graph class is deeply integrated with other components of the Lion framework:

1. It inherits from `Node`, allowing graphs to be treated as nodes in larger structures.
2. It uses `Pile` for efficient storage and manipulation of nodes and edges.
3. It works with `Edge` objects to represent connections between nodes.
4. It utilizes `Note` for intermediate data storage in some methods.
5. It incorporates special handling for `Event` objects in head node determination.

This integration allows for complex graph structures and operations within the Lion framework ecosystem.

## Performance Considerations

- The use of `Pile` for storing nodes and edges provides efficient access and manipulation, especially for large graphs.
- The `find_node_edge` method constructs a new dictionary and Piles for each call. For frequent access to edge information, consider caching results if the graph structure is not changing frequently.
- Adding and removing nodes and edges are generally O(1) operations due to the underlying `Pile` implementation.
- The `get_heads` method iterates over all nodes, which can be time-consuming for very large graphs. Consider caching this result if the graph structure is stable.

## Best Practices and Error Handling

1. Always check for the existence of nodes and edges before operations:

```python
try:
    graph.remove_node(node)
except LionRelationError as e:
    print(f"Node not found in graph: {e}")
    # Handle the error appropriately
```

2. When adding nodes or edges, be prepared to handle `LionRelationError` for duplicate items:

```python
try:
    graph.add_node(node)
except LionRelationError as e:
    print(f"Node already exists in graph: {e}")
    # Decide whether to ignore, update, or handle differently
```

3. When working with large graphs, consider the performance implications of operations like `get_heads()`. Implement caching mechanisms if appropriate for your use case.

4. Be mindful of the `delete` parameter in `remove_node` and `remove_edge`. Use it judiciously to avoid unintended memory management issues.

5. When using `find_node_edge`, always check if the returned dictionary contains the keys you expect:

```python
edges = graph.find_node_edge(node, direction="both")
incoming_edges = edges.get("head", pile())
if not incoming_edges:
    print("No incoming edges found for this node")
```

By following these practices and understanding the Graph class's role in the Lion framework, you can effectively model and manipulate complex graph structures in your applications.
