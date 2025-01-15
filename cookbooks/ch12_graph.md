# LionAGI Cookbook

## Chapter 12: Building a Knowledge Graph

In previous chapters, you built various systems. Now we'll explore graph operations by building a knowledge system that:
- Stores information nodes
- Manages relationships
- Enables traversal
- Supports queries

### Prerequisites
- Completed [Chapter 11](ch11_performance.md)
- Understanding of graph concepts
- Basic Python knowledge

## Graph Basics

### Node Management
```python
from lionagi import (
    Branch, Model, Session,
    Node, Edge, Graph,
    types
)
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json

class KnowledgeNode(Node):
    """Knowledge graph node."""
    def __init__(
        self,
        content: dict,
        node_type: str = "concept",
        embedding: List[float] = None
    ):
        super().__init__(
            content=content,
            node_type=node_type,
            embedding=embedding
        )
    
    def similarity(
        self,
        other: 'KnowledgeNode'
    ) -> float:
        """Compute node similarity."""
        if not (self.embedding and other.embedding):
            return 0.0
        
        # Cosine similarity
        import numpy as np
        a = np.array(self.embedding)
        b = np.array(other.embedding)
        return np.dot(a, b) / (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

class KnowledgeEdge(Edge):
    """Knowledge graph edge."""
    def __init__(
        self,
        head: str,
        tail: str,
        label: List[str],
        weight: float = 1.0
    ):
        super().__init__(
            head=head,
            tail=tail,
            label=label,
            properties={
                "weight": weight,
                "created": datetime.now().isoformat()
            }
        )
    
    @property
    def weight(self) -> float:
        """Get edge weight."""
        return self.properties["weight"]
    
    @weight.setter
    def weight(self, value: float):
        """Set edge weight."""
        if not 0 <= value <= 1:
            raise ValueError(
                "Weight must be between 0 and 1"
            )
        self.properties["weight"] = value
```

### Graph Operations
```python
class KnowledgeGraph(Graph):
    """Knowledge graph operations."""
    def __init__(self):
        super().__init__()
    
    def add_concept(
        self,
        name: str,
        content: dict,
        embedding: List[float] = None
    ) -> KnowledgeNode:
        """Add concept node."""
        node = KnowledgeNode(
            content={
                "name": name,
                **content
            },
            node_type="concept",
            embedding=embedding
        )
        self.add_node(node)
        return node
    
    def add_relationship(
        self,
        head: str,
        tail: str,
        label: str,
        weight: float = 1.0
    ) -> KnowledgeEdge:
        """Add relationship edge."""
        edge = KnowledgeEdge(
            head=head,
            tail=tail,
            label=[label],
            weight=weight
        )
        self.add_edge(edge)
        return edge
    
    def get_neighbors(
        self,
        node: KnowledgeNode,
        direction: str = "both"
    ) -> List[KnowledgeNode]:
        """Get neighboring nodes."""
        if direction == "out":
            return self.get_successors(node)
        elif direction == "in":
            return self.get_predecessors(node)
        else:
            return [
                *self.get_successors(node),
                *self.get_predecessors(node)
            ]
    
    def find_path(
        self,
        start: KnowledgeNode,
        end: KnowledgeNode,
        max_depth: int = 3
    ) -> List[KnowledgeNode]:
        """Find path between nodes."""
        visited = set()
        queue = [(start, [start])]
        
        while queue:
            node, path = queue.pop(0)
            if node == end:
                return path
            
            if len(path) >= max_depth:
                continue
            
            if node not in visited:
                visited.add(node)
                neighbors = self.get_neighbors(node)
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append(
                            (neighbor, path + [neighbor])
                        )
        
        return []  # No path found
    
    def find_similar(
        self,
        node: KnowledgeNode,
        min_similarity: float = 0.5
    ) -> List[KnowledgeNode]:
        """Find similar nodes."""
        similar = []
        for other in self.internal_nodes:
            if other != node:
                similarity = node.similarity(other)
                if similarity >= min_similarity:
                    similar.append((other, similarity))
        
        return sorted(
            similar,
            key=lambda x: x[1],
            reverse=True
        )
```

