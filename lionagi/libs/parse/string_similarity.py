# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence


def jaro_distance(s: str, t: str) -> float:
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
        if s_matches[i]:
            while not t_matches[k]:
                k += 1
            if s[i] != t[k]:
                transpositions += 1
            k += 1

    transpositions //= 2

    return (
        (matches / s_len)
        + (matches / t_len)
        + ((matches - transpositions) / matches)
    ) / 3.0


def jaro_winkler_similarity(s: str, t: str, scaling: float = 0.1) -> float:
    if not 0 <= scaling <= 0.25:
        raise ValueError("Scaling factor must be between 0 and 0.25")

    jaro_sim = jaro_distance(s, t)

    # Find common prefix length (up to 4 chars)
    prefix_len = 0
    for s_char, t_char in zip(s, t):
        if s_char != t_char:
            break
        prefix_len += 1
        if prefix_len == 4:
            break

    return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))


def string_similarity(
    word: str,
    correct_words: Sequence[str],
    threshold: float = 0.85,
    case_sensitive: bool = False,
    return_most_similar: bool = False,
) -> str | list[str] | None:
    """
    Find similar strings to `word` from `correct_words` using Jaro-Winkler similarity.

    Args:
        word: The input string to find matches for
        correct_words: List of strings to compare against
        threshold: Minimum similarity score (0.0 to 1.0)
        case_sensitive: Whether to consider case when matching
        return_most_similar: Return only the most similar match

    Returns:
        Matching string(s) or None if no matches found
    """
    if not correct_words:
        raise ValueError("correct_words must not be empty")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0")

    compare_word = word if case_sensitive else word.lower()
    compare_words = [w if case_sensitive else w.lower() for w in correct_words]

    # Calculate similarities
    results = []
    for idx, (orig_word, comp_word) in enumerate(
        zip(correct_words, compare_words)
    ):
        score = jaro_winkler_similarity(compare_word, comp_word)
        if score >= threshold:
            results.append((orig_word, score, idx))

    if not results:
        return None

    # Sort by score descending, index ascending
    results.sort(key=lambda x: (-x[1], x[2]))

    if return_most_similar:
        return results[0][0]

    # If multiple have the same top score, return all that share it
    max_score = results[0][1]
    top_matches = [r[0] for r in results if r[1] == max_score]
    return top_matches
