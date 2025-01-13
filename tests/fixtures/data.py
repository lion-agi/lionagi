from typing import Any, Dict, List

import numpy as np


def generate_test_documents() -> list[dict[str, Any]]:
    """Generate sample documents for testing.

    Returns:
        List of documents with text content and metadata.
    """
    return [
        {
            "id": "doc1",
            "text": "The quick brown fox jumps over the lazy dog",
            "metadata": {"source": "test", "category": "sample"},
            "vector": np.random.rand(128),  # Random embedding
        },
        {
            "id": "doc2",
            "text": "Lorem ipsum dolor sit amet",
            "metadata": {"source": "test", "category": "lorem"},
            "vector": np.random.rand(128),
        },
        {
            "id": "doc3",
            "text": "Testing document number three",
            "metadata": {"source": "test", "category": "sample"},
            "vector": np.random.rand(128),
        },
    ]
