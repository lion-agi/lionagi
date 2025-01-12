import pytest
from typing import Generator

from tests.mocks.vector_db import MockVectorDB
from tests.mocks.graph_db import MockGraphDB
from tests.fixtures.data import generate_test_documents

@pytest.fixture
def mock_vector_db() -> Generator[MockVectorDB, None, None]:
    """Provides a mock vector database for testing."""
    db = MockVectorDB()
    yield db
    db.clear()  # Cleanup after tests

@pytest.fixture
def mock_graph_db() -> Generator[MockGraphDB, None, None]:
    """Provides a mock graph database for testing."""
    db = MockGraphDB()
    yield db
    db.clear()  # Cleanup after tests

@pytest.fixture
def test_documents():
    """Provides sample documents for testing."""
    return generate_test_documents()
