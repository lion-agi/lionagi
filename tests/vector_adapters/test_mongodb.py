import pytest
from unittest.mock import Mock, patch
from lionagi.service.adapters.vector_adapters.mongo_vector_adapter import MongoVectorAdapter

@pytest.fixture
def mock_vector_db():
    return Mock()

@pytest.fixture
def test_documents():
    return [
        {"id": "1", "content": "test doc 1", "metadata": {"type": "test"}},
        {"id": "2", "content": "test doc 2", "metadata": {"type": "test"}}
    ]

def test_mongo_from_obj(mock_vector_db, test_documents):
    adapter = MongoVectorAdapter(client=mock_vector_db)
    adapter.from_obj(test_documents)
    mock_vector_db.insert_many.assert_called_once()

def test_mongo_to_obj(mock_vector_db, test_documents):
    adapter = MongoVectorAdapter(client=mock_vector_db)
    mock_vector_db.find.return_value = test_documents
    result = adapter.to_obj()
    assert len(result) == len(test_documents)
    mock_vector_db.find.assert_called_once()

def test_mongo_batch_operations(mock_vector_db, test_documents):
    adapter = MongoVectorAdapter(client=mock_vector_db)
    # Test batch insert
    adapter.batch_insert(test_documents)
    mock_vector_db.insert_many.assert_called_once()
    
    # Test batch update
    updates = [{"id": "1", "content": "updated"}]
    adapter.batch_update(updates)
    mock_vector_db.update_many.assert_called_once()

def test_mongo_error_handling(mock_vector_db):
    adapter = MongoVectorAdapter(client=mock_vector_db)
    mock_vector_db.insert_many.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        adapter.from_obj([{"id": "1", "content": "test"}])
