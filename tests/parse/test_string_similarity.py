import pytest

from lionagi.libs.parse.string_similarity import (
    jaro_distance,
    jaro_winkler_similarity,
    string_similarity,
)


def test_jaro_distance_identical():
    assert jaro_distance("hello", "hello") == 1.0


def test_jaro_distance_empty():
    assert jaro_distance("", "") == 1.0
    assert jaro_distance("hello", "") == 0.0
    assert jaro_distance("", "hello") == 0.0


def test_jaro_distance_similar():
    # Similar strings should have a high score
    assert jaro_distance("hello", "helo") > 0.9
    assert jaro_distance("martha", "marhta") > 0.9


def test_jaro_distance_different():
    # Different strings should have a low score
    assert jaro_distance("hello", "world") < 0.5


def test_jaro_distance_transpositions():
    # Test strings with transposed characters
    score = jaro_distance("hello", "ehllo")
    assert 0.7 < score < 0.95


def test_jaro_winkler_similarity_identical():
    assert jaro_winkler_similarity("hello", "hello") == 1.0


def test_jaro_winkler_similarity_empty():
    assert jaro_winkler_similarity("", "") == 1.0
    assert jaro_winkler_similarity("hello", "") == 0.0
    assert jaro_winkler_similarity("", "hello") == 0.0


def test_jaro_winkler_similarity_common_prefix():
    # Strings with common prefix should have higher score than Jaro distance
    jaro_score = jaro_distance("hello", "help")
    winkler_score = jaro_winkler_similarity("hello", "help")
    assert winkler_score > jaro_score


def test_jaro_winkler_similarity_invalid_scaling():
    with pytest.raises(
        ValueError, match="Scaling factor must be between 0 and 0.25"
    ):
        jaro_winkler_similarity("hello", "hello", scaling=0.3)


def test_jaro_winkler_similarity_different_scaling():
    # Test different scaling factors
    score1 = jaro_winkler_similarity("hello", "help", scaling=0.1)
    score2 = jaro_winkler_similarity("hello", "help", scaling=0.2)
    assert (
        score2 > score1
    )  # Higher scaling factor should give higher score for common prefix


def test_string_similarity_exact_match():
    words = ["hello", "world", "python"]
    assert string_similarity("hello", words) == ["hello"]


def test_string_similarity_multiple_matches():
    words = ["hello", "helo", "help"]
    matches = string_similarity("hello", words)
    assert isinstance(matches, list)
    assert "hello" in matches


def test_string_similarity_most_similar():
    words = ["hello", "helo", "help"]
    match = string_similarity("hello", words, return_most_similar=True)
    assert match == "hello"


def test_string_similarity_case_sensitive():
    words = ["Hello", "HELLO", "hello"]
    # Case-sensitive matching
    matches = string_similarity("Hello", words, case_sensitive=True)
    assert matches == ["Hello"]

    # Case-insensitive matching
    matches = string_similarity("Hello", words, case_sensitive=False)
    assert len(matches) == 3


def test_string_similarity_threshold():
    # Test with words that have varying degrees of similarity
    words = ["hello", "helo", "help", "world"]
    # High threshold should return fewer matches
    high_threshold = string_similarity("hello", words, threshold=0.9)
    assert len(high_threshold) <= 2


def test_string_similarity_no_matches():
    words = ["hello", "world", "python"]
    # Test with a completely different string
    assert string_similarity("xyz", words, threshold=0.8) is None


def test_string_similarity_empty_input():
    with pytest.raises(ValueError, match="correct_words must not be empty"):
        string_similarity("hello", [])


def test_string_similarity_invalid_threshold():
    words = ["hello", "world"]
    with pytest.raises(
        ValueError, match="threshold must be between 0.0 and 1.0"
    ):
        string_similarity("hello", words, threshold=1.5)


def test_string_similarity_long_strings():
    words = [
        "pneumonoultramicroscopicsilicovolcanoconiosis",
        "pneumonoultramicroscopicsilicovolcanoconiasis",
        "supercalifragilisticexpialidocious",
    ]
    matches = string_similarity(
        "pneumonoultramicroscopicsilicovolcanoconiosis", words, threshold=0.9
    )
    assert len(matches) >= 1


def test_string_similarity_special_characters():
    words = ["hello!", "hello?", "hello."]
    matches = string_similarity("hello!", words)
    assert "hello!" in matches


def test_string_similarity_numbers():
    words = ["test1", "test2", "test3"]
    matches = string_similarity("test1", words)
    assert "test1" in matches


def test_string_similarity_whitespace():
    words = ["hello world", "hello  world", "helloworld"]
    matches = string_similarity("hello world", words)
    assert "hello world" in matches
