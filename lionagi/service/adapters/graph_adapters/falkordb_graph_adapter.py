"""FalkorDB Graph Adapter implementation.

Provides a comprehensive interface for interacting with FalkorDB graphs, including:
- Node and relationship CRUD operations
- Property management
- Graph traversal and queries
- Transaction handling
- Error recovery
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

from lionagi._errors import OperationError

from ..base import Adapter

T = TypeVar("T")

try:
    import falkordb  # type: ignore
    from falkordb.exceptions import (  # type: ignore
        ConnectionError,
        FalkorDBError,
        QueryError,
        TransactionError,
    )

    HAS_FALKOR = True
except ImportError:
    HAS_FALKOR = False


class FalkorGraphAdapter(Adapter[T]):
    """Adapter for reading/writing graph data to/from FalkorDB.

    Provides comprehensive graph database operations including:
    - Connection management with context managers
    - Transaction support
    - Node and relationship CRUD operations
    - Query execution
    - Error handling and recovery

    Attributes:
        _conn: Optional[falkordb.FalkorDB] - Active database connection
        _graph: Optional[str] - Current graph name
    """

    def __init__(self):
        self._conn: falkordb.FalkorDB | None = None
        self._graph: str | None = None

    @contextmanager
    def connect(
        self, conn_info: dict[str, Any]
    ) -> Iterator[falkordb.FalkorDB]:
        """Creates and manages a FalkorDB connection.

        Args:
            conn_info: Connection parameters including host, port, etc.

        Yields:
            Active FalkorDB connection

        Raises:
            ConnectionError: If connection fails
        """
        if not HAS_FALKOR:
            raise ImportError("falkordb package is required")

        try:
            self._conn = falkordb.FalkorDB(
                host=conn_info.get("host", "127.0.0.1"),
                port=conn_info.get("port", 6379),
                username=conn_info.get("username"),
                password=conn_info.get("password"),
            )
            self._graph = conn_info["graph_name"]
            yield self._conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {str(e)}") from e
        finally:
            if self._conn:
                self._conn.close()
                self._conn = None
                self._graph = None

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Manages graph transactions.

        Yields:
            None

        Raises:
            TransactionError: If transaction operations fail
        """
        if not self._conn:
            raise ConnectionError("No active connection")

        try:
            self._conn.multi()
            yield
            self._conn.exec()
        except Exception as e:
            self._conn.discard()
            raise TransactionError(f"Transaction failed: {str(e)}") from e

    def execute_query(
        self, query: str, params: dict | None = None
    ) -> list[dict]:
        """Executes a Cypher query against the graph.

        Args:
            query: Cypher query string
            params: Optional query parameters

        Returns:
            List of result records as dicts

        Raises:
            QueryError: If query execution fails
        """
        if not self._conn or not self._graph:
            raise ConnectionError("No active connection")

        try:
            graph = self._conn.select_graph(self._graph)
            result = graph.query(query, params or {})
            return [record.properties for record in result]
        except Exception as e:
            raise QueryError(f"Query failed: {str(e)}") from e

    def create_node(
        self, labels: str | list[str], properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Creates a new node with given labels and properties.

        Args:
            labels: Node label(s)
            properties: Node properties

        Returns:
            Created node data

        Raises:
            OperationError: If node creation fails
        """
        if not self._conn or not self._graph:
            raise ConnectionError("No active connection")

        try:
            graph = self._conn.select_graph(self._graph)
            labels = [labels] if isinstance(labels, str) else labels
            node = graph.create_node(labels=labels, properties=properties)
            return {
                "id": node.id,
                "labels": node.labels,
                "properties": node.properties,
            }
        except Exception as e:
            raise OperationError(f"Failed to create node: {str(e)}") from e

    def create_relationship(
        self,
        start_node_id: int,
        end_node_id: int,
        rel_type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Creates a relationship between nodes.

        Args:
            start_node_id: Source node ID
            end_node_id: Target node ID
            rel_type: Relationship type
            properties: Optional relationship properties

        Returns:
            Created relationship data

        Raises:
            OperationError: If relationship creation fails
        """
        if not self._conn or not self._graph:
            raise ConnectionError("No active connection")

        try:
            graph = self._conn.select_graph(self._graph)
            rel = graph.create_relationship(
                start_node_id, end_node_id, rel_type, properties or {}
            )
            return {
                "id": rel.id,
                "type": rel.type,
                "properties": rel.properties,
                "start_node": rel.start_node,
                "end_node": rel.end_node,
            }
        except Exception as e:
            raise OperationError(
                f"Failed to create relationship: {str(e)}"
            ) from e

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """Reads graph data from FalkorDB.

        Args:
            subj_cls: Target class type
            obj: Connection info dict
            **kwargs: Additional options

        Returns:
            List of node/relationship data

        Raises:
            ValueError: If connection info is invalid
            ConnectionError: If database connection fails
        """
        adapter = cls()
        with adapter.connect(obj):
            query = kwargs.get("query", "MATCH (n) RETURN n")
            return adapter.execute_query(query)

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> str:
        """Writes graph data to FalkorDB.

        Args:
            subj: List of node/relationship data to write
            **kwargs: Must include 'connection' dict

        Returns:
            Status message

        Raises:
            ValueError: If connection info is missing
            OperationError: If write operations fail
        """
        if not kwargs.get("connection"):
            raise ValueError("Missing connection info in kwargs")

        adapter = cls()
        inserted = 0
        relationships = 0

        with adapter.connect(kwargs["connection"]):
            with adapter.transaction():
                for record in subj:
                    if record.get("type") == "node":
                        adapter.create_node(
                            record.get("labels", []),
                            record.get("properties", {}),
                        )
                        inserted += 1
                    elif record.get("type") == "relationship":
                        adapter.create_relationship(
                            record["start_node"],
                            record["end_node"],
                            record["rel_type"],
                            record.get("properties"),
                        )
                        relationships += 1

        return (
            f"Inserted {inserted} node(s) and {relationships} "
            f"relationship(s) in graph '{kwargs['connection']['graph_name']}'"
        )
