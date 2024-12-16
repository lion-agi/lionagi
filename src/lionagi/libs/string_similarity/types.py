"""Type definitions for string similarity calculations."""

from collections.abc import Callable
from typing import Literal

SIMILARITY_TYPE = Literal[
    "jaro_winkler",
    "levenshtein",
    "sequence_matcher",
    "hamming",
    "cosine",
]

# Type alias for similarity functions
SimilarityFunc = Callable[[str, str], float]
