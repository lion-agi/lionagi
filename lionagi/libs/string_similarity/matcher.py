"""String matching functionality using similarity algorithms."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .algorithms import SIMILARITY_ALGO_MAP
from .utils import SIMILARITY_TYPE


@dataclass(frozen=True)
class MatchResult:
    """Represents a string matching result."""

    word: str
    score: float
    index: int


def string_similarity(
    word: str,
    correct_words: Sequence[str],
    algorithm: SIMILARITY_TYPE | Callable[[str, str], float] = "jaro_winkler",
    threshold: float = 0.0,
    case_sensitive: bool = False,
    return_most_similar: bool = False,
) -> str | list[str] | None:
    """Find similar strings using specified similarity algorithm.

    Args:
        word: The input string to find matches for
        correct_words: List of strings to compare against
        algorithm: Similarity algorithm to use
        threshold: Minimum similarity score (0.0 to 1.0)
        case_sensitive: Whether to consider case when matching
        return_most_similar: Return only the most similar match

    Returns:
        Matching string(s) or None if no matches found

    Raises:
        ValueError: If correct_words is empty or threshold is invalid
    """
    if not correct_words:
        raise ValueError("correct_words must not be empty")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0")

    # Convert inputs to strings
    compare_word = str(word)
    original_words = [str(w) for w in correct_words]

    # Handle case sensitivity
    if not case_sensitive:
        compare_word = compare_word.lower()
        compare_words = [w.lower() for w in original_words]
    else:
        compare_words = original_words.copy()

    # Get scoring function
    if isinstance(algorithm, str):
        score_func = SIMILARITY_ALGO_MAP.get(algorithm)
        if score_func is None:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    elif callable(algorithm):
        score_func = algorithm
    else:
        raise ValueError(
            "algorithm must be a string specifying a built-in algorithm or "
            "a callable"
        )

    # Calculate similarities
    results = []
    for idx, (orig_word, comp_word) in enumerate(
        zip(original_words, compare_words)
    ):
        # Skip different length strings for hamming similarity
        if algorithm == "hamming" and len(comp_word) != len(compare_word):
            continue

        score = score_func(compare_word, comp_word)
        if score >= threshold:
            results.append(MatchResult(orig_word, score, idx))

    # Return None if no matches
    if not results:
        return None

    # Sort by score (descending) and index (ascending) for stable ordering
    results.sort(key=lambda x: (-x.score, x.index))

    # Return results
    if return_most_similar:
        return results[0].word

    # Filter exact matches for case sensitive comparisons
    if case_sensitive:
        max_score = results[0].score
        results = [r for r in results if r.score == max_score]

    return [r.word for r in results]
