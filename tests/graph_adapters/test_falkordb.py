import pytest
from unittest.mock import Mock, patch
from lionagi.service.adapters.graph_adapters.falkordb_graph_adapter import FalkorDBGraphAdapter

@pytest.fixture
def mock_graph_db():
    return Mock()

@pytest.fixture
def test_nodes():
    return [
        {"id": "1", "labels": ["Person"], "properties": {"name": "John"}},
        {"id": "2", "labels": ["Person"], "properties": {"name": "Jane"}}
    ]

@pytest.fixture
def test_relationships():
    return [
        {"start": "1", "end": "2", "type": "KNOWS", "properties": {"since": 2020}}
    ]

def test_falkordb_create_nodes(mock_graph_db, test_nodes):
    adapter = FalkorDBGraphAdapter(client=mock_graph_db)
    adapter.create_nodes(test_nodes)
    mock_graph_db.execute_command.assert_called()

def test_falkordb_create_relationships(mock_graph_db, test_relationships):
    adapter = FalkorDBGraphAdapter(client=mock_graph_db)
    adapter.create_relationships(test_relationships)
    mock_graph_db.execute_command.assert_called()

def test_falkordb_query(mock_graph_db):
    adapter = FalkorDBGraphAdapter(client=mock_graph_db)
    mock_graph_db.execute_command.return_value = [{"n": {"name": "John"}}]
    
    result = adapter.query("MATCH (n:Person) RETURN n")
    assert len(result) > 0
    mock_graph_db.execute_command.assert_called_once()

def test_falkordb_error_handling(mock_graph_db):
    adapter = FalkorDBGraphAdapter(client=mock_graph_db)
    mock_graph_db.execute_command.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        adapter.query("INVALID QUERY")
