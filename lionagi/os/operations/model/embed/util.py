import heapq
import math
from typing import Any, Callable, List, Optional, Tuple

import numpy as np


def default_similarity_fn(embedding1: List[float], embedding2: List[float]) -> float:
    """Default cosine similarity function."""
    product = np.dot(embedding1, embedding2)
    norm = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    return product / norm


def get_top_k_embeddings(
    query_embedding: List[float],
    embeddings: List[List[float]],
    similarity_fn: Optional[Callable[..., float]] = None,
    similarity_top_k: Optional[int] = None,
    embedding_ids: Optional[List] = None,
    similarity_cutoff: Optional[float] = None,
) -> Tuple[List[float], List]:
    """Get top nodes by similarity to the query."""
    if embedding_ids is None:
        embedding_ids = list(range(len(embeddings)))

    similarity_fn = similarity_fn or default_similarity_fn

    embeddings_np = np.array(embeddings)
    query_embedding_np = np.array(query_embedding)

    similarity_heap: List[Tuple[float, Any]] = []
    for i, emb in enumerate(embeddings_np):
        similarity = similarity_fn(query_embedding_np, emb)
        if similarity_cutoff is None or similarity > similarity_cutoff:
            heapq.heappush(similarity_heap, (similarity, embedding_ids[i]))
            if similarity_top_k and len(similarity_heap) > similarity_top_k:
                heapq.heappop(similarity_heap)
    result_tups = sorted(similarity_heap, key=lambda x: x[0], reverse=True)

    result_similarities = [s for s, _ in result_tups]
    result_ids = [n for _, n in result_tups]

    return result_similarities, result_ids


def get_top_k_mmr_embeddings(
    query_embedding: List[float],
    embeddings: List[List[float]],
    similarity_fn: Optional[Callable[..., float]] = None,
    similarity_top_k: Optional[int] = None,
    embedding_ids: Optional[List] = None,
    similarity_cutoff: Optional[float] = None,
    mmr_threshold: Optional[float] = None,
) -> Tuple[List[float], List]:
    """Get top nodes by similarity to the query, discounted by their similarity to previous results."""
    threshold = mmr_threshold or 0.5
    similarity_fn = similarity_fn or default_similarity_fn

    if embedding_ids is None or embedding_ids == []:
        embedding_ids = list(range(len(embeddings)))
    full_embed_map = dict(zip(embedding_ids, range(len(embedding_ids))))
    embed_map = full_embed_map.copy()
    embed_similarity = {}
    score: float = -math.inf
    high_score_id = None

    for i, emb in enumerate(embeddings):
        similarity = similarity_fn(query_embedding, emb)
        embed_similarity[embedding_ids[i]] = similarity
        if similarity * threshold > score:
            high_score_id = embedding_ids[i]
            score = similarity * threshold

    results: List[Tuple[Any, Any]] = []

    embedding_length = len(embeddings or [])
    similarity_top_k_count = similarity_top_k or embedding_length
    while len(results) < min(similarity_top_k_count, embedding_length):
        results.append((score, high_score_id))

        del embed_map[high_score_id]
        recent_embedding_id = high_score_id
        score = -math.inf

        for embed_id in embed_map:
            overlap_with_recent = similarity_fn(
                embeddings[embed_map[embed_id]],
                embeddings[full_embed_map[recent_embedding_id]],
            )
            if (
                threshold * embed_similarity[embed_id]
                - ((1 - threshold) * overlap_with_recent)
                > score
            ):
                score = threshold * embed_similarity[embed_id] - (
                    (1 - threshold) * overlap_with_recent
                )
                high_score_id = embed_id

    result_similarities = [s for s, _ in results]
    result_ids = [n for _, n in results]

    return result_similarities, result_ids
