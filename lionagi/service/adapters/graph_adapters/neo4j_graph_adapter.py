# adapters/graph_adapters/neo4j_graph_adapter.py

from typing import Any, Dict, List, TypeVar, Optional, Callable, Iterator, ContextManager
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass

from ..base import Adapter
from neo4j import (  # type: ignore
    GraphDatabase, 
    Transaction, 
    Session,
    Result,
    Driver,
    unit_of_work
)
from neo4j.exceptions import ServiceUnavailable, SessionExpired  # type: ignore

T = TypeVar("T")

try:
    from neo4j import GraphDatabase
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False

@dataclass
class BatchStats:
    """Statistics for batch operations"""
    nodes_created: int = 0
    relationships_created: int = 0
    properties_set: int = 0
    labels_added: int = 0
    nodes_deleted: int = 0
    relationships_deleted: int = 0

class TransactionError(Exception):
    """Custom exception for transaction-related errors"""
    pass


class Neo4jGraphAdapter(Adapter[T]):
    """
    Enhanced adapter for reading and writing node/relationship data to a Neo4j database.
    
    Features:
    - Transaction management with savepoint support
    - Batch operations for nodes and relationships
    - Complex query support with pattern matching
    - Parameterized queries and aggregations
    
    Example:
        ```python
        adapter = Neo4jGraphAdapter()
        
        # Using transaction context manager
        with adapter.transaction() as tx:
            results = tx.run("MATCH (n) RETURN n LIMIT 5")
            
        # Batch node creation
        nodes = [
            {"labels": ["Person"], "properties": {"name": "Alice"}},
            {"labels": ["Person"], "properties": {"name": "Bob"}}
        ]
        stats = adapter.create_nodes_batch(nodes)
        ```
    """
    
    def __init__(self):
        self._driver: Optional[Driver] = None
        self._active_tx: Optional[Transaction] = None
        self._savepoints: List[str] = []
        
    def connect(self, uri: str, user: str, password: str) -> None:
        """Establish connection to Neo4j database"""
        if not HAS_NEO4J:
            raise ImportError("Neo4j driver not installed")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self) -> None:
        """Close the database connection"""
        if self._driver:
            self._driver.close()
            self._driver = None
            
    @contextmanager
    def transaction(self, timeout: Optional[float] = None) -> Iterator[Transaction]:
        """
        Transaction context manager with timeout support
        
        Args:
            timeout: Optional timeout in seconds
            
        Yields:
            Active transaction object
            
        Example:
            ```python
            with adapter.transaction() as tx:
                tx.run("CREATE (n:Person {name: 'Alice'})")
            ```
        """
        if not self._driver:
            raise TransactionError("Not connected to database")
            
        session = self._driver.session()
        try:
            tx = session.begin_transaction(timeout=timeout)
            self._active_tx = tx
            yield tx
            tx.commit()
        except Exception as e:
            if tx:
                tx.rollback()
            raise TransactionError(f"Transaction failed: {str(e)}") from e
        finally:
            self._active_tx = None
            session.close()
            
    def transaction_decorator(self, func: Callable) -> Callable:
        """Decorator to wrap functions in a transaction"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.transaction() as tx:
                return func(tx, *args, **kwargs)
        return wrapper

    def create_nodes_batch(
        self, 
        nodes: List[Dict[str, Any]], 
        batch_size: int = 1000
    ) -> BatchStats:
        """
        Bulk create nodes in batches
        
        Args:
            nodes: List of node definitions with labels and properties
            batch_size: Number of nodes to create in each batch
            
        Returns:
            BatchStats with creation metrics
        """
        stats = BatchStats()
        
        with self.transaction() as tx:
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i + batch_size]
                params = {"batch": batch}
                query = """
                UNWIND $batch as node
                CREATE (n)
                SET n = node.properties
                WITH n, node.labels as labels
                CALL apoc.create.addLabels(n, labels) YIELD node as _
                RETURN count(n)
                """
                result = tx.run(query, params)
                stats.nodes_created += result.single()[0]
                
        return stats
        
    def create_relationships_batch(
        self,
        relationships: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> BatchStats:
        """
        Bulk create relationships in batches
        
        Args:
            relationships: List of relationship definitions
            batch_size: Number of relationships to create in each batch
            
        Returns:
            BatchStats with creation metrics
        """
        stats = BatchStats()
        
        with self.transaction() as tx:
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i + batch_size]
                params = {"batch": batch}
                query = """
                UNWIND $batch as rel
                MATCH (start) WHERE id(start) = rel.start
                MATCH (end) WHERE id(end) = rel.end
                CREATE (start)-[r:${rel.type_name}]->(end)
                SET r = rel.properties
                RETURN count(r)
                """
                result = tx.run(query, params)
                stats.relationships_created += result.single()[0]
                
        return stats
        
    def update_properties_batch(
        self,
        updates: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> BatchStats:
        """
        Bulk update node/relationship properties
        
        Args:
            updates: List of property updates
            batch_size: Updates per batch
            
        Returns:
            BatchStats with update metrics
        """
        stats = BatchStats()
        
        with self.transaction() as tx:
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                params = {"batch": batch}
                query = """
                UNWIND $batch as item
                MATCH (n) WHERE id(n) = item.id
                SET n += item.properties
                RETURN count(n)
                """
                result = tx.run(query, params)
                stats.properties_set += result.single()[0]
                
        return stats
        
    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        Retrieve data from Neo4j as a list of dicts. 'obj' is a dict:
            {
              "uri": "bolt://localhost:7687",
              "user": "neo4j",
              "password": "...",
              "cypher": "MATCH (n) RETURN n LIMIT 5"
            }

        If 'cypher' is omitted, we'll default to retrieving (n) for all nodes.
        The returned list-of-dicts will look like:
            [
              {
                "type": "node",
                "id": <node_id>,
                "labels": [...],
                "properties": {...}
              },
              ...
            ]
        or if the cypher returns relationships, we also store them as:
            {
              "type": "relationship",
              "id": <rel_id>,
              "start": <start_node_id>,
              "end": <end_node_id>,
              "type_name": <relationship_type>,
              "properties": {...}
            }
        """
        if not HAS_NEO4J:
            raise ImportError("Neo4j driver not installed.")

        uri = obj.get("uri")
        user = obj.get("user")
        password = obj.get("password")
        if not uri or not user or not password:
            raise ValueError(
                "Missing 'uri', 'user', or 'password' for Neo4j connection."
            )

        driver = GraphDatabase.driver(uri, auth=(user, password))

        cypher = obj.get("cypher", "MATCH (n) RETURN n")

        data = []
        with driver.session() as session:
            results = session.run(cypher)
            for record in results:
                for key, val in record.items():
                    # If it's a node
                    if hasattr(val, "labels") and hasattr(val, "id"):
                        data.append(
                            {
                                "type": "node",
                                "id": val.id,
                                "labels": list(val.labels),
                                "properties": dict(val),
                            }
                        )
                    # If it's a relationship
                    elif hasattr(val, "start_node_id") and hasattr(
                        val, "end_node_id"
                    ):
                        data.append(
                            {
                                "type": "relationship",
                                "id": val.id,
                                "start": val.start_node_id,
                                "end": val.end_node_id,
                                "type_name": val.type,
                                "properties": dict(val),
                            }
                        )
                    # Otherwise, store it in a generic manner
                    else:
                        data.append({key: str(val)})

        driver.close()
        return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Write data to Neo4j. Expects 'connection' in kwargs:
            {
              "uri": "...",
              "user": "...",
              "password": "...",
              "merge": True/False
            }

        Each dict in 'subj' can be:
          {
            "type": "node",
            "labels": [...],
            "properties": {...}
          }
          or
          {
            "type": "relationship",
            "start": <node_id>,
            "end": <node_id>,
            "type_name": <REL_TYPE>,
            "properties": {...}
          }

        We'll do a naive approach with CREATE or MERGE.
        """
        conn = kwargs.get("connection")
        if not conn or not isinstance(conn, dict):
            raise ValueError(
                "Neo4jGraphAdapter.to_obj requires 'connection' dict with 'uri','user','password'."
            )

        uri = conn.get("uri")
        user = conn.get("user")
        password = conn.get("password")
        merge_mode = conn.get("merge", True)  # default to MERGE vs. CREATE

        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            for record in subj:
                rec_type = record.get("type")
                if rec_type == "node":
                    labels = record.get("labels", [])
                    props = record.get("properties", {})
                    if merge_mode:
                        # Potentially do a MERGE approach using a unique property, but we do CREATE for simplicity
                        label_str = ":" + ":".join(labels) if labels else ""
                        set_clause, param_dict = cls._props_to_set(
                            props, prefix="props"
                        )
                        cypher = f"CREATE (n{label_str} {{}}) SET {set_clause}"
                        session.run(cypher, **param_dict)
                    else:
                        # Just a plain CREATE if not merging
                        label_str = ":" + ":".join(labels) if labels else ""
                        set_clause, param_dict = cls._props_to_set(
                            props, prefix="props"
                        )
                        cypher = f"CREATE (n{label_str} {{}}) SET {set_clause}"
                        session.run(cypher, **param_dict)

                elif rec_type == "relationship":
                    start_id = record.get("start")
                    end_id = record.get("end")
                    rel_type = record.get("type_name", "RELATES_TO")
                    props = record.get("properties", {})
                    set_clause, param_dict = cls._props_to_set(
                        props, prefix="props"
                    )
                    cypher = (
                        f"MATCH (s), (e) WHERE id(s)=$start_id AND id(e)=$end_id "
                        f"CREATE (s)-[r:{rel_type} {{}}]->(e) SET {set_clause}"
                    )
                    param_dict["start_id"] = start_id
                    param_dict["end_id"] = end_id
                    session.run(cypher, **param_dict)
                else:
                    # ignore unknown type
                    pass

        driver.close()
        return f"Processed {len(subj)} records in Neo4j."

    def execute_pattern_match(
        self,
        pattern: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Result:
        """
        Execute a pattern matching query
        
        Args:
            pattern: Cypher pattern to match
            params: Query parameters
            limit: Optional result limit
            
        Returns:
            Query result
            
        Example:
            ```python
            result = adapter.execute_pattern_match(
                "MATCH (p:Person)-[:KNOWS]->(friend) RETURN p, friend",
                limit=10
            )
            ```
        """
        query = f"MATCH {pattern}"
        if limit:
            query += f" LIMIT {limit}"
            
        with self.transaction() as tx:
            return tx.run(query, parameters=params or {})
            
    def execute_aggregation(
        self,
        match_clause: str,
        group_by: str,
        aggregations: List[str],
        params: Optional[Dict[str, Any]] = None
    ) -> Result:
        """
        Execute an aggregation query
        
        Args:
            match_clause: MATCH clause
            group_by: GROUP BY expression
            aggregations: List of aggregation expressions
            params: Query parameters
            
        Returns:
            Query result
            
        Example:
            ```python
            result = adapter.execute_aggregation(
                "MATCH (p:Person)",
                "p.age",
                ["count(p) as count", "avg(p.salary) as avg_salary"]
            )
            ```
        """
        aggs = ", ".join(aggregations)
        query = f"{match_clause} WITH {group_by} as group_key {aggs}"
        
        with self.transaction() as tx:
            return tx.run(query, parameters=params or {})
            
    def execute_traversal(
        self,
        start_pattern: str,
        relationship_pattern: str,
        depth: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Result:
        """
        Execute a graph traversal query
        
        Args:
            start_pattern: Pattern to match start nodes
            relationship_pattern: Pattern for relationships to traverse
            depth: Optional maximum traversal depth
            params: Query parameters
            
        Returns:
            Query result
            
        Example:
            ```python
            result = adapter.execute_traversal(
                "(p:Person {name: 'Alice'})",
                "-[:KNOWS]->(friend)",
                depth=3
            )
            ```
        """
        depth_str = str(depth) if depth else "*"
        query = f"""
        MATCH path = ({start_pattern}){relationship_pattern}{{{depth_str}}}
        RETURN path
        """
        
        with self.transaction() as tx:
            return tx.run(query, parameters=params or {})
            
    @staticmethod
    def _props_to_set(props: dict, prefix="props") -> tuple[str, dict]:
        """
        Helper: produce a string for the SET clause and param dict for Cypher.
        e.g. "n.propA = $props_propA, n.propB = $props_propB"
        """
        if not props:
            return "", {}
        sets = []
        params = {}
        for k, v in props.items():
            param_key = f"{prefix}_{k}"
            sets.append(f"n.{k} = ${param_key}")
            params[param_key] = v
        return ", ".join(sets), params
