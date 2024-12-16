"""String similarity calculation algorithms."""

from difflib import SequenceMatcher
from itertools import product


def cosine_similarity(s1: str, s2: str) -> float:
    """Calculate the cosine similarity between two strings.

    Args:
        s1: First input string
        s2: Second input string

    Returns:
        float: Cosine similarity score between 0 and 1
    """
    if not s1 or not s2:
        return 0.0

    set1, set2 = set(s1), set(s2)
    intersection = set1.intersection(set2)

    if not set1 or not set2:
        return 0.0

    return len(intersection) / ((len(set1) * len(set2)) ** 0.5)


def hamming_similarity(s1: str, s2: str) -> float:
    """Calculate the Hamming similarity between two strings.

    The strings must be of equal length. Returns the proportion of positions
    at which corresponding symbols are the same.

    Args:
        s1: First input string
        s2: Second input string

    Returns:
        float: Hamming similarity score between 0 and 1
    """
    if not s1 or not s2 or len(s1) != len(s2):
        return 0.0

    matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
    return matches / len(s1)


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
        while not t_matches[k]:
            k += 1
        if s[i] != t[k]:
            transpositions += 1
        k += 1

    transpositions //= 2

    return (
        matches / s_len
        + matches / t_len
        + (matches - transpositions) / matches
    ) / 3.0


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


def levenshtein_distance(a: str, b: str) -> int:
    """Calculate the Levenshtein (edit) distance between two strings.

    Args:
        a: First input string
        b: Second input string

    Returns:
        int: Minimum number of single-character edits needed to change one
             string into the other
    """
    if not a:
        return len(b)
    if not b:
        return len(a)

    m, n = len(a), len(b)
    d = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for i, j in product(range(1, m + 1), range(1, n + 1)):
        cost = 0 if a[i - 1] == b[j - 1] else 1
        d[i][j] = min(
            d[i - 1][j] + 1,  # deletion
            d[i][j - 1] + 1,  # insertion
            d[i - 1][j - 1] + cost,  # substitution
        )

    return d[m][n]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculate the Levenshtein similarity between two strings.

    Converts Levenshtein distance to a similarity score between 0 and 1.

    Args:
        s1: First input string
        s2: Second input string

    Returns:
        float: Levenshtein similarity score between 0 and 1
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return 1 - (distance / max_len)


def sequence_matcher_similarity(s1: str, s2: str) -> float:
    """Calculate similarity using Python's SequenceMatcher.

    Args:
        s1: First input string
        s2: Second input string

    Returns:
        float: Similarity score between 0 and 1
    """
    return SequenceMatcher(None, s1, s2).ratio()


# Map of available similarity algorithms
SIMILARITY_ALGO_MAP = {
    "jaro_winkler": jaro_winkler_similarity,
    "levenshtein": levenshtein_similarity,
    "sequence_matcher": sequence_matcher_similarity,
    "hamming": hamming_similarity,
    "cosine": cosine_similarity,
}