## Advanced Features

### Pattern Matching
```python
class PatternMatcher:
    """Match graph patterns."""
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
    
    def find_pattern(
        self,
        pattern: dict
    ) -> List[KnowledgeNode]:
        """Find nodes matching pattern."""
        matches = []
        for node in self.graph.internal_nodes:
            if self._matches_pattern(
                node.content,
                pattern
            ):
                matches.append(node)
        return matches
    
    def _matches_pattern(
        self,
        content: dict,
        pattern: dict
    ) -> bool:
        """Check if content matches pattern."""
        return all(
            k in content and content[k] == v
            for k, v in pattern.items()
        )
    
    def find_subgraph(
        self,
        nodes: List[KnowledgeNode],
        max_depth: int = 2
    ) -> KnowledgeGraph:
        """Extract subgraph around nodes."""
        subgraph = KnowledgeGraph()
        visited = set()
        queue = [(node, 0) for node in nodes]
        
        while queue:
            node, depth = queue.pop(0)
            if depth > max_depth:
                continue
            
            if node not in visited:
                visited.add(node)
                subgraph.add_node(node)
                
                # Add edges
                edges = self.graph.find_node_edge(
                    node,
                    direction="both"
                )
                for edge in edges:
                    head = self.graph.internal_nodes[edge.head]
                    tail = self.graph.internal_nodes[edge.tail]
                    
                    if head in visited and tail in visited:
                        subgraph.add_edge(edge)
                    
                    # Queue neighbors
                    if depth < max_depth:
                        neighbors = self.graph.get_neighbors(node)
                        for neighbor in neighbors:
                            if neighbor not in visited:
                                queue.append(
                                    (neighbor, depth + 1)
                                )
        
        return subgraph
```

