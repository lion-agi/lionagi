import pytest
from unittest.mock import Mock, patch
from lionagi.service.adapters.graph_adapters.neo4j_graph_adapter import Neo4jGraphAdapter

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

def test_neo4j_create_nodes(mock_graph_db, test_nodes):
    adapter = Neo4jGraphAdapter(client=mock_graph_db)
    adapter.create_nodes(test_nodes)
    mock_graph_db.run.assert_called()

def test_neo4j_create_relationships(mock_graph_db, test_relationships):
    adapter = Neo4jGraphAdapter(client=mock_graph_db)
    adapter.create_relationships(test_relationships)
    mock_graph_db.run.assert_called()

def test_neo4j_query(mock_graph_db):
    adapter = Neo4jGraphAdapter(client=mock_graph_db)
    mock_graph_db.run.return_value = [{"n": {"name": "John"}}]
    
    result = adapter.query("MATCH (n:Person) RETURN n")
    assert len(result) > 0
    mock_graph_db.run.assert_called_once()

def test_neo4j_error_handling(mock_graph_db):
    adapter = Neo4jGraphAdapter(client=mock_graph_db)
    mock_graph_db.run.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        adapter.query("INVALID QUERY")
