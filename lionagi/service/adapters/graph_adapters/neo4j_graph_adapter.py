# adapters/graph_adapters/neo4j_graph_adapter.py

from typing import Any, Dict, List, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    from neo4j import GraphDatabase  # type: ignore

    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False


class Neo4jGraphAdapter(Adapter[T]):
    """
    Minimal adapter for reading and writing node/relationship data to a Neo4j database.
    """

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
