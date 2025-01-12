# adapters/vector/mongo_vector_adapter.py
from typing import Any, Dict, List, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    import pymongo  # type: ignore
    from pymongo import MongoClient  # type: ignore

    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False


class MongoVectorAdapter(Adapter[T]):
    """
    A minimal vector adapter for MongoDB.
    from_obj can query or retrieve documents by ID,
    to_obj can insert or upsert documents with embeddings into a 'collection'.

    'obj' or 'connection' dict should contain:
      {
        "connection_string": "...",
        "db_name": "...",
        "collection_name": "...",
        -- optional "query" or "filter" or "search" to specify how we retrieve
      }
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        """
        Retrieve or search vector data from Mongo. If 'obj' has 'filter' or 'query',
        we do a normal find; if we want advanced Atlas Vector search, we need the
        appropriate pipeline or call. This example is minimal.
        """
        if not HAS_PYMONGO:
            raise ImportError(
                "pymongo not installed. Please `pip install pymongo`."
            )

        if not isinstance(obj, dict):
            raise ValueError(
                "MongoVectorAdapter.from_obj expects a dict with connection details."
            )
        conn_str = obj.get("connection_string")
        db_name = obj.get("db_name")
        coll_name = obj.get("collection_name")
        if not (conn_str and db_name and coll_name):
            raise ValueError(
                "Missing 'connection_string', 'db_name', or 'collection_name' in 'obj' dict."
            )

        client = MongoClient(conn_str)
        db = client[db_name]
        coll = db[coll_name]

        # We'll do a basic find if there's a "filter" or return all if not
        search_filter = obj.get("filter") or {}
        cursor = coll.find(search_filter)
        results = []
        for doc in cursor:
            # convert _id -> id
            doc["id"] = doc.pop("_id", None)
            results.append(doc)
        return results

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Insert or update vector data. Expects 'connection' in kwargs:
           {
             "connection_string": "...",
             "db_name": "...",
             "collection_name": "...",
             "upsert": True/False
           }
        Each record in subj might have a 'vector' key, 'id', 'content', 'metadata', etc.
        We'll do a naive upsert with _id= record["id"].
        """
        if not HAS_PYMONGO:
            raise ImportError(
                "pymongo not installed. Please `pip install pymongo`."
            )

        conn = kwargs.get("connection")
        if not (conn and isinstance(conn, dict)):
            raise ValueError(
                "MongoVectorAdapter.to_obj requires 'connection' dict with 'connection_string', etc."
            )
        conn_str = conn.get("connection_string")
        db_name = conn.get("db_name")
        coll_name = conn.get("collection_name")
        if not (conn_str and db_name and coll_name):
            raise ValueError(
                "Missing 'connection_string', 'db_name', or 'collection_name' in 'connection' dict."
            )

        client = MongoClient(conn_str)
        db = client[db_name]
        coll = db[coll_name]
        upsert_flag = conn.get("upsert", True)

        # Prepare bulk operations
        ops = []
        for record in subj:
            if "id" not in record:
                raise ValueError(
                    "Each record must have an 'id' field to store in Mongo."
                )
            doc_id = record.pop("id")
            # set _id = doc_id, if it's not ObjectId
            record["_id"] = doc_id
            ops.append(
                pymongo.UpdateOne(
                    {"_id": doc_id}, {"$set": record}, upsert=upsert_flag
                )
            )
        if ops:
            res = coll.bulk_write(ops)
            return f"Upserted {res.upserted_count}, modified {res.modified_count} documents."
        return "No documents to write."
