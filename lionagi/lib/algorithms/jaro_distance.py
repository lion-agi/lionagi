def jaro_distance(s, t):
    """
    Calculate the Jaro distance between two strings.

    The Jaro distance is a measure of similarity between two strings. The higher
    the Jaro distance for two strings is, the more similar the strings are. The
    value is between 0 and 1, with 1 meaning an exact match and 0 meaning no
    similarity.

    Args:
        s (str): The first string to compare.
        t (str): The second string to compare.

    Returns:
        float: The Jaro distance between the two strings.

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

    # If both strings are empty, they are considered identical
    if s_len == 0 and t_len == 0:
        return 1.0

    # Match distance is the maximum distance within which characters can match
    match_distance = (max(s_len, t_len) // 2) - 1

    # Initialize match flags
    s_matches = [False] * s_len
    t_matches = [False] * t_len

    matches = 0
    transpositions = 0

    # Identify matches
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

    # If no matches, return 0.0
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

    # Compute Jaro distance
    return (
        matches / s_len + matches / t_len + (matches - transpositions) / matches
    ) / 3.0


def jaro_winkler_similarity(s, t, scaling=0.1):
    """
    Calculate the Jaro-Winkler similarity between two strings.

    The Jaro-Winkler similarity is an extension of the Jaro distance, adding a
    prefix scale factor to give more favorable ratings to strings that match
    from the beginning for a set prefix length.

    Args:
        s (str): The first string to compare.
        t (str): The second string to compare.
        scaling (float, optional): The scaling factor for the prefix length.
                                   Defaults to 0.1.

    Returns:
        float: The Jaro-Winkler similarity between the two strings.

    Algorithm:
    1. Calculate the Jaro distance.
    2. Determine the length of the common prefix up to 4 characters.
    3. Adjust the Jaro distance with the prefix scaling factor.

    """
    jaro_sim = jaro_distance(s, t)

    prefix_len = 0

    # Find length of common prefix
    for s_char, t_char in zip(s, t):
        if s_char == t_char:
            prefix_len += 1
        else:
            break
        if prefix_len == 4:
            break

    # Calculate and return Jaro-Winkler similarity
    return jaro_sim + (prefix_len * scaling * (1 - jaro_sim))
