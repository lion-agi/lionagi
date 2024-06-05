import asyncio
from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Coroutine, List, Optional

import numpy as np


class SimilarityMode(str, Enum):
    """Modes for similarity/distance."""

    DEFAULT = "cosine"
    DOT_PRODUCT = "dot_product"
    EUCLIDEAN = "euclidean"


def mean_agg(embeddings: List[List[float]]) -> List[float]:
    """Mean aggregation for embeddings."""
    return np.array(embeddings).mean(axis=0).tolist()


def similarity(
    embedding1: List[float],
    embedding2: List[float],
    mode: SimilarityMode = SimilarityMode.DEFAULT,
) -> float:
    """Get embedding similarity."""
    if mode == SimilarityMode.EUCLIDEAN:
        return -float(np.linalg.norm(np.array(embedding1) - np.array(embedding2)))
    elif mode == SimilarityMode.DOT_PRODUCT:
        return np.dot(embedding1, embedding2)
    else:
        product = np.dot(embedding1, embedding2)
        norm = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        return product / norm


class BaseEmbedding:
    """Base class for embeddings."""

    def __init__(
        self,
        model_name: str = "unknown",
        embed_batch_size: int = 32,
        num_workers: Optional[int] = None,
    ):
        self.model_name = model_name
        self.embed_batch_size = embed_batch_size
        self.num_workers = num_workers

    @abstractmethod
    def _get_query_embedding(self, query: str) -> List[float]:
        """Embed the input query synchronously."""

    @abstractmethod
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Embed the input query asynchronously."""

    def get_query_embedding(self, query: str) -> List[float]:
        """Embed the input query."""
        return self._get_query_embedding(query)

    async def aget_query_embedding(self, query: str) -> List[float]:
        """Async get query embedding."""
        return await self._aget_query_embedding(query)

    def get_agg_embedding_from_queries(
        self, queries: List[str], agg_fn: Optional[Callable[..., List[float]]] = None
    ) -> List[float]:
        """Get aggregated embedding from multiple queries."""
        query_embeddings = [self.get_query_embedding(query) for query in queries]
        agg_fn = agg_fn or mean_agg
        return agg_fn(query_embeddings)

    async def aget_agg_embedding_from_queries(
        self, queries: List[str], agg_fn: Optional[Callable[..., List[float]]] = None
    ) -> List[float]:
        """Async get aggregated embedding from multiple queries."""
        query_embeddings = [await self.aget_query_embedding(query) for query in queries]
        agg_fn = agg_fn or mean_agg
        return agg_fn(query_embeddings)

    @abstractmethod
    def _get_text_embedding(self, text: str) -> List[float]:
        """Embed the input text synchronously."""

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Embed the input text asynchronously."""
        return self._get_text_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Embed the input sequence of text synchronously."""
        return [self._get_text_embedding(text) for text in texts]

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Embed the input sequence of text asynchronously."""
        return await asyncio.gather(
            *[self._aget_text_embedding(text) for text in texts]
        )

    def get_text_embedding(self, text: str) -> List[float]:
        """Embed the input text."""
        return self._get_text_embedding(text)

    async def aget_text_embedding(self, text: str) -> List[float]:
        """Async get text embedding."""
        return await self._aget_text_embedding(text)

    def get_text_embedding_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        """Get a list of text embeddings, with batching."""
        cur_batch: List[str] = []
        result_embeddings: List[List[float]] = []

        for idx, text in enumerate(texts):
            cur_batch.append(text)
            if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
                embeddings = self._get_text_embeddings(cur_batch)
                result_embeddings.extend(embeddings)
                cur_batch = []

        return result_embeddings

    async def aget_text_embedding_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        """Asynchronously get a list of text embeddings, with batching."""
        cur_batch: List[str] = []
        result_embeddings: List[List[float]] = []
        embeddings_coroutines: List[Coroutine] = []

        for idx, text in enumerate(texts):
            cur_batch.append(text)
            if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
                embeddings_coroutines.append(self._aget_text_embeddings(cur_batch))
                cur_batch = []

        nested_embeddings = await asyncio.gather(*embeddings_coroutines)
        result_embeddings = [
            embedding for embeddings in nested_embeddings for embedding in embeddings
        ]

        return result_embeddings

    def __call__(self, nodes: List[Any], **kwargs: Any) -> List[Any]:
        embeddings = self.get_text_embedding_batch(
            [node.get_content(metadata_mode="embed") for node in nodes],
            **kwargs,
        )

        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding

        return nodes

    async def acall(self, nodes: List[Any], **kwargs: Any) -> List[Any]:
        embeddings = await self.aget_text_embedding_batch(
            [node.get_content(metadata_mode="embed") for node in nodes],
            **kwargs,
        )

        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding

        return nodes
