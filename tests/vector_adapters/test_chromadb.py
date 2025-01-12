import pytest
from unittest.mock import Mock, patch
from lionagi.service.adapters.vector_adapters.chroma_vector_adapter import ChromaVectorAdapter

@pytest.fixture
def mock_vector_db():
    return Mock()

@pytest.fixture
def test_documents():
    return [
        {"id": "1", "content": "test doc 1", "metadata": {"type": "test"}},
        {"id": "2", "content": "test doc 2", "metadata": {"type": "test"}}
    ]

def test_chroma_from_obj(mock_vector_db, test_documents):
    adapter = ChromaVectorAdapter(client=mock_vector_db)
    adapter.from_obj(test_documents)
    mock_vector_db.add.assert_called_once()

def test_chroma_to_obj(mock_vector_db, test_documents):
    adapter = ChromaVectorAdapter(client=mock_vector_db)
    mock_vector_db.get.return_value = {
        "ids": ["1", "2"],
        "documents": ["test doc 1", "test doc 2"],
        "metadatas": [{"type": "test"}, {"type": "test"}]
    }
    result = adapter.to_obj()
    assert len(result) == len(test_documents)
    mock_vector_db.get.assert_called_once()

def test_chroma_query(mock_vector_db, test_documents):
    adapter = ChromaVectorAdapter(client=mock_vector_db)
    mock_vector_db.query.return_value = {
        "ids": ["1"],
        "documents": ["test doc 1"],
        "metadatas": [{"type": "test"}],
        "distances": [0.1]
    }
    
    results = adapter.query("test query", n_results=1)
    assert len(results) == 1
    mock_vector_db.query.assert_called_once()

def test_chroma_error_handling(mock_vector_db):
    adapter = ChromaVectorAdapter(client=mock_vector_db)
    mock_vector_db.add.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        adapter.from_obj([{"id": "1", "content": "test"}])