### Knowledge System
```python
class KnowledgeSystem:
    """Complete knowledge system."""
    def __init__(
        self,
        name: str = "Knowledge",
        save_dir: str = "knowledge"
    ):
        # Create graph
        self.graph = KnowledgeGraph()
        
        # Create matcher
        self.matcher = PatternMatcher(self.graph)
        
        # Setup storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Track operations
        self.operations: List[dict] = []
    
    def add_knowledge(
        self,
        concept: str,
        content: dict,
        relationships: List[dict] = None
    ) -> dict:
        """Add knowledge to graph."""
        try:
            # Create node
            node = self.graph.add_concept(
                name=concept,
                content=content
            )
            
            # Add relationships
            edges = []
            if relationships:
                for rel in relationships:
                    edge = self.graph.add_relationship(
                        head=node.id,
                        tail=rel["target"],
                        label=rel["type"],
                        weight=rel.get("weight", 1.0)
                    )
                    edges.append(edge)
            
            # Record operation
            operation = {
                "type": "add",
                "node": node.id,
                "content": content,
                "edges": [e.id for e in edges],
                "timestamp": datetime.now().isoformat()
            }
            self.operations.append(operation)
            
            return {
                "status": "success",
                "node_id": node.id,
                "edges": [e.id for e in edges]
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def query_knowledge(
        self,
        pattern: dict = None,
        concept: str = None
    ) -> dict:
        """Query knowledge graph."""
        try:
            # Find matches
            if pattern:
                nodes = self.matcher.find_pattern(pattern)
            elif concept:
                nodes = self.matcher.find_pattern({
                    "name": concept
                })
            else:
                return {
                    "status": "error",
                    "error": "No query provided"
                }
            
            if not nodes:
                return {
                    "status": "success",
                    "matches": []
                }
            
            # Extract subgraph
            subgraph = self.matcher.find_subgraph(
                nodes,
                max_depth=2
            )
            
            # Record operation
            operation = {
                "type": "query",
                "pattern": pattern,
                "concept": concept,
                "matches": len(nodes),
                "timestamp": datetime.now().isoformat()
            }
            self.operations.append(operation)
            
            return {
                "status": "success",
                "matches": [
                    {
                        "id": n.id,
                        "content": n.content,
                        "type": n.node_type
                    }
                    for n in nodes
                ],
                "subgraph": {
                    "nodes": len(subgraph.internal_nodes),
                    "edges": len(subgraph.internal_edges)
                }
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def save(self):
        """Save knowledge graph."""
        # Save graph
        graph_file = self.save_dir / "graph.json"
        with open(graph_file, "w") as f:
            json.dump({
                "nodes": [
                    {
                        "id": n.id,
                        "content": n.content,
                        "type": n.node_type,
                        "embedding": n.embedding
                    }
                    for n in self.graph.internal_nodes
                ],
                "edges": [
                    {
                        "id": e.id,
                        "head": e.head,
                        "tail": e.tail,
                        "label": e.label,
                        "properties": e.properties
                    }
                    for e in self.graph.internal_edges
                ]
            }, f, indent=2)
        
        # Save operations
        ops_file = self.save_dir / "operations.json"
        with open(ops_file, "w") as f:
            json.dump(self.operations, f, indent=2)
    
    def load(self):
        """Load knowledge graph."""
        # Load graph
        graph_file = self.save_dir / "graph.json"
        if graph_file.exists():
            with open(graph_file) as f:
                data = json.load(f)
                
                # Load nodes
                for node in data["nodes"]:
                    self.graph.add_concept(
                        name=node["content"]["name"],
                        content=node["content"],
                        embedding=node["embedding"]
                    )
                
                # Load edges
                for edge in data["edges"]:
                    self.graph.add_relationship(
                        head=edge["head"],
                        tail=edge["tail"],
                        label=edge["label"][0],
                        weight=edge["properties"]["weight"]
                    )
        
        # Load operations
        ops_file = self.save_dir / "operations.json"
        if ops_file.exists():
            with open(ops_file) as f:
                self.operations = json.load(f)

# Usage
def build_knowledge():
    """Demo knowledge system."""
    # Create system
    system = KnowledgeSystem(
        name="AI Knowledge",
        save_dir="ai_knowledge"
    )
    
    # Add concepts
    concepts = [
        {
            "concept": "Machine Learning",
            "content": {
                "description": "Field of AI",
                "type": "technology"
            },
            "relationships": []
        },
        {
            "concept": "Deep Learning",
            "content": {
                "description": "Neural networks",
                "type": "technology"
            },
            "relationships": [
                {
                    "target": "concept_0",  # Machine Learning
                    "type": "subset_of",
                    "weight": 0.8
                }
            ]
        }
    ]
    
    # Add knowledge
    for concept in concepts:
        result = system.add_knowledge(
            concept=concept["concept"],
            content=concept["content"],
            relationships=concept["relationships"]
        )
        print(f"\nAdded {concept['concept']}:", result)
    
    # Query knowledge
    query = system.query_knowledge(
        pattern={"type": "technology"}
    )
    print("\nQuery result:", query)
    
    # Save system
    system.save()
    
    return system

# Build knowledge
system = build_knowledge()
```

## Best Practices

1. **Graph Design**
   - Define clear nodes
   - Use meaningful edges
   - Add proper weights
   - Enable traversal

2. **Pattern Design**
   - Keep patterns focused
   - Handle variations
   - Support matching
   - Enable extraction

3. **System Design**
   - Validate inputs
   - Track operations
   - Save state
   - Handle errors

## Quick Reference
```python
from lionagi import Node, Edge, Graph

# Create graph
graph = Graph()

# Add node
node = Node(content={"name": "Concept"})
graph.add_node(node)

# Add edge
edge = Edge(
    head=node1.id,
    tail=node2.id,
    label=["relates_to"]
)
graph.add_edge(edge)
```

## Next Steps

You've learned:
- How to build knowledge graphs
- How to manage relationships
- How to query patterns
- How to traverse graphs

This concludes our cookbook series. You now have a comprehensive understanding of LionAGI's features and can build sophisticated AI applications.
