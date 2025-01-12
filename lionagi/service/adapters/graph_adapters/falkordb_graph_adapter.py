# adapters/graph_adapters/falkor_graph_adapter.py

from typing import Any, Dict, List, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    import falkordb  # type: ignore
    from graphrag_sdk import KnowledgeGraph  # type: ignore

    HAS_FALKOR = True
except ImportError:
    HAS_FALKOR = False


class FalkorGraphAdapter(Adapter[T]):
    """
    A minimal example of reading/writing node data to FalkorDB.
    from_obj():
      - 'obj' is a dict with e.g. {"graph_name": "...", "host": "...", "port": ...}
      - returns a list of nodes as dicts
    to_obj():
      - inserts or updates node data
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        if not HAS_FALKOR:
            raise ImportError("falkordb or graphrag_sdk not installed.")

        if not isinstance(obj, dict):
            raise ValueError(
                "FalkorGraphAdapter.from_obj requires a dict with FalkorDB connection info."
            )
        graph_name = obj.get("graph_name")
        host = obj.get("host", "127.0.0.1")
        port = obj.get("port", 6379)
        if not graph_name:
            raise ValueError("Missing 'graph_name' for FalkorDB graph.")

        db = falkordb.FalkorDB(
            host=host,
            port=port,
            username=obj.get("username"),
            password=obj.get("password"),
        )

        if graph_name not in db.list_graphs():
            raise ValueError(
                f"Graph '{graph_name}' does not exist in FalkorDB."
            )

        graph = db.select_graph(graph_name)

        # We'll do a naive approach: fetch all nodes
        all_nodes = graph.all_nodes()
        data = []
        for node in all_nodes:
            data.append(
                {
                    "type": "node",
                    "id": node.id,
                    "labels": node.labels,
                    "properties": node.properties,
                }
            )
        return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Insert or update records. Expects 'connection' in kwargs:
            {
              "graph_name": "...",
              "host": "...",
              "port": ...,
              etc.
            }
        Each dict in subj might look like:
          {
            "type": "node",
            "labels": ["SomeLabel"],
            "properties": {"key": "value", ...}
          }
        """
        if not HAS_FALKOR:
            raise ImportError("falkordb or graphrag_sdk not installed.")

        conn = kwargs.get("connection")
        if not conn or not isinstance(conn, dict):
            raise ValueError(
                "FalkorGraphAdapter.to_obj requires 'connection' dict with 'graph_name','host','port' etc."
            )

        graph_name = conn.get("graph_name")
        host = conn.get("host", "127.0.0.1")
        port = conn.get("port", 6379)

        db = falkordb.FalkorDB(
            host=host,
            port=port,
            username=conn.get("username"),
            password=conn.get("password"),
        )

        if graph_name not in db.list_graphs():
            raise ValueError(
                f"Graph '{graph_name}' does not exist in FalkorDB."
            )

        g = db.select_graph(graph_name)
        inserted = 0

        for record in subj:
            if record.get("type") == "node":
                labels = record.get("labels", [])
                props = record.get("properties", {})
                # create_node might take a 'labels=' param, plus a dict of props
                node = g.create_node(labels=labels, properties=props)
                inserted += 1
            elif record.get("type") == "relationship":
                # Implementation left as an example
                pass

        return f"Inserted/updated {inserted} node(s) in Falkor graph '{graph_name}'."
