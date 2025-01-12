from collections.abc import Generator

import pytest

from tests.fixtures.data import generate_test_documents
from tests.mocks.graph_db import MockGraphDB
from tests.mocks.vector_db import MockVectorDB


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
