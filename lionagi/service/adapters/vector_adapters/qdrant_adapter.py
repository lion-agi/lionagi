# adapters/vector/qdrant_adapter.py
from typing import Any, Dict, List, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    import qdrant_client  # type: ignore
    from qdrant_client import QdrantClient  # type: ignore
    from qdrant_client.http import models as qdrant_models  # type: ignore

    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False


class QdrantAdapter(Adapter[T]):
    """
    A minimal adapter to read/write data to a Qdrant vector database.

    Expects 'obj' or 'connection' in kwargs to be a dict with:
        {
          "host": "...",
          "port": 6333,
          "api_key": "...",
          "collection_name": "...",
          "vectors_config": { ... } # optional Qdrant config
        }
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        from_obj is typically used to perform a vector search or retrieve from Qdrant.

        'obj' is expected to be a dict containing Qdrant connection info and
        at least a "collection_name". If we want to do a vector search, we can
        pass a "search" key with the query vectors or text. This example is minimal.
        """
        if not HAS_QDRANT:
            raise ImportError(
                "qdrant-client is not installed. Please `pip install qdrant-client`."
            )

        if not isinstance(obj, dict):
            raise ValueError(
                "QdrantAdapter requires 'obj' to be a dict with connection config."
            )

        collection_name = obj.get("collection_name")
        if not collection_name:
            raise ValueError(
                "No 'collection_name' provided in 'obj' for QdrantAdapter.from_obj()."
            )

        # Create or reuse a QdrantClient
        client = QdrantClient(
            host=obj.get("host", "localhost"),
            port=obj.get("port", 6333),
            api_key=obj.get("api_key"),
        )

        # Let's assume user provided a 'search' dict, or we do a 'scroll' retrieval
        search_conf = obj.get("search", {})
        if "vector" in search_conf:
            # We do a search with a single vector
            query_vector = search_conf["vector"]
            top_k = search_conf.get("limit", 5)
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
                with_vectors=search_conf.get("with_vectors", False),
            )
            # Convert results to list[dict]
            # Each 'result' is a ScoredPoint
            # We'll store them as { "id": ..., "score": ..., "payload": ..., "vector": ... }
            data = []
            for r in results:
                row = {
                    "id": r.id,
                    "score": r.score,
                    "payload": r.payload,
                }
                if r.vector:
                    row["vector"] = r.vector
                data.append(row)
            return data
        else:
            # Return entire collection or do a 'scroll'
            points, _next_page = client.scroll(
                collection_name=collection_name, limit=100
            )  # example
            data = []
            for p in points:
                row = {
                    "id": p.id,
                    "payload": p.payload,
                }
                if p.vector:
                    row["vector"] = p.vector
                data.append(row)
            return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Writes data to Qdrant. Expects 'connection' in kwargs as a dict, containing
        Qdrant client info and 'collection_name'.

        The subj is a list of dict: each must have at least "id" and "vector" fields.
        e.g. [
          {"id": 123, "vector": [...], "payload": {"text": "hello"}},
          ...
        ]
        """
        if not HAS_QDRANT:
            raise ImportError(
                "qdrant-client is not installed. Please `pip install qdrant-client`."
            )

        conn = kwargs.get("connection")
        if not conn or not isinstance(conn, dict):
            raise ValueError(
                "QdrantAdapter.to_obj requires 'connection' dict with Qdrant info."
            )

        collection_name = conn.get("collection_name")
        if not collection_name:
            raise ValueError(
                "No 'collection_name' found in 'connection' for QdrantAdapter.to_obj."
            )

        client = QdrantClient(
            host=conn.get("host", "localhost"),
            port=conn.get("port", 6333),
            api_key=conn.get("api_key"),
        )

        # Convert our list[dict] into Qdrant PointStruct
        points = []
        for record in subj:
            if "id" not in record or "vector" not in record:
                raise ValueError(
                    "Each record must have 'id' and 'vector' keys to upsert in Qdrant."
                )
            p = qdrant_models.PointStruct(
                id=record["id"],
                vector=record["vector"],
                payload=record.get("payload", {}),
            )
            points.append(p)

        # Upsert into Qdrant
        result = client.upsert(collection_name=collection_name, points=points)
        return f"Upserted {len(points)} points into {collection_name}, {result.status}"
