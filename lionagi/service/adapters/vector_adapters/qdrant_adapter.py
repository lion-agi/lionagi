# adapters/vector/qdrant_adapter.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union
from urllib.parse import urlparse

from ....._errors import ItemNotFoundError, OperationError
from ..base import Adapter

T = TypeVar("T")

try:
    import grpc
    import numpy as np
    from qdrant_client import QdrantClient
    from qdrant_client import grpc as qdrant_grpc
    from qdrant_client.conversions import common_types as types
    from qdrant_client.http import models as rest_models
    from qdrant_client.http.exceptions import UnexpectedResponse

    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False

T = TypeVar("T")


@dataclass
class QdrantConfig:
    """Configuration for Qdrant connection and operations."""

    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    api_key: str | None = None
    prefer_grpc: bool = True
    timeout: float = 5.0
    collection_name: str = "default"
    vectors_config: dict[str, Any] | None = None

    @classmethod
    def from_url(cls, url: str) -> "QdrantConfig":
        """Create config from URL string."""
        parsed = urlparse(url)
        return cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6333,
            api_key=parsed.password,
        )


class QdrantAdapter(Adapter[T]):
    """
    Advanced adapter for Qdrant vector database operations.

    Supports both REST and gRPC protocols with comprehensive vector operations:
    - Collection management (create, delete, update)
    - Point operations (upsert, delete, search, scroll)
    - Batch operations with configurable size
    - Advanced search with filtering and scoring

    Args:
        config: QdrantConfig object or dict with connection settings
        batch_size: Size of batches for bulk operations

    Example:
        ```python
        config = QdrantConfig(host="localhost", collection_name="vectors")
        adapter = QdrantAdapter(config)

        # Search vectors
        results = adapter.search(
            query_vector=[0.1, 0.2, ...],
            limit=10,
            filter={"must": [{"key": "category", "match": {"value": "example"}}]}
        )
        ```
    """

    def __init__(
        self,
        config: QdrantConfig | dict[str, Any],
        batch_size: int = 100,
    ):
        if not HAS_QDRANT:
            raise ImportError(
                "Required packages not installed. Please run:\n"
                "pip install qdrant-client grpcio-tools numpy"
            )

        self.config = (
            config
            if isinstance(config, QdrantConfig)
            else QdrantConfig(**config)
        )
        self.batch_size = batch_size
        self._client = None

    @property
    def client(self) -> QdrantClient:
        """Lazy initialization of QdrantClient."""
        if self._client is None:
            self._client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                grpc_port=self.config.grpc_port,
                api_key=self.config.api_key,
                prefer_grpc=self.config.prefer_grpc,
                timeout=self.config.timeout,
            )
        return self._client

    def create_collection(
        self, vectors_config: dict[str, Any] | None = None, **kwargs
    ) -> None:
        """
        Create a new collection with specified configuration.

        Args:
            vectors_config: Vector parameters (dim, distance, etc)
            **kwargs: Additional collection parameters
        """
        try:
            config = vectors_config or self.config.vectors_config
            if not config:
                raise ValueError("vectors_config is required")

            self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config=config,
                **kwargs,
            )
        except Exception as e:
            raise OperationError(f"Failed to create collection: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection."""
        try:
            self.client.delete_collection(self.config.collection_name)
        except Exception as e:
            raise OperationError(f"Failed to delete collection: {str(e)}")

    @classmethod
    def from_obj(
        cls, subj_cls: type[T], obj: Any, /, **kwargs
    ) -> list[dict[str, Any]]:
        """
        Retrieve or search vectors from Qdrant.

        Args:
            obj: Dict with search parameters or collection info
            **kwargs: Additional parameters

        Returns:
            List of retrieved points as dictionaries
        """
        if not isinstance(obj, dict):
            raise ValueError("obj must be a dict with Qdrant parameters")

        adapter = cls(obj)

        search_params = obj.get("search", {})
        if "vector" in search_params:
            return adapter.search(
                query_vector=search_params["vector"],
                limit=search_params.get("limit", 10),
                with_payload=True,
                with_vectors=search_params.get("with_vectors", False),
                filter=search_params.get("filter"),
                score_threshold=search_params.get("score_threshold"),
                **kwargs,
            )
        else:
            return adapter.scroll(
                limit=obj.get("limit", 100),
                with_payload=True,
                with_vectors=True,
                filter=obj.get("filter"),
                **kwargs,
            )

    @classmethod
    def to_obj(cls, subj: list[dict[str, Any]], /, **kwargs) -> str:
        """
        Upload vectors to Qdrant.

        Args:
            subj: List of points to upload
            **kwargs: Additional parameters including connection info

        Returns:
            Status message
        """
        conn = kwargs.get("connection", {})
        if not conn:
            raise ValueError("connection info required in kwargs")

        adapter = cls(conn)
        result = adapter.upsert(points=subj)

        return f"Upserted {len(subj)} points, status: {result.status}"

    def upsert(
        self,
        points: list[dict[str, Any]],
        batch_size: int | None = None,
    ) -> rest_models.UpdateResult:
        """
        Upsert points in batches.

        Args:
            points: List of points to upsert
            batch_size: Optional custom batch size

        Returns:
            UpdateResult with operation status
        """
        try:
            batch_size = batch_size or self.batch_size

            # Validate points
            for point in points:
                if "id" not in point or "vector" not in point:
                    raise ValueError("Each point must have 'id' and 'vector'")

            # Convert to PointStruct objects
            point_structs = [
                rest_models.PointStruct(
                    id=p["id"],
                    vector=p["vector"],
                    payload=p.get("payload", {}),
                )
                for p in points
            ]

            # Upsert in batches
            results = []
            for i in range(0, len(point_structs), batch_size):
                batch = point_structs[i : i + batch_size]
                result = self.client.upsert(
                    collection_name=self.config.collection_name, points=batch
                )
                results.append(result)

            return results[-1]  # Return last batch result

        except Exception as e:
            raise OperationError(f"Upsert failed: {str(e)}")

    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        offset: int = 0,
        filter: dict[str, Any] | None = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        score_threshold: float | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Vector to search for
            limit: Max number of results
            offset: Number of results to skip
            filter: Filter conditions
            with_payload: Include payloads
            with_vectors: Include vectors
            score_threshold: Minimum similarity threshold
            **kwargs: Additional search parameters

        Returns:
            List of search results
        """
        try:
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                query_filter=filter,
                with_payload=with_payload,
                with_vectors=with_vectors,
                score_threshold=score_threshold,
                **kwargs,
            )

            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "payload": r.payload,
                    **({"vector": r.vector} if r.vector is not None else {}),
                }
                for r in results
            ]

        except UnexpectedResponse as e:
            if "not found" in str(e).lower():
                raise ItemNotFoundError("Collection not found")
            raise OperationError(f"Search failed: {str(e)}")
        except Exception as e:
            raise OperationError(f"Search failed: {str(e)}")

    def scroll(
        self,
        limit: int = 100,
        offset: str | int | None = None,
        filter: dict[str, Any] | None = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        **kwargs,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """
        Scroll through collection points.

        Args:
            limit: Points per page
            offset: Offset ID or number
            filter: Filter conditions
            with_payload: Include payloads
            with_vectors: Include vectors
            **kwargs: Additional parameters

        Returns:
            Tuple of (points, next_page_offset)
        """
        try:
            points, next_offset = self.client.scroll(
                collection_name=self.config.collection_name,
                limit=limit,
                offset=offset,
                filter=filter,
                with_payload=with_payload,
                with_vectors=with_vectors,
                **kwargs,
            )

            return (
                [
                    {
                        "id": p.id,
                        "payload": p.payload,
                        **(
                            {"vector": p.vector}
                            if p.vector is not None
                            else {}
                        ),
                    }
                    for p in points
                ],
                next_offset,
            )

        except Exception as e:
            raise OperationError(f"Scroll failed: {str(e)}")

    def delete(
        self, points: list[str] | list[int] | dict[str, Any], **kwargs
    ) -> rest_models.UpdateResult:
        """
        Delete points by IDs or filter.

        Args:
            points: List of point IDs or filter dict
            **kwargs: Additional parameters

        Returns:
            UpdateResult with operation status
        """
        try:
            if isinstance(points, (list, tuple)):
                return self.client.delete(
                    collection_name=self.config.collection_name,
                    points_selector=rest_models.PointIdsList(points=points),
                    **kwargs,
                )
            else:
                return self.client.delete(
                    collection_name=self.config.collection_name,
                    points_selector=rest_models.FilterSelector(filter=points),
                    **kwargs,
                )
        except Exception as e:
            raise OperationError(f"Delete failed: {str(e)}")
