from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Node:
    id: str
    properties: Dict[str, Any]

@dataclass
class Edge:
    source: str
    target: str
    type: str
    properties: Dict[str, Any]

class MockGraphDB:
    """Mock implementation of a graph database for testing."""
    
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []
        
    def add_node(self, id: str, properties: Dict[str, Any]) -> None:
        """Add a node with properties."""
        self._nodes[id] = Node(id=id, properties=properties)
        
    def add_edge(self, source: str, target: str, type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Add an edge between nodes."""
        if source not in self._nodes or target not in self._nodes:
            raise ValueError("Source or target node does not exist")
        self._edges.append(Edge(source, target, type, properties or {}))
        
    def get_node(self, id: str) -> Optional[Node]:
        """Retrieve a node by ID."""
        return self._nodes.get(id)
        
    def get_edges(self, source: Optional[str] = None, target: Optional[str] = None) -> List[Edge]:
        """Get edges, optionally filtered by source/target."""
        edges = self._edges
        if source:
            edges = [e for e in edges if e.source == source]
        if target:
            edges = [e for e in edges if e.target == target]
        return edges
        
    def delete_node(self, id: str) -> None:
        """Delete a node and its connected edges."""
        self._nodes.pop(id, None)
        self._edges = [e for e in self._edges 
                      if e.source != id and e.target != id]
                      
    def clear(self) -> None:
        """Clear all data."""
        self._nodes.clear()
        self._edges.clear()
