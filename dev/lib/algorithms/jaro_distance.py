def jaro_distance(s: str, t: str) -> float:
    """
    Calculate the Jaro distance between two strings.

    The Jaro distance is a measure of similarity between two strings. The higher
    the Jaro distance for two strings is, the more similar the strings are. The
    value is between 0 and 1, with 1 meaning an exact match and 0 meaning no
    similarity.

    Args:
        s: The first string to compare.
        t: The second string to compare.

    Returns:
        The Jaro distance between the two strings.

    Algorithm:
    1. Calculate lengths of both strings. If both are empty, return 1.0.
    2. Determine the match distance as half the length of the longer string
       minus one.
    3. Initialize match flags for both strings.
    4. Identify matches within the match distance.
    5. Count transpositions.
    6. Compute and return the Jaro distance.
    """
    s_len = len(s)
    t_len = len(t)

    if s_len == 0 and t_len == 0:
        return 1.0

    match_distance = (max(s_len, t_len) // 2) - 1

    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    for i in range(s_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, t_len)

        for j in range(start, end):
            if t_matches[j]:
                continue
            if s[i] != t[j]:
                continue
            s_matches[i] = t_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

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
        matches / s_len + matches / t_len + (matches - transpositions) / matches
    ) / 3.0


def jaro_winkler_similarity(s: str, t: str, scaling: float = 0.1) -> float:
    """
    Calculate the Jaro-Winkler similarity between two strings.

    The Jaro-Winkler similarity is an extension of the Jaro distance, adding a
    prefix scale factor to give more favorable ratings to strings that match
    from the beginning for a set prefix length.

    Args:
        s: The first string to compare.
        t: The second string to compare.
        scaling: The scaling factor for the prefix length. Defaults to 0.1.

    Returns:
        The Jaro-Winkler similarity between the two strings.

    Algorithm:
    1. Calculate the Jaro distance.
    2. Determine the length of the common prefix up to 4 characters.
    3. Adjust the Jaro distance with the prefix scaling factor.
    """
    jaro_sim = jaro_distance(s, t)

    prefix_len = 0
    for s_char, t_char in zip(s, t):
        if s_char == t_char:
            prefix_len += 1
        else:
            break
        if prefix_len == 4:
            break

    return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))



import unittest


class TestStringSimilarity(unittest.TestCase):

    def test_jaro_distance(self):
        self.assertAlmostEqual(jaro_distance("MARTHA", "MARHTA"), 0.9444444444444445)
        self.assertAlmostEqual(jaro_distance("DWAYNE", "DUANE"), 0.8222222222222223)
        self.assertAlmostEqual(jaro_distance("DIXON", "DICKSONX"), 0.7666666666666666)
        self.assertAlmostEqual(jaro_distance("", ""), 1.0)
        self.assertAlmostEqual(jaro_distance("a", ""), 0.0)
        self.assertAlmostEqual(jaro_distance("", "a"), 0.0)
        self.assertAlmostEqual(jaro_distance("abc", "abc"), 1.0)

    def test_jaro_winkler_similarity(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("MARTHA", "MARHTA"), 0.9611111111111111
        )
        self.assertAlmostEqual(jaro_winkler_similarity("DWAYNE", "DUANE"), 0.84)
        self.assertAlmostEqual(
            jaro_winkler_similarity("DIXON", "DICKSONX"), 0.8133333333333332
        )
        self.assertAlmostEqual(jaro_winkler_similarity("", ""), 1.0)
        self.assertAlmostEqual(jaro_winkler_similarity("a", ""), 0.0)
        self.assertAlmostEqual(jaro_winkler_similarity("", "a"), 0.0)
        self.assertAlmostEqual(jaro_winkler_similarity("abc", "abc"), 1.0)

if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
