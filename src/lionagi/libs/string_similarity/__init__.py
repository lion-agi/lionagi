"""String similarity calculation and matching functionality."""

from .algorithms import (
    SIMILARITY_ALGO_MAP,
    cosine_similarity,
    hamming_similarity,
    jaro_distance,
    jaro_winkler_similarity,
    levenshtein_distance,
    levenshtein_similarity,
    sequence_matcher_similarity,
)
from .matcher import MatchResult, string_similarity
from .types import SIMILARITY_TYPE, SimilarityFunc

__all__ = [
    # Main functionality
    "string_similarity",
    "MatchResult",
    # Algorithms
    "cosine_similarity",
    "hamming_similarity",
    "jaro_distance",
    "jaro_winkler_similarity",
    "levenshtein_distance",
    "levenshtein_similarity",
    "sequence_matcher_similarity",
    # Types and constants
    "SIMILARITY_TYPE",
    "SimilarityFunc",
    "SIMILARITY_ALGO_MAP",
]
