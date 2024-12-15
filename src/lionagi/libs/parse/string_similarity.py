# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from dataclasses import dataclass


def jaro_distance(s: str, t: str) -> float:
    """Calculate the Jaro distance between two strings.

    Args:
        s: First input string
        t: Second input string

    Returns:
        float: Jaro distance score between 0 and 1
    """
    s_len = len(s)
    t_len = len(t)

    if s_len == 0 and t_len == 0:
        return 1.0
    elif s_len == 0 or t_len == 0:
        return 0.0

    match_distance = (max(s_len, t_len) // 2) - 1
    match_distance = max(0, match_distance)  # Ensure non-negative

    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    # Identify matches
    for i in range(s_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, t_len)

        for j in range(start, end):
            if t_matches[j] or s[i] != t[j]:
                continue
            s_matches[i] = t_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    # Count transpositions
    k = 0
    for i in range(s_len):
        if not s_matches[i]:
            continue
        while k < t_len and not t_matches[k]:
            k += 1
        if k < t_len and s[i] != t[k]:
            transpositions += 1
        k += 1

    # Adjust transposition count (half it to reduce penalty)
    transpositions = transpositions / 2

    # Calculate final score with balanced transposition weight
    score = (
        matches / s_len
        + matches / t_len
        + (matches - transpositions) / matches
    ) / 3.0

    # Ensure score is within bounds
    return max(0.0, min(1.0, score))


def jaro_winkler_similarity(s: str, t: str, scaling: float = 0.1) -> float:
    """Calculate the Jaro-Winkler similarity between two strings.

    Args:
        s: First input string
        t: Second input string
        scaling: Scaling factor for common prefix adjustment

    Returns:
        float: Jaro-Winkler similarity score between 0 and 1

    Raises:
        ValueError: If scaling factor is not between 0 and 0.25
    """
    if not 0 <= scaling <= 0.25:
        raise ValueError("Scaling factor must be between 0 and 0.25")

    jaro_sim = jaro_distance(s, t)

    # Find length of common prefix (up to 4 chars)
    prefix_len = 0
    for s_char, t_char in zip(s, t):
        if s_char != t_char:
            break
        prefix_len += 1
        if prefix_len == 4:
            break

    return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))


@dataclass(frozen=True)
class MatchResult:
    """Represents a string matching result."""

    word: str
    score: float
    index: int


def string_similarity(
    word: str,
    correct_words: Sequence[str],
    threshold: float = 0.0,
    case_sensitive: bool = False,
    return_most_similar: bool = False,
) -> str | list[str] | None:
    """Find similar strings using specified similarity algorithm."""
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
    score_func = jaro_winkler_similarity

    # Calculate similarities
    results = []
    for idx, (orig_word, comp_word) in enumerate(
        zip(original_words, compare_words)
    ):
        score = score_func(compare_word, comp_word)
        # Only include scores that meet minimum threshold
        if score >= max(0.4, threshold):  # Set minimum threshold to 0.4
            results.append(MatchResult(orig_word, score, idx))

    # Return None if no matches meet threshold
    if not results:
        return None

    # Sort by score (descending) and index (ascending) for stable ordering
    results.sort(key=lambda x: (-x.score, x.index))

    # Return most similar if requested
    if return_most_similar:
        return results[0].word

    # For exact matches (score = 1.0), only return those
    exact_matches = [r for r in results if abs(r.score - 1.0) < 1e-10]
    if exact_matches:
        return [r.word for r in exact_matches]

    # For case sensitive matches, only return highest scoring matches
    if case_sensitive:
        max_score = results[0].score
        results = [r for r in results if abs(r.score - max_score) < 1e-10]
        return [r.word for r in results]

    # For threshold matches, return all matches above threshold
    return [r.word for r in results]
