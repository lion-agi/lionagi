from typing import Dict, List, Optional, Any
import numpy as np

class MockVectorDB:
    """Mock implementation of a vector database for testing."""
    
    def __init__(self):
        self._vectors: Dict[str, np.ndarray] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def add(self, id: str, vector: np.ndarray, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a vector with optional metadata."""
        self._vectors[id] = vector
        if metadata:
            self._metadata[id] = metadata
            
    def get(self, id: str) -> tuple[Optional[np.ndarray], Optional[Dict[str, Any]]]:
        """Retrieve a vector and its metadata by ID."""
        return self._vectors.get(id), self._metadata.get(id)
    
    def delete(self, id: str) -> None:
        """Delete a vector and its metadata."""
        self._vectors.pop(id, None)
        self._metadata.pop(id, None)
        
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[tuple[str, float]]:
        """Simple cosine similarity search."""
        results = []
        for id, vector in self._vectors.items():
            similarity = np.dot(query_vector, vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(vector)
            )
            results.append((id, float(similarity)))
        return sorted(results, key=lambda x: x[1], reverse=True)[:k]
    
    def clear(self) -> None:
        """Clear all data."""
        self._vectors.clear()
        self._metadata.clear()
