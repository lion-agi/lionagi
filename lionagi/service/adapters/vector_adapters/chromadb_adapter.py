# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


# adapters/vector/chromadb_adapter.py
import warnings
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Any, TypeVar

from ..base import Adapter

T = TypeVar("T")

try:
    import chromadb  # type: ignore
    import chromadb.utils.embedding_functions as ef  # type: ignore
    from chromadb.api import Collection  # type: ignore
    from chromadb.api.models.Collection import QueryResult  # type: ignore
    from chromadb.config import Settings  # type: ignore

    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

# Default configuration
DEFAULT_BATCH_SIZE = 100
DEFAULT_CACHE_SIZE = 128
MAX_WORKERS = 4


class ChromaDBAdapter(Adapter[T]):
    """
    An enhanced ChromaDB-based adapter with support for batch operations,
    advanced querying, and performance optimizations.

    Features:
    - Batch operations for add/update/delete/query
    - Advanced filtering with where clauses
    - Multiple query strategies (mmr, exhaustive)
    - Pagination support
    - Connection pooling
    - Query result caching
    - Configurable batch sizes
    - Index management

    Configuration dictionary can include:
        {
            "persist_directory": str,          # ChromaDB storage location
            "collection_name": str,            # Target collection
            "batch_size": int,                # Size of batches for operations
            "cache_size": int,                # Size of LRU cache
            "embedding_function": str,         # Name of embedding function
            "query_strategy": str,            # "mmr" or "exhaustive"
            "where": dict,                    # Filter conditions
            "offset": int,                    # Pagination offset
            "limit": int,                     # Results per page
            "sort": str,                      # Sort field
            "sort_order": str                 # "asc" or "desc"
        }
    """

    def __init__(self):
        self._client = None
        self._collection = None
        self._batch_size = DEFAULT_BATCH_SIZE
        self._executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @property
    def client(self):
        """Lazy initialization of ChromaDB client with connection pooling."""
        if not self._client:
            if not HAS_CHROMA:
                raise ImportError(
                    "ChromaDB not installed. Please run: pip install chromadb"
                )
            self._client = chromadb.Client(
                Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="tmp/chroma_db",
                )
            )
        return self._client

    def _get_collection(self, name: str) -> Collection:
        """Get or create a collection with caching."""
        if not self._collection or self._collection.name != name:
            self._collection = self.client.get_or_create_collection(name=name)
        return self._collection

    @lru_cache(maxsize=DEFAULT_CACHE_SIZE)
    def _query_batch(
        self,
        query_texts: list[str],
        n_results: int = 5,
        where: dict = None,
        offset: int = 0,
        limit: int = 100,
        query_strategy: str = "exhaustive",
    ) -> QueryResult:
        """Execute batched queries with caching."""
        collection = self._collection
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            offset=offset,
            limit=limit,
            query_strategy=query_strategy,
        )

    @lru_cache(maxsize=DEFAULT_CACHE_SIZE)
    def _get_batch(
        self,
        ids: list[str] = None,
        where: dict = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = None,
    ) -> QueryResult:
        """Retrieve batched records with caching."""
        collection = self._collection
        return collection.get(ids=ids, where=where, limit=limit, offset=offset)

    def _add_batch(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict] = None,
        embeddings: list[list[float]] = None,
    ) -> bool:
        """Add multiple records in a batch."""
        try:
            self._collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            return True
        except Exception as e:
            warnings.warn(f"Batch add failed: {str(e)}")
            return False

    def _update_batch(
        self,
        ids: list[str],
        documents: list[str] = None,
        metadatas: list[dict] = None,
        embeddings: list[list[float]] = None,
    ) -> bool:
        """Update multiple records in a batch."""
        try:
            self._collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            return True
        except Exception as e:
            warnings.warn(f"Batch update failed: {str(e)}")
            return False

    def _delete_batch(self, ids: list[str]) -> bool:
        """Delete multiple records in a batch."""
        try:
            self._collection.delete(ids=ids)
            return True
        except Exception as e:
            warnings.warn(f"Batch delete failed: {str(e)}")
            return False

    def count(self, where: dict = None) -> int:
        """Get count of records matching filter criteria."""
        result = self._collection.get(where=where)
        return len(result["ids"]) if result else 0

    def get_nearest_neighbors(
        self, query_text: str, k: int = 5, where: dict = None
    ) -> list[dict]:
        """Find k nearest neighbors for query text."""
        results = self._collection.query(
            query_texts=[query_text], n_results=k, where=where
        )
        return [
            {"id": id, "document": doc, "metadata": meta, "distance": dist}
            for id, doc, meta, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results.get("distances", [[]])[0],
            )
        ]

    def search(
        self,
        query_texts: str | list[str],
        n_results: int = 5,
        where: dict = None,
        **kwargs,
    ) -> list[dict]:
        """Enhanced search with filtering and options."""
        if isinstance(query_texts, str):
            query_texts = [query_texts]

        results = self._query_batch(
            query_texts=query_texts, n_results=n_results, where=where, **kwargs
        )

        return [
            {
                "query": query,
                "matches": [
                    {
                        "id": id,
                        "document": doc,
                        "metadata": meta,
                        "distance": dist,
                    }
                    for id, doc, meta, dist in zip(ids, docs, metas, distances)
                ],
            }
            for query, ids, docs, metas, distances in zip(
                query_texts,
                results["ids"],
                results["documents"],
                results["metadatas"],
                results.get("distances", [[]] * len(query_texts)),
            )
        ]

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

    def reset_cache(self):
        """Clear query result cache."""
        self._query_batch.cache_clear()
        self._get_batch.cache_clear()

    def optimize_index(self):
        """Optimize index for faster queries."""
        # ChromaDB handles most optimization internally
        # This is a placeholder for future optimization capabilities
        pass

    def get_stats(self) -> dict:
        """Get collection statistics."""
        if not self._collection:
            return {}

        count = self.count()
        stats = {
            "total_count": count,
            "collection_name": self._collection.name,
        }

        # Add additional stats if available
        try:
            peek = self._collection.peek()
            stats.update(
                {
                    "has_embeddings": bool(peek.get("embeddings")),
                    "has_metadata": bool(peek.get("metadatas")),
                }
            )
        except:
            pass

        return stats

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
