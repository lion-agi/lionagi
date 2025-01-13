from unittest.mock import Mock, patch

import pytest

from lionagi.service.adapters.vector_adapters.qdrant_vector_adapter import (
    QdrantVectorAdapter,
)


@pytest.fixture
def mock_vector_db():
    return Mock()


@pytest.fixture
def test_documents():
    return [
        {
            "id": "1",
            "content": "test doc 1",
            "metadata": {"type": "test"},
            "vector": [0.1, 0.2, 0.3],
        },
        {
            "id": "2",
            "content": "test doc 2",
            "metadata": {"type": "test"},
            "vector": [0.4, 0.5, 0.6],
        },
    ]


def test_qdrant_from_obj(mock_vector_db, test_documents):
    adapter = QdrantVectorAdapter(client=mock_vector_db)
    adapter.from_obj(test_documents)
    mock_vector_db.upsert.assert_called_once()


def test_qdrant_to_obj(mock_vector_db, test_documents):
    adapter = QdrantVectorAdapter(client=mock_vector_db)
    mock_vector_db.scroll.return_value = (test_documents, None)
    result = adapter.to_obj()
    assert len(result) == len(test_documents)
    mock_vector_db.scroll.assert_called_once()


def test_qdrant_search(mock_vector_db, test_documents):
    adapter = QdrantVectorAdapter(client=mock_vector_db)
    query_vector = [0.1, 0.2, 0.3]
    mock_vector_db.search.return_value = test_documents

    results = adapter.search(query_vector, limit=2)
    assert len(results) == len(test_documents)
    mock_vector_db.search.assert_called_once()


def test_qdrant_error_handling(mock_vector_db):
    adapter = QdrantVectorAdapter(client=mock_vector_db)
    mock_vector_db.upsert.side_effect = Exception("DB Error")

    with pytest.raises(Exception):
        adapter.from_obj([{"id": "1", "vector": [0.1, 0.2, 0.3]}])
