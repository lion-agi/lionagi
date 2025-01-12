# adapters/vector/chromadb_adapter.py
from typing import Any, Dict, List, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    import chromadb  # type: ignore
    import chromadb.utils.embedding_functions as ef  # type: ignore
    from chromadb.api import Collection  # type: ignore
    from chromadb.config import Settings  # type: ignore

    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False


class ChromaDBAdapter(Adapter[T]):
    """
    A minimal ChromaDB-based adapter. from_obj can do a query or retrieve,
    to_obj can add documents to a collection.

    'obj' or 'connection' dictionary can have:
        {
          "persist_directory": "...",
          "collection_name": "...",
          "texts": [...],  # for reading? or searching?
          "query_texts": [...]
        }
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        if not HAS_CHROMA:
            raise ImportError(
                "chromadb not installed. Please `pip install chromadb`."
            )

        if not isinstance(obj, dict):
            raise ValueError(
                "ChromaDBAdapter requires 'obj' to be a dict with connection config."
            )
        coll_name = obj.get("collection_name")
        if not coll_name:
            raise ValueError(
                "No 'collection_name' provided for ChromaDBAdapter.from_obj."
            )

        # Initialize Chroma client
        chroma_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=obj.get("persist_directory", "tmp/chroma_db"),
        )
        client = chromadb.Client(chroma_settings)
        # get or create collection
        collection = client.get_or_create_collection(name=coll_name)

        # If user provides "query_texts", let's do a similarity query
        query_texts = obj.get("query_texts")
        if query_texts:
            n_results = obj.get("n_results", 5)
            results = collection.query(
                query_texts=query_texts, n_results=n_results
            )
            # results is a dict with e.g. keys: "ids", "documents", "embeddings", "metadatas"
            # We can unify them into list[dict]
            combined = []
            # results["ids"] is a list of lists (per query)
            for i in range(len(results["ids"])):
                row = {
                    "ids": results["ids"][i],
                    "documents": results["documents"][i],
                    "metadatas": results["metadatas"][i],
                    "embeddings": results.get("embeddings", [[]])[i],
                }
                combined.append(row)
            return combined
        else:
            # Possibly return entire collection or a limited set
            # This is not a default Chroma method, so we do e.g. random usage:
            # Actually, we can do collection.get(ids=...) or .get(where=...) etc.
            all_docs = collection.get()
            data = []
            for i in range(len(all_docs["ids"])):
                data.append(
                    {
                        "id": all_docs["ids"][i],
                        "doc": all_docs["documents"][i],
                        "meta": all_docs["metadatas"][i],
                        "embedding": (
                            (all_docs.get("embeddings") or [])[i]
                            if all_docs.get("embeddings")
                            else None
                        ),
                    }
                )
            return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Insert or update records in Chroma. Expects 'connection' dict with 'collection_name'.
        Each element of 'subj' should have 'id' and 'content'. Optionally 'metadata', 'embedding'.
        """
        if not HAS_CHROMA:
            raise ImportError(
                "chromadb not installed. Please `pip install chromadb`."
            )

        conn = kwargs.get("connection")
        if not conn or not isinstance(conn, dict):
            raise ValueError(
                "ChromaDBAdapter.to_obj requires 'connection' dict with 'collection_name' etc."
            )
        coll_name = conn.get("collection_name")
        if not coll_name:
            raise ValueError(
                "No 'collection_name' in 'connection' for ChromaDBAdapter.to_obj."
            )

        # create or get collection
        chroma_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=conn.get("persist_directory", "tmp/chroma_db"),
        )
        client = chromadb.Client(chroma_settings)
        collection = client.get_or_create_collection(name=coll_name)

        # We assume each record in subj has { 'id': str, 'content': str, 'metadata': dict, 'embedding': [...] }
        # If 'embedding' is missing, Chroma can auto-embed if a function is set, or we skip.
        ids = []
        contents = []
        metadatas = []
        embeddings = []
        for rec in subj:
            ids.append(str(rec["id"]))
            contents.append(rec.get("content", ""))
            metadatas.append(rec.get("metadata", {}))
            embeddings.append(rec.get("embedding", None))

        # Chroma can handle add or update with "upsert" style if the ID already exists
        collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=(
                embeddings if any(e is not None for e in embeddings) else None
            ),
        )
        return (
            f"Added or updated {len(subj)} records in collection '{coll_name}'"
        )
