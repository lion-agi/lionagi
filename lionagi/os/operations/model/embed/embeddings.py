from abc import ABC
from some_package import Component, ModelLimitExceededError
from another_package import calculate_num_token


class EmbeddingUtility(ABC):

    async def call_embedding_service(self, embed_str, **kwargs):
        """
        Asynchronous method to call the embedding service.

        Args:
            embed_str (str): The string to be embedded.
            **kwargs: Additional parameters for the service call.

        Returns:
            dict: Response from the embedding service.
        """
        return await self.service.serve_embedding(embed_str, **kwargs)

    async def embed_node(self, node, field="content", **kwargs) -> bool:
        """
        Embed the specified field of a node.
        """
        if not isinstance(node, Component):
            raise ValueError("Node must be a valid component")
        embed_str = getattr(node, field)

        if isinstance(embed_str, dict) and "images" in embed_str:
            embed_str.pop("images", None)
            embed_str.pop("image_detail", None)

        num_tokens = calculate_num_token(
            {"input": str(embed_str) if isinstance(embed_str, dict) else embed_str},
            "embeddings",
            self.endpoint_schema["token_encoding_name"],
        )

        if self.token_limit and num_tokens > self.token_limit:
            raise ModelLimitExceededError(
                f"Number of tokens {num_tokens} exceeds the limit {self.token_limit}"
            )

        payload, embed = await self.call_embedding_service(embed_str, **kwargs)
        payload.pop("input")
        node.add_field("embedding", embed["data"][0]["embedding"])
        node._meta_insert("embedding_meta", payload)


import heapq
import math
from typing import Any, Callable, List, Optional, Tuple

import numpy as np


def get_top_k_embeddings(
    query_embedding: List[float],
    embeddings: List[List[float]],
    similarity_fn: Optional[Callable[..., float]] = None,
    similarity_top_k: Optional[int] = None,
    embedding_ids: Optional[List] = None,
    similarity_cutoff: Optional[float] = None,
) -> Tuple[List[float], List]:
    """Get top embeddings by similarity to the query."""
    if embedding_ids is None:
        embedding_ids = list(range(len(embeddings)))

    similarity_fn = similarity_fn or np.dot  # default to dot product similarity

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


def get_top_k_embeddings_learner(
    query_embedding: List[float],
    embeddings: List[List[float]],
    similarity_top_k: Optional[int] = None,
    embedding_ids: Optional[List] = None,
    query_mode: str = "SVM",
) -> Tuple[List[float], List]:
    """Get top embeddings by fitting a learner against the query."""
    try:
        from sklearn import linear_model, svm
    except ImportError:
        raise ImportError("Please install scikit-learn to use this feature.")

    if embedding_ids is None:
        embedding_ids = list(range(len(embeddings)))
    query_embedding_np = np.array(query_embedding)
    embeddings_np = np.array(embeddings)
    dataset_len = len(embeddings) + 1
    dataset = np.concatenate([query_embedding_np[None, ...], embeddings_np])
    y = np.zeros(dataset_len)
    y[0] = 1

    if query_mode == "SVM":
        clf = svm.LinearSVC(
            class_weight="balanced", verbose=False, max_iter=10000, tol=1e-6, C=0.1
        )
    elif query_mode == "LINEAR_REGRESSION":
        clf = linear_model.LinearRegression()
    elif query_mode == "LOGISTIC_REGRESSION":
        clf = linear_model.LogisticRegression(class_weight="balanced")
    else:
        raise ValueError(f"Unknown query mode: {query_mode}")

    clf.fit(dataset, y)
    similarities = clf.decision_function(dataset[1:])
    sorted_ix = np.argsort(-similarities)
    top_sorted_ix = sorted_ix[:similarity_top_k]

    result_similarities = similarities[top_sorted_ix]
    result_ids = [embedding_ids[ix] for ix in top_sorted_ix]

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
    """Get top embeddings by similarity to the query, considering diversity."""
    threshold = mmr_threshold or 0.5
    similarity_fn = similarity_fn or np.dot

    if embedding_ids is None:
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

    embedding_length = len(embeddings)
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
