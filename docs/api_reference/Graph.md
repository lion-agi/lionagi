# Graph System API Reference

## Overview

The Graph system implements a directed graph with:
- Nodes storing content and embeddings
- Edges supporting conditional traversal and properties
- Graph operations for structure management and analysis

## Components

### Node
```python
class Node(Element, Relational):
    """Graph vertex with content and embedding storage."""
    
    content: Any = None              # Arbitrary content
    embedding: list[float] | None = None  # Vector representation
    
    def adapt_to(self, obj_key: str, many: bool = False, **kwargs) -> Any:
        """Convert node to external format."""
        
    @classmethod
    def adapt_from(cls, obj: Any, obj_key: str, many: bool = False, **kwargs) -> "Node":
        """Create node from external format."""

# Usage
node = Node(
    id="start",
    content={"type": "process", "data": "Start"},
    embedding=[0.1, 0.2, 0.3]
)
```

### Edge
```python
class Edge(Element):
    """Directed edge with traversal conditions."""
    
    head: IDType           # Source node ID
    tail: IDType           # Target node ID
    properties: dict       # Custom properties
    
    async def check_condition(self, *args, **kwargs) -> bool:
        """Verify traversal conditions."""

# Usage
edge = Edge(
    head="node1",
    tail="node2", 
    label=["flow"],
    condition=EdgeCondition(source=lambda x: x > 0)
)
```

### Graph
```python
class Graph(Element, Relational):
    """Directed graph management."""
    
    def add_node(self, node: Relational) -> None:
        """Add node to graph."""
        
    def add_edge(self, edge: Edge) -> None:
        """Add edge between nodes."""
        
    def get_successors(self, node: Node) -> Pile[Node]:
        """Get nodes connected from given node."""
        
    def get_predecessors(self, node: Node) -> Pile[Node]:
        """Get nodes connected to given node."""
        
    def is_acyclic(self) -> bool:
        """Check for cycles in graph."""

# Usage
graph = Graph()
graph.add_node(node1)
graph.add_node(node2)
graph.add_edge(Edge(head=node1.id, tail=node2.id))
```

## Common Operations

### Building Graphs
```python
# Create structure
graph = Graph()

# Add process nodes
start = Node(id="start", content="Start Process")
process = Node(id="process", content="Processing")
end = Node(id="end", content="End Process")

# Add all nodes
for node in [start, process, end]:
    graph.add_node(node)

# Connect with edges
edges = [
    Edge(head=start.id, tail=process.id),
    Edge(head=process.id, tail=end.id)
]
for edge in edges:
    graph.add_edge(edge)
```

### Conditional Flow
```python
# Add conditional branching
condition = EdgeCondition(source=lambda x: x.get("status") == "success")
alt_path = Edge(
    head=process.id,
    tail=end.id,
    condition=condition,
    label=["alternate"]
)

# Check condition
can_traverse = await alt_path.check_condition({"status": "success"})
```

### Analysis
```python
# Structure validation
if graph.is_acyclic():
    # Find entry points
    start_nodes = graph.get_heads()
    
    # Get node connections
    next_steps = graph.get_successors(start)
    previous_steps = graph.get_predecessors(end)
```

## Error Handling
```python
try:
    # Add edge
    graph.add_edge(edge)
except RelationError as e:
    # Handle missing nodes or invalid structure
    logging.error(f"Invalid edge: {e}")

try:
    # Check condition
    await edge.check_condition(data)
except ValueError as e:
    # Handle condition evaluation error
    logging.error(f"Condition check failed: {e}")
```
